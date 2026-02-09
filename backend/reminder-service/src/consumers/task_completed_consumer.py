"""Consumer for task.completed events."""

import logging
from typing import Dict, Any, Set, Optional

from sqlmodel import Session, select

from ..models import Reminder

logger = logging.getLogger(__name__)


class TaskCompletedConsumer:
    """Consumer for processing task.completed events.

    When a task is marked as completed:
    1. Find associated Reminder record
    2. Mark reminder as sent = True to prevent duplicate sends
    3. Return success status

    Rationale: If a task is completed, we don't want to send a reminder for it.
    Marking sent=True prevents the ReminderProcessor from sending it.

    Features:
    - Idempotency protection using event_id cache
    - Error handling with detailed logging
    - Handles case where no reminder exists (not an error)
    """

    def __init__(self):
        """Initialize TaskCompletedConsumer."""
        # Idempotency cache: Track processed event_ids
        self._processed_event_ids: Set[str] = set()
        self._max_cache_size = 10000

    async def handle_event(self, event: Dict[str, Any], session: Session) -> Dict[str, str]:
        """Handle task.completed event.

        Args:
            event: Task completed event payload from Dapr
            session: Database session

        Returns:
            Processing status

        Raises:
            ValueError: If event format is invalid
        """
        try:
            # Extract event metadata
            event_data = event.get("data", {})
            event_id = event_data.get("event_id")
            payload = event_data.get("payload", {})

            # Idempotency check
            if self._is_duplicate(event_id):
                logger.warning(f"Duplicate event detected: event_id={event_id}")
                return {"status": "duplicate", "event_id": event_id}

            # Extract task data
            task_id = payload.get("task_id")

            logger.info(
                f"Processing task.completed event: event_id={event_id}, task_id={task_id}"
            )

            # Validate required fields
            if not task_id:
                logger.error(f"Missing required field: task_id={task_id}")
                raise ValueError("task_id is required")

            # Find existing reminder
            reminder = self._get_existing_reminder(session, task_id)

            if not reminder:
                logger.info(f"No reminder found for task {task_id} - nothing to cancel")
                self._mark_as_processed(event_id)
                return {"status": "no_reminder"}

            # Mark reminder as sent to prevent duplicate sends
            if not reminder.sent:
                logger.info(
                    f"Marking reminder {reminder.id} as sent (task completed before reminder due)"
                )
                reminder.sent = True
                session.add(reminder)
                session.commit()
                session.refresh(reminder)

                self._mark_as_processed(event_id)
                return {
                    "status": "cancelled",
                    "reminder_id": reminder.id,
                    "task_id": task_id
                }
            else:
                logger.info(f"Reminder {reminder.id} already marked as sent")
                self._mark_as_processed(event_id)
                return {"status": "already_sent", "reminder_id": reminder.id}

        except Exception as e:
            logger.error(f"Failed to process task.completed event: {str(e)}", exc_info=True)
            # Rollback transaction on error
            session.rollback()
            raise

    def _get_existing_reminder(self, session: Session, task_id: int) -> Optional[Reminder]:
        """Get existing reminder for a task.

        Args:
            session: Database session
            task_id: Task ID

        Returns:
            Existing Reminder or None
        """
        statement = select(Reminder).where(Reminder.task_id == task_id)
        reminder = session.exec(statement).first()
        return reminder

    def _is_duplicate(self, event_id: str) -> bool:
        """Check if event was already processed (idempotency check).

        Args:
            event_id: Event ID to check

        Returns:
            True if already processed, False otherwise
        """
        return event_id in self._processed_event_ids

    def _mark_as_processed(self, event_id: str) -> None:
        """Mark event as processed in idempotency cache.

        Args:
            event_id: Event ID to mark as processed
        """
        # Evict oldest entries if cache is full
        if len(self._processed_event_ids) >= self._max_cache_size:
            # Remove half the cache (FIFO-like eviction)
            to_remove = list(self._processed_event_ids)[: self._max_cache_size // 2]
            for eid in to_remove:
                self._processed_event_ids.discard(eid)

        self._processed_event_ids.add(event_id)


# Singleton instance
_task_completed_consumer: TaskCompletedConsumer | None = None


def get_task_completed_consumer() -> TaskCompletedConsumer:
    """Get singleton TaskCompletedConsumer instance.

    Returns:
        TaskCompletedConsumer instance
    """
    global _task_completed_consumer
    if _task_completed_consumer is None:
        _task_completed_consumer = TaskCompletedConsumer()
    return _task_completed_consumer
