"""Reminder processor service for checking and publishing due reminders."""

import logging
from datetime import datetime, timezone
from typing import List, Set

from dapr.clients import DaprClient
from sqlmodel import Session, select

from ..models import Reminder, ReminderDueEvent
from ..config import settings

logger = logging.getLogger(__name__)


class ReminderProcessor:
    """Service for processing due reminders and publishing reminder.due events.

    Features:
    - Queries database for reminders with reminder_at <= now and sent = false
    - Publishes reminder.due events via Dapr Pub/Sub
    - Marks reminders as sent to prevent duplicates
    - Idempotency protection using in-memory cache

    Attributes:
        pubsub_name: Name of Dapr Pub/Sub component
        batch_size: Maximum number of reminders to process per batch
        _processed_reminder_ids: In-memory cache of recently processed reminder IDs
    """

    def __init__(
        self,
        pubsub_name: str = settings.pubsub_name,
        batch_size: int = settings.reminder_batch_size
    ):
        """Initialize ReminderProcessor.

        Args:
            pubsub_name: Name of Dapr Pub/Sub component
            batch_size: Maximum reminders to process per batch
        """
        self.pubsub_name = pubsub_name
        self.batch_size = batch_size

        # Idempotency cache: Track recently processed reminder IDs
        # Prevents duplicate reminder sends if cron runs before DB commit finishes
        self._processed_reminder_ids: Set[int] = set()
        self._max_cache_size = 1000

    async def process_due_reminders(self, session: Session) -> int:
        """Process all due reminders and publish reminder.due events.

        Args:
            session: Database session

        Returns:
            Number of reminders processed

        Raises:
            Exception: If reminder processing fails
        """
        now = datetime.now(timezone.utc)

        logger.info(f"Processing due reminders (batch_size={self.batch_size}, now={now.isoformat()})")

        # Query database for due reminders
        due_reminders = self._get_due_reminders(session, now)

        if not due_reminders:
            logger.info("No due reminders found")
            return 0

        logger.info(f"Found {len(due_reminders)} due reminders to process")

        # Process each reminder
        processed_count = 0
        for reminder in due_reminders:
            try:
                # Idempotency check
                if self._is_already_processed(reminder.id):
                    logger.warning(
                        f"Reminder {reminder.id} already processed (idempotency cache hit)"
                    )
                    continue

                # Publish reminder.due event
                await self._publish_reminder_event(reminder)

                # Mark as sent in database
                self._mark_as_sent(session, reminder)

                # Add to idempotency cache
                self._mark_as_processed(reminder.id)

                processed_count += 1

                logger.info(
                    f"Processed reminder: id={reminder.id}, task_id={reminder.task_id}, "
                    f"user_id={reminder.user_id}, reminder_at={reminder.reminder_at.isoformat()}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to process reminder {reminder.id}: {str(e)}",
                    exc_info=True
                )
                # Continue processing other reminders even if one fails

        # Commit all changes
        session.commit()

        logger.info(f"Successfully processed {processed_count}/{len(due_reminders)} reminders")

        return processed_count

    def _get_due_reminders(self, session: Session, now: datetime) -> List[Reminder]:
        """Query database for due reminders.

        Args:
            session: Database session
            now: Current timestamp

        Returns:
            List of due reminders (not sent, reminder_at <= now)
        """
        statement = (
            select(Reminder)
            .where(Reminder.sent == False)  # noqa: E712
            .where(Reminder.reminder_at <= now)
            .limit(self.batch_size)
        )

        reminders = session.exec(statement).all()
        return list(reminders)

    async def _publish_reminder_event(self, reminder: Reminder) -> None:
        """Publish reminder.due event via Dapr Pub/Sub.

        Args:
            reminder: Reminder record to publish event for

        Raises:
            Exception: If event publishing fails
        """
        # Create reminder.due event
        event = ReminderDueEvent.create(
            user_id=reminder.user_id,
            task_id=reminder.task_id,
            reminder_at=reminder.reminder_at.isoformat()
        )

        # Publish via Dapr Pub/Sub
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name="reminders.due",
                data=event.model_dump(mode="json"),
                data_content_type="application/json"
            )

        logger.info(
            f"Published reminder.due event: event_id={event.event_id}, "
            f"task_id={reminder.task_id}, user_id={reminder.user_id}"
        )

    def _mark_as_sent(self, session: Session, reminder: Reminder) -> None:
        """Mark reminder as sent in database.

        Args:
            session: Database session
            reminder: Reminder to mark as sent
        """
        reminder.sent = True
        session.add(reminder)
        # Note: Commit happens in process_due_reminders() after all reminders processed

    def _is_already_processed(self, reminder_id: int) -> bool:
        """Check if reminder was recently processed (idempotency check).

        Args:
            reminder_id: Reminder ID to check

        Returns:
            True if already processed, False otherwise
        """
        return reminder_id in self._processed_reminder_ids

    def _mark_as_processed(self, reminder_id: int) -> None:
        """Mark reminder as processed in idempotency cache.

        Args:
            reminder_id: Reminder ID to mark as processed
        """
        # Evict oldest entries if cache is full
        if len(self._processed_reminder_ids) >= self._max_cache_size:
            # Remove half the cache (FIFO-like eviction)
            to_remove = list(self._processed_reminder_ids)[: self._max_cache_size // 2]
            for rid in to_remove:
                self._processed_reminder_ids.discard(rid)

        self._processed_reminder_ids.add(reminder_id)


# Singleton instance
_reminder_processor: ReminderProcessor | None = None


def get_reminder_processor() -> ReminderProcessor:
    """Get singleton ReminderProcessor instance.

    Returns:
        ReminderProcessor instance
    """
    global _reminder_processor
    if _reminder_processor is None:
        _reminder_processor = ReminderProcessor()
    return _reminder_processor
