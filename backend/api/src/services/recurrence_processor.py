"""Recurrence processor service for generating recurring task instances.

This service queries tasks with due recurrences and creates new task instances
based on their recurrence rules. Designed to be triggered periodically by a
background job or cron schedule (e.g., every 1 minute via Dapr Cron Binding).
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select

from ..models.task import Task
from .recurrence_service import RecurrenceService

logger = logging.getLogger(__name__)


class RecurrenceProcessor:
    """Service for processing recurring tasks and creating new instances.

    Workflow:
    1. Query tasks where next_occurrence <= now AND recurrence_rule is not null
    2. For each task, create a new task instance (copy of original)
    3. Calculate next_occurrence for the original task
    4. Update original task's next_occurrence
    5. Publish task.created event for new instance (handled by caller)

    Design decisions:
    - Creates new task instances (not modifying original)
    - Preserves original task as template
    - New instances inherit: title, description, priority, reminder_offset
    - New instances get fresh: id, completed=False, created_at, updated_at
    - Original task's next_occurrence is updated to next recurrence time
    - Original task's due_date is NOT changed (remains as template)
    """

    @staticmethod
    def process_recurring_tasks(session: Session) -> List[Task]:
        """Process all tasks with due recurrences and create new instances.

        Args:
            session: Database session

        Returns:
            List of newly created task instances

        Note:
            This method should be called periodically (e.g., every 1 minute).
            It's idempotent - safe to call multiple times without duplicates
            because it only processes tasks where next_occurrence <= now.
        """
        current_time = datetime.now(timezone.utc)

        # Query tasks with due recurrences
        statement = select(Task).where(
            Task.recurrence_rule.isnot(None),
            Task.next_occurrence.isnot(None),
            Task.next_occurrence <= current_time,
        )
        recurring_tasks = session.exec(statement).all()

        logger.info(f"Found {len(recurring_tasks)} tasks with due recurrences")

        new_instances = []

        for template_task in recurring_tasks:
            try:
                # Create new task instance from template
                new_instance = RecurrenceProcessor._create_task_instance(
                    session, template_task
                )
                if new_instance:
                    new_instances.append(new_instance)

                # Update template task's next_occurrence
                RecurrenceProcessor._update_next_occurrence(session, template_task)

            except Exception as e:
                logger.error(
                    f"Failed to process recurring task {template_task.id}: {str(e)}",
                    exc_info=True,
                )
                # Continue processing other tasks even if one fails
                continue

        logger.info(f"Created {len(new_instances)} new task instances")
        return new_instances

    @staticmethod
    def _create_task_instance(session: Session, template_task: Task) -> Optional[Task]:
        """Create a new task instance from a recurring task template.

        Args:
            session: Database session
            template_task: The recurring task template

        Returns:
            Newly created task instance, or None if creation failed

        Note:
            The new instance is a copy of the template with:
            - Fresh ID (auto-generated)
            - completed=False (always starts incomplete)
            - created_at=now, updated_at=now
            - due_date=next_occurrence (moved from template's next_occurrence)
            - recurrence_rule=None (instances don't recur, only templates)
            - next_occurrence=None (instances don't recur, only templates)
            - Inherits: title, description, priority, reminder_offset, user_id
        """
        if not template_task.next_occurrence:
            logger.warning(
                f"Task {template_task.id} has no next_occurrence, skipping instance creation"
            )
            return None

        # Create new instance with inherited fields
        new_instance = Task(
            user_id=template_task.user_id,
            title=template_task.title,
            description=template_task.description,
            completed=False,  # Always start incomplete
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            # Inherit advanced fields (except recurrence)
            priority=template_task.priority,
            due_date=template_task.next_occurrence,  # Instance due date = template's next occurrence
            recurrence_rule=None,  # Instances don't recur
            reminder_offset=template_task.reminder_offset,
            next_occurrence=None,  # Instances don't recur
        )

        session.add(new_instance)
        session.commit()
        session.refresh(new_instance)

        logger.info(
            f"Created task instance {new_instance.id} from template {template_task.id} "
            f"with due_date={new_instance.due_date}"
        )

        return new_instance

    @staticmethod
    def _update_next_occurrence(session: Session, template_task: Task) -> None:
        """Update the template task's next_occurrence to the next recurrence time.

        Args:
            session: Database session
            template_task: The recurring task template to update

        Note:
            If no more occurrences (COUNT or UNTIL reached), sets next_occurrence=None
            and the task will no longer be processed by the recurrence processor.
        """
        if not template_task.recurrence_rule:
            logger.warning(
                f"Task {template_task.id} has no recurrence_rule, skipping update"
            )
            return

        # Calculate next occurrence after current next_occurrence
        try:
            next_occurrence = RecurrenceService.calculate_next_occurrence(
                template_task.recurrence_rule,
                after=template_task.next_occurrence,
            )

            template_task.next_occurrence = next_occurrence
            template_task.updated_at = datetime.utcnow()

            session.add(template_task)
            session.commit()
            session.refresh(template_task)

            if next_occurrence:
                logger.info(
                    f"Updated template task {template_task.id} next_occurrence to {next_occurrence}"
                )
            else:
                logger.info(
                    f"Template task {template_task.id} has no more occurrences (COUNT/UNTIL reached)"
                )

        except ValueError as e:
            logger.error(
                f"Failed to calculate next occurrence for task {template_task.id}: {str(e)}"
            )
            # Don't update next_occurrence if calculation fails
            # This prevents the task from being stuck in error state

    @staticmethod
    def get_upcoming_recurrences(
        session: Session, user_id: int, limit: int = 10
    ) -> List[Task]:
        """Get upcoming recurring tasks for a user, ordered by next_occurrence.

        Args:
            session: Database session
            user_id: ID of the user
            limit: Maximum number of tasks to return (default: 10)

        Returns:
            List of recurring tasks with next_occurrence, ordered by soonest first

        Use case:
            Display "Upcoming Recurring Tasks" in UI to show user what's scheduled.
        """
        statement = (
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.recurrence_rule.isnot(None),
                Task.next_occurrence.isnot(None),
            )
            .order_by(Task.next_occurrence.asc())
            .limit(limit)
        )

        upcoming_tasks = session.exec(statement).all()
        return list(upcoming_tasks)
