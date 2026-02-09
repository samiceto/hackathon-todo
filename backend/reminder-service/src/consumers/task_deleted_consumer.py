"""Consumer for task.deleted events."""

import logging
from typing import Dict, Any, Set, List

from sqlmodel import Session, select

from ..models import Reminder

logger = logging.getLogger(__name__)


class TaskDeletedConsumer:
    """Consumer for processing task.deleted events.

    When a task is deleted:
    1. Find all associated Reminder records
    2. Delete all reminders for the task
    3. Return success status

    Rationale: If a task is deleted, we should clean up all associated reminders.

    Features:
    - Idempotency protection using event_id cache
    - Error handling with detailed logging
    - Handles case where no reminders exist (not an error)
    - Deletes all reminders (in case there are multiple)
    """

    def __init__(self):
        """Initialize TaskDeletedConsumer."""
        # Idempotency cache: Track processed event_ids
        self._processed_event_ids: Set[str] = set()
        self._max_cache_size = 10000

    async def handle_event(self, event: Dict[str, Any], session: Session) -> Dict[str, str]:
        """Handle task.deleted event.

        Args:
            event: Task deleted event payload from Dapr
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
                f"Processing task.deleted event: event_id={event_id}, task_id={task_id}"
            )

            # Validate required fields
            if not task_id:
                logger.error(f"Missing required field: task_id={task_id}")
                raise ValueError("task_id is required")

            # Find all existing reminders for this task
            reminders = self._get_existing_reminders(session, task_id)

            if not reminders:
                logger.info(f"No reminders found for task {task_id} - nothing to delete")
                self._mark_as_processed(event_id)
                return {"status": "no_reminders", "task_id": task_id}

            # Delete all reminders
            deleted_count = 0
            for reminder in reminders:
                logger.info(f"Deleting reminder {reminder.id} for deleted task {task_id}")
                session.delete(reminder)
                deleted_count += 1

            session.commit()

            logger.info(f"Deleted {deleted_count} reminder(s) for task {task_id}")

            self._mark_as_processed(event_id)
            return {
                "status": "deleted",
                "task_id": task_id,
                "reminders_deleted": deleted_count
            }

        except Exception as e:
            logger.error(f"Failed to process task.deleted event: {str(e)}", exc_info=True)
            # Rollback transaction on error
            session.rollback()
            raise

    def _get_existing_reminders(self, session: Session, task_id: int) -> List[Reminder]:
        """Get all existing reminders for a task.

        Args:
            session: Database session
            task_id: Task ID

        Returns:
            List of Reminder records (may be empty)
        """
        statement = select(Reminder).where(Reminder.task_id == task_id)
        reminders = session.exec(statement).all()
        return list(reminders)

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
_task_deleted_consumer: TaskDeletedConsumer | None = None


def get_task_deleted_consumer() -> TaskDeletedConsumer:
    """Get singleton TaskDeletedConsumer instance.

    Returns:
        TaskDeletedConsumer instance
    """
    global _task_deleted_consumer
    if _task_deleted_consumer is None:
        _task_deleted_consumer = TaskDeletedConsumer()
    return _task_deleted_consumer
