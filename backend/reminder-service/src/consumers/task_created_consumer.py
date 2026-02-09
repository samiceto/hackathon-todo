"""Consumer for task.created events."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Set

from sqlmodel import Session

from ..models import Reminder

logger = logging.getLogger(__name__)


class TaskCreatedConsumer:
    """Consumer for processing task.created events.

    When a task is created with a due_date and reminder_offset:
    1. Calculate reminder_at = due_date - reminder_offset
    2. Create Reminder record in database
    3. Return success status

    Features:
    - Idempotency protection using event_id cache
    - Error handling with detailed logging
    - Validates required fields before creating reminder
    """

    def __init__(self):
        """Initialize TaskCreatedConsumer."""
        # Idempotency cache: Track processed event_ids
        self._processed_event_ids: Set[str] = set()
        self._max_cache_size = 10000

    async def handle_event(self, event: Dict[str, Any], session: Session) -> Dict[str, str]:
        """Handle task.created event.

        Args:
            event: Task created event payload from Dapr
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
            user_id = event_data.get("user_id")
            due_date_str = payload.get("due_date")
            reminder_offset_minutes = payload.get("reminder_offset")

            logger.info(
                f"Processing task.created event: event_id={event_id}, "
                f"task_id={task_id}, user_id={user_id}, due_date={due_date_str}, "
                f"reminder_offset={reminder_offset_minutes}"
            )

            # Validate required fields
            if not task_id or not user_id:
                logger.error(f"Missing required fields: task_id={task_id}, user_id={user_id}")
                raise ValueError("task_id and user_id are required")

            # Only create reminder if task has due_date AND reminder_offset
            if not due_date_str or reminder_offset_minutes is None:
                logger.info(
                    f"Task {task_id} has no due_date or reminder_offset - skipping reminder creation"
                )
                self._mark_as_processed(event_id)
                return {"status": "skipped", "reason": "no_due_date_or_reminder"}

            # Parse due_date
            due_date = self._parse_datetime(due_date_str)

            # Calculate reminder_at = due_date - reminder_offset
            reminder_at = due_date - timedelta(minutes=reminder_offset_minutes)

            # Don't create reminder if reminder_at is in the past
            now = datetime.now(timezone.utc)
            if reminder_at <= now:
                logger.info(
                    f"Reminder time is in the past (reminder_at={reminder_at.isoformat()}) - skipping"
                )
                self._mark_as_processed(event_id)
                return {"status": "skipped", "reason": "reminder_in_past"}

            # Create Reminder record
            reminder = Reminder(
                task_id=task_id,
                user_id=user_id,
                reminder_at=reminder_at,
                sent=False
            )

            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(
                f"Created reminder: id={reminder.id}, task_id={task_id}, "
                f"reminder_at={reminder_at.isoformat()}"
            )

            # Mark as processed
            self._mark_as_processed(event_id)

            return {
                "status": "success",
                "reminder_id": reminder.id,
                "task_id": task_id,
                "reminder_at": reminder_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to process task.created event: {str(e)}", exc_info=True)
            # Rollback transaction on error
            session.rollback()
            raise

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse ISO 8601 datetime string.

        Args:
            dt_str: ISO 8601 datetime string

        Returns:
            datetime object in UTC timezone

        Raises:
            ValueError: If datetime format is invalid
        """
        try:
            # Parse ISO 8601 string
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

            # Ensure UTC timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt

        except Exception as e:
            logger.error(f"Failed to parse datetime: {dt_str}, error: {str(e)}")
            raise ValueError(f"Invalid datetime format: {dt_str}")

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
_task_created_consumer: TaskCreatedConsumer | None = None


def get_task_created_consumer() -> TaskCreatedConsumer:
    """Get singleton TaskCreatedConsumer instance.

    Returns:
        TaskCreatedConsumer instance
    """
    global _task_created_consumer
    if _task_created_consumer is None:
        _task_created_consumer = TaskCreatedConsumer()
    return _task_created_consumer
