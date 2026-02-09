"""
Task Service

Business logic for task-related operations.
Handles CRUD operations with proper data isolation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlmodel import Session, select

from ..models.task import Task
from ..models.user import User
from ..models.reminder import Reminder
from ..schemas.task import CreateTaskRequest, UpdateTaskRequest
from .recurrence_service import RecurrenceService


class TaskService:
    """Service for task-related business logic"""

    @staticmethod
    def _create_or_update_reminder(
        session: Session, task: Task, user_id: int
    ) -> Optional[Reminder]:
        """
        Create or update reminder for a task if due_date and reminder_offset are set.

        Args:
            session: Database session
            task: Task object
            user_id: ID of the user

        Returns:
            Reminder object if created/updated, None otherwise

        Note:
            - Deletes existing unsent reminders for the task
            - Creates new reminder if due_date and reminder_offset are set
            - reminder_at = due_date - reminder_offset (minutes)
        """
        # Delete existing unsent reminders for this task
        existing_reminders = session.exec(
            select(Reminder).where(
                Reminder.task_id == task.id,
                Reminder.sent == False
            )
        ).all()
        for reminder in existing_reminders:
            session.delete(reminder)

        # Create new reminder if conditions are met
        if task.due_date and task.reminder_offset:
            # Calculate reminder time: due_date - reminder_offset (minutes)
            reminder_at = task.due_date - timedelta(minutes=task.reminder_offset)

            # Only create reminder if reminder_at is in the future
            if reminder_at > datetime.now(timezone.utc):
                new_reminder = Reminder(
                    task_id=task.id,
                    user_id=user_id,
                    reminder_at=reminder_at,
                    sent=False,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(new_reminder)
                session.commit()
                session.refresh(new_reminder)
                return new_reminder

        return None

    @staticmethod
    def get_all_tasks(session: Session, user_id: int) -> List[Task]:
        """
        Retrieve all tasks for a specific user.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of Task objects ordered by created_at descending (newest first)

        Note:
            Data isolation is enforced by filtering on user_id.
            Only tasks belonging to the authenticated user are returned.
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        tasks = session.exec(statement).all()
        return list(tasks)

    @staticmethod
    def get_task_by_id(session: Session, task_id: int, user_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.

        Args:
            session: Database session
            task_id: ID of the task to retrieve
            user_id: ID of the user (for data isolation)

        Returns:
            Task object if found and belongs to user, None otherwise

        Note:
            Data isolation enforced by requiring both task_id AND user_id match.
            Prevents users from accessing other users' tasks.
        """
        statement = select(Task).where(
            Task.id == task_id, Task.user_id == user_id
        )
        task = session.exec(statement).first()
        return task

    @staticmethod
    def create_task(
        session: Session, user_id: int, task_data: CreateTaskRequest
    ) -> Task:
        """
        Create a new task for the user.

        Args:
            session: Database session
            user_id: ID of the user creating the task
            task_data: Validated task creation data

        Returns:
            Newly created Task object

        Raises:
            ValueError: If user_id doesn't exist (foreign key constraint)
        """
        # Verify user exists
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Calculate next_occurrence if recurrence_rule is provided
        next_occurrence = None
        if task_data.recurrence_rule:
            # Use due_date as start if provided, otherwise use current time
            start_time = task_data.due_date if task_data.due_date else datetime.now(timezone.utc)
            next_occurrence = RecurrenceService.calculate_next_occurrence(
                task_data.recurrence_rule,
                after=start_time
            )

        # Create new task
        new_task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            # Step 5: Advanced fields
            priority=task_data.priority,
            due_date=task_data.due_date,
            recurrence_rule=task_data.recurrence_rule,
            reminder_offset=task_data.reminder_offset,
            next_occurrence=next_occurrence,
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Create reminder if due_date and reminder_offset are set
        TaskService._create_or_update_reminder(session, new_task, user_id)

        return new_task

    @staticmethod
    def update_task(
        session: Session,
        task_id: int,
        user_id: int,
        task_data: UpdateTaskRequest,
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: ID of the user (for data isolation)
            task_data: Validated update data (partial updates allowed)

        Returns:
            Updated Task object if found, None if task not found or doesn't belong to user

        Note:
            Only updates fields that are provided (not None).
            Automatically updates updated_at timestamp.
            Recalculates next_occurrence if recurrence_rule or due_date changes.
        """
        # Retrieve task with data isolation check
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Track if recurrence-related fields changed
        recurrence_changed = False

        # Update only provided fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        # Step 5: Update advanced fields
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
            recurrence_changed = True
        if task_data.recurrence_rule is not None:
            task.recurrence_rule = task_data.recurrence_rule
            recurrence_changed = True
        if task_data.reminder_offset is not None:
            task.reminder_offset = task_data.reminder_offset

        # Recalculate next_occurrence if recurrence_rule changed
        if recurrence_changed and task.recurrence_rule:
            start_time = task.due_date if task.due_date else datetime.now(timezone.utc)
            task.next_occurrence = RecurrenceService.calculate_next_occurrence(
                task.recurrence_rule,
                after=start_time
            )
        elif task_data.recurrence_rule == "":  # Empty string to clear recurrence
            task.recurrence_rule = None
            task.next_occurrence = None

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        # Create or update reminder if due_date and reminder_offset changed
        TaskService._create_or_update_reminder(session, task, user_id)

        return task

    @staticmethod
    def toggle_completion(
        session: Session, task_id: int, user_id: int
    ) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            session: Database session
            task_id: ID of the task to toggle
            user_id: ID of the user (for data isolation)

        Returns:
            Updated Task object if found, None if task not found or doesn't belong to user
        """
        # Retrieve task with data isolation check
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: int) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: ID of the user (for data isolation)

        Returns:
            True if task was deleted, False if task not found or doesn't belong to user
        """
        # Retrieve task with data isolation check
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return False

        session.delete(task)
        session.commit()

        return True
