"""
In-memory storage for tasks.

This module provides TaskStorage class for managing tasks in memory using
a dictionary-based approach. Designed for easy migration to database storage
in future steps.
"""

from typing import Optional

from hackathon_todo.models import Task


class TaskStorage:
    """
    In-memory storage for tasks with CRUD operations.

    This class manages task persistence using an in-memory dictionary.
    The interface is designed to minimize migration effort when transitioning
    to database-backed storage in Step 2.

    Attributes:
        _tasks: Internal dictionary mapping task IDs to Task instances
        _next_id: Counter for generating sequential task IDs

    Examples:
        >>> storage = TaskStorage()
        >>> task = storage.add("Buy groceries", "Milk, eggs, bread")
        >>> task.id
        1
        >>> storage.count()
        1
    """

    def __init__(self) -> None:
        """Initialize empty task storage with ID counter starting at 1."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """
        Create and store a new task.

        Args:
            title: Task title (required, non-empty)
            description: Task description (optional, default: "")

        Returns:
            The newly created Task instance

        Raises:
            ValueError: If title is empty or whitespace-only

        Examples:
            >>> storage = TaskStorage()
            >>> task = storage.add("Write tests")
            >>> task.id
            1
            >>> task.title
            'Write tests'
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: The task ID to retrieve

        Returns:
            The Task if found, None otherwise

        Examples:
            >>> storage = TaskStorage()
            >>> task = storage.add("Test")
            >>> retrieved = storage.get(task.id)
            >>> retrieved.title
            'Test'
            >>> storage.get(999)  # Non-existent ID
            None
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks sorted by ID.

        Returns:
            List of all tasks ordered by ID ascending.
            Returns empty list if no tasks exist.

        Examples:
            >>> storage = TaskStorage()
            >>> storage.add("Task 1")
            >>> storage.add("Task 2")
            >>> tasks = storage.get_all()
            >>> len(tasks)
            2
            >>> tasks[0].id < tasks[1].id
            True
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            title: New title (optional, must be non-empty if provided)
            description: New description (optional)

        Returns:
            The updated Task if found, None if task doesn't exist

        Raises:
            ValueError: If title is empty or whitespace-only

        Examples:
            >>> storage = TaskStorage()
            >>> task = storage.add("Original")
            >>> updated = storage.update(task.id, title="Updated")
            >>> updated.title
            'Updated'
        """
        task = self.get(task_id)
        if task:
            task.update(title, description)
        return task

    def toggle_complete(self, task_id: int) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of task to toggle

        Returns:
            The updated Task if found, None if task doesn't exist

        Examples:
            >>> storage = TaskStorage()
            >>> task = storage.add("Test")
            >>> task.completed
            False
            >>> toggled = storage.toggle_complete(task.id)
            >>> toggled.completed
            True
        """
        task = self.get(task_id)
        if task:
            task.toggle_completed()
        return task

    def delete(self, task_id: int) -> bool:
        """
        Delete a task.

        This operation is idempotent - calling it multiple times with
        the same ID is safe.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task was deleted, False if task didn't exist

        Examples:
            >>> storage = TaskStorage()
            >>> task = storage.add("Test")
            >>> storage.delete(task.id)
            True
            >>> storage.delete(task.id)  # Second call
            False
        """
        if task_id in self._tasks:
            deleted_task = self._tasks[task_id]
            del self._tasks[task_id]
            print("task deleted successfully",deleted_task)
            return True
        return False

    def count(self) -> int:
        """
        Return the total number of tasks in storage.

        Returns:
            Number of tasks currently stored

        Examples:
            >>> storage = TaskStorage()
            >>> storage.count()
            0
            >>> storage.add("Task 1")
            >>> storage.count()
            1
        """
        return len(self._tasks)
