"""Event publisher service for publishing events to Kafka via Dapr Pub/Sub."""

import logging
import time
from typing import Any, Dict, Set
from collections import deque
import threading

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

from ..models.event import Event, EventType

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing domain events to Kafka via Dapr Pub/Sub.

    Uses Dapr Pub/Sub API to abstract Kafka complexity and enable portability.
    Events are published to topics based on event_type (e.g., task.created -> tasks.created).

    Features:
    - Idempotency: Tracks published event_ids to prevent duplicates (in-memory cache)
    - Delivery guarantees: Retry with exponential backoff on failures
    - Local queueing: Failed events stored in queue for later retry
    - Dead letter queue: Events that fail after max retries are logged

    Attributes:
        pubsub_name: Name of the Dapr Pub/Sub component (default: pubsub-kafka)
        max_retries: Maximum retry attempts for failed publishes (default: 3)
        initial_backoff_ms: Initial backoff delay in milliseconds (default: 1000)
        max_cache_size: Maximum size of idempotency cache (default: 10000)
        dapr_client: Dapr client for pub/sub operations (optional, created if not provided)
    """

    def __init__(
        self,
        pubsub_name: str = "pubsub-kafka",
        dapr_client: DaprClient | None = None,
        max_retries: int = 3,
        initial_backoff_ms: int = 1000,
        max_cache_size: int = 10000
    ):
        """Initialize EventPublisher.

        Args:
            pubsub_name: Name of the Dapr Pub/Sub component
            dapr_client: Optional Dapr client instance (for testing/dependency injection)
            max_retries: Maximum retry attempts for failed publishes
            initial_backoff_ms: Initial backoff delay in milliseconds
            max_cache_size: Maximum size of idempotency cache
        """
        self.pubsub_name = pubsub_name
        self._dapr_client = dapr_client
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.max_cache_size = max_cache_size

        # Idempotency: Track published event IDs to prevent duplicates
        # Using a set with size limit (FIFO eviction when full)
        self._published_event_ids: deque = deque(maxlen=max_cache_size)
        self._published_event_ids_set: Set[str] = set()
        self._idempotency_lock = threading.Lock()

        # Local queue: Store failed events for retry
        self._failed_events_queue: deque = deque(maxlen=1000)
        self._queue_lock = threading.Lock()

    def publish(self, event: Event, retry_count: int = 0) -> bool:
        """Publish an event to Kafka via Dapr Pub/Sub with idempotency and retries.

        Features:
        - Idempotency: Skips duplicate event_ids
        - Retry logic: Exponential backoff on failures
        - Dead letter queue: Logs events that fail after max retries

        Args:
            event: Event to publish
            retry_count: Current retry attempt (internal use)

        Returns:
            True if published successfully, False if failed after all retries

        Raises:
            DaprInternalError: If publishing fails after all retries (optional)
        """
        # Idempotency check: Skip if already published
        if self._is_duplicate(event.event_id):
            logger.warning(
                f"Duplicate event detected (already published): event_id={event.event_id}, "
                f"event_type={event.event_type}. Skipping."
            )
            return True  # Return success since event was already published

        # Determine topic from event_type
        topic = self._get_topic_name(event.event_type)

        # Convert event to dict for JSON serialization
        event_data = event.model_dump(mode="json")

        try:
            # Publish via Dapr Pub/Sub API
            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=event_data,
                    data_content_type="application/json"
                )

            # Mark event as published (for idempotency)
            self._mark_as_published(event.event_id)

            logger.info(
                f"Published event: event_id={event.event_id}, "
                f"event_type={event.event_type}, topic={topic}, "
                f"user_id={event.user_id}, retry_count={retry_count}"
            )

            return True

        except DaprInternalError as e:
            logger.error(
                f"Failed to publish event: event_id={event.event_id}, "
                f"event_type={event.event_type}, error={str(e)}, retry_count={retry_count}"
            )

            # Retry with exponential backoff if retries remaining
            if retry_count < self.max_retries:
                # Calculate backoff delay (exponential: 1s, 2s, 4s)
                backoff_ms = self.initial_backoff_ms * (2 ** retry_count)
                backoff_seconds = backoff_ms / 1000.0

                logger.info(
                    f"Retrying event publish in {backoff_seconds}s: event_id={event.event_id}, "
                    f"retry={retry_count + 1}/{self.max_retries}"
                )

                # Sleep for backoff period
                time.sleep(backoff_seconds)

                # Recursive retry
                return self.publish(event, retry_count=retry_count + 1)

            else:
                # Max retries exceeded - add to dead letter queue
                logger.error(
                    f"Event publish failed after {self.max_retries} retries. "
                    f"Moving to dead letter queue: event_id={event.event_id}, "
                    f"event_type={event.event_type}"
                )

                self._add_to_dlq(event, str(e))
                return False

    def _get_topic_name(self, event_type: EventType) -> str:
        """Get Kafka topic name from event type.

        Maps event types to Kafka topics:
        - task.created -> tasks.created
        - task.updated -> tasks.updated
        - task.completed -> tasks.completed
        - task.deleted -> tasks.deleted
        - reminder.due -> reminders.due

        Args:
            event_type: Event type

        Returns:
            Kafka topic name
        """
        topic_map = {
            "task.created": "tasks.created",
            "task.updated": "tasks.updated",
            "task.completed": "tasks.completed",
            "task.deleted": "tasks.deleted",
            "reminder.due": "reminders.due"
        }
        return topic_map.get(event_type, event_type)

    def _is_duplicate(self, event_id: str) -> bool:
        """Check if event_id has already been published (idempotency check).

        Args:
            event_id: Event ID to check

        Returns:
            True if event was already published, False otherwise
        """
        with self._idempotency_lock:
            return event_id in self._published_event_ids_set

    def _mark_as_published(self, event_id: str) -> None:
        """Mark event_id as published (for idempotency).

        Uses a deque with max size for FIFO eviction when cache is full.

        Args:
            event_id: Event ID to mark as published
        """
        with self._idempotency_lock:
            # Add to set
            self._published_event_ids_set.add(event_id)

            # Add to deque (FIFO eviction when maxlen reached)
            if len(self._published_event_ids) == self.max_cache_size:
                # Remove oldest event_id from set when deque evicts it
                oldest_event_id = self._published_event_ids[0]
                self._published_event_ids_set.discard(oldest_event_id)

            self._published_event_ids.append(event_id)

    def _add_to_dlq(self, event: Event, error_message: str) -> None:
        """Add failed event to dead letter queue for manual review.

        Events in the DLQ can be:
        - Logged for debugging
        - Stored in a database for later replay
        - Sent to a monitoring/alerting system

        Args:
            event: Event that failed to publish
            error_message: Error message from the failure
        """
        with self._queue_lock:
            dlq_entry = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "event_data": event.model_dump(mode="json"),
                "error_message": error_message,
                "retry_count": self.max_retries,
                "failed_at": time.time()
            }

            self._failed_events_queue.append(dlq_entry)

            logger.error(
                f"Dead Letter Queue: Added event {event.event_id} "
                f"(queue size: {len(self._failed_events_queue)}). "
                f"Error: {error_message}"
            )

    def get_dlq_size(self) -> int:
        """Get number of events in dead letter queue.

        Returns:
            Number of failed events in DLQ
        """
        with self._queue_lock:
            return len(self._failed_events_queue)

    def get_dlq_events(self) -> list:
        """Get all events in dead letter queue (for debugging/monitoring).

        Returns:
            List of DLQ entries with event data and error info
        """
        with self._queue_lock:
            return list(self._failed_events_queue)

    def clear_dlq(self) -> int:
        """Clear all events from dead letter queue.

        Returns:
            Number of events cleared
        """
        with self._queue_lock:
            count = len(self._failed_events_queue)
            self._failed_events_queue.clear()
            logger.info(f"Cleared {count} events from dead letter queue")
            return count

    async def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously (future enhancement).

        Note: Current implementation is synchronous. Async version requires
        async Dapr client and FastAPI background tasks.

        Args:
            event: Event to publish
        """
        # For now, call synchronous version
        # TODO: Implement async publishing with background tasks
        self.publish(event)


# Singleton instance for dependency injection
_event_publisher: EventPublisher | None = None


def get_event_publisher() -> EventPublisher:
    """Get singleton EventPublisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
