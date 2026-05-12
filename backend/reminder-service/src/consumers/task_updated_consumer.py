"""Consumer for task.updated events."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Set, Optional

from sqlmodel import Session, select

from ..models import Reminder

logger = logging.getLogger(__name__)


class TaskUpdatedConsumer:
    """Consumer for processing task.updated events.

    When a task is updated:
    1. Check if due_date or reminder_offset changed
    2. If changed, update existing Reminder record (or create/delete as needed)
    3. Return success status

    Cases handled:
    - due_date or reminder_offset changed → Update reminder_at
    - due_date removed → Delete reminder
    - due_date added (was None before) → Create reminder
    - No relevant changes → Skip

    Features:
    - Idempotency protection using event_id cache
    - Error handling with detailed logging
    - Validates reminder_at not in past
    """

    def __init__(self):
        """Initialize TaskUpdatedConsumer."""
        # Idempotency cache: Track processed event_ids
        self._processed_event_ids: Set[str] = set()
        self._max_cache_size = 10000

    async def handle_event(self, event: Dict[str, Any], session: Session) -> Dict[str, str]:
        """Handle task.updated event.

        Args:
            event: Task updated event payload from Dapr
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
                f"Processing task.updated event: event_id={event_id}, "
                f"task_id={task_id}, user_id={user_id}, due_date={due_date_str}, "
                f"reminder_offset={reminder_offset_minutes}"
            )

            # Validate required fields
            if not task_id or not user_id:
                logger.error(f"Missing required fields: task_id={task_id}, user_id={user_id}")
                raise ValueError("task_id and user_id are required")

            # Get existing reminder(s) for this task
            existing_reminder = self._get_existing_reminder(session, task_id)

            # Case 1: No due_date or reminder_offset → Delete reminder if exists
            if not due_date_str or reminder_offset_minutes is None:
                if existing_reminder:
                    logger.info(
                        f"due_date or reminder_offset removed - deleting reminder {existing_reminder.id}"
                    )
                    session.delete(existing_reminder)
                    session.commit()
                    self._mark_as_processed(event_id)
                    return {"status": "deleted", "reminder_id": existing_reminder.id}
                else:
                    logger.info("No due_date/reminder - no reminder to update")
                    self._mark_as_processed(event_id)
                    return {"status": "skipped", "reason": "no_due_date_or_reminder"}

            # Parse due_date
            due_date = self._parse_datetime(due_date_str)

            # Calculate new reminder_at
            reminder_at = due_date - timedelta(minutes=reminder_offset_minutes)

            # Don't create/update reminder if reminder_at is in the past
            now = datetime.now(timezone.utc)
            if reminder_at <= now:
                if existing_reminder:
                    # Delete existing reminder if time is in the past
                    logger.info(f"Reminder time is in the past - deleting reminder {existing_reminder.id}")
                    session.delete(existing_reminder)
                    session.commit()
                    self._mark_as_processed(event_id)
                    return {"status": "deleted", "reason": "reminder_in_past"}
                else:
                    logger.info("Reminder time is in the past - skipping creation")
                    self._mark_as_processed(event_id)
                    return {"status": "skipped", "reason": "reminder_in_past"}

            # Case 2: Reminder exists → Update reminder_at
            if existing_reminder:
                # Only update if reminder_at changed
                if existing_reminder.reminder_at != reminder_at:
                    logger.info(
                        f"Updating reminder {existing_reminder.id}: "
                        f"old_reminder_at={existing_reminder.reminder_at.isoformat()}, "
                        f"new_reminder_at={reminder_at.isoformat()}"
                    )
                    existing_reminder.reminder_at = reminder_at
                    existing_reminder.sent = False  # Reset sent flag
                    session.add(existing_reminder)
                    session.commit()
                    session.refresh(existing_reminder)

                    self._mark_as_processed(event_id)
                    return {
                        "status": "updated",
                        "reminder_id": existing_reminder.id,
                        "reminder_at": reminder_at.isoformat()
                    }
                else:
                    logger.info("Reminder unchanged - skipping update")
                    self._mark_as_processed(event_id)
                    return {"status": "unchanged"}

            # Case 3: No existing reminder → Create new one
            else:
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
                    f"Created new reminder: id={reminder.id}, task_id={task_id}, "
                    f"reminder_at={reminder_at.isoformat()}"
                )

                self._mark_as_processed(event_id)
                return {
                    "status": "created",
                    "reminder_id": reminder.id,
                    "reminder_at": reminder_at.isoformat()
                }

        except Exception as e:
            logger.error(f"Failed to process task.updated event: {str(e)}", exc_info=True)
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
_task_updated_consumer: TaskUpdatedConsumer | None = None


def get_task_updated_consumer() -> TaskUpdatedConsumer:
    """Get singleton TaskUpdatedConsumer instance.

    Returns:
        TaskUpdatedConsumer instance
    """
    global _task_updated_consumer
    if _task_updated_consumer is None:
        _task_updated_consumer = TaskUpdatedConsumer()
    return _task_updated_consumer
