"""
Task Service

Business logic for task-related operations.
Handles CRUD operations with proper data isolation and validation.
"""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from ..models.task import Task
from ..models.user import User
from ..schemas.task import CreateTaskRequest, UpdateTaskRequest


class TaskService:
    """Service for task-related business logic"""

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

        # Create new task
        new_task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

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
        """
        # Retrieve task with data isolation check
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Update only provided fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

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
