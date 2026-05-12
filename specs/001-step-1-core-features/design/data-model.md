# Data Model Specification - Step 1

**Feature**: Core Todo Features
**Date**: 2025-12-31
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data model for Step 1's in-memory todo application. The model is intentionally simple and focused on core CRUD operations, with a clear migration path to database-backed storage in Step 2.

---

## Entity: Task

### Purpose
Represents a single todo item with essential tracking information.

### Attributes

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes | Auto-generated | Unique, positive integer | Unique identifier for the task |
| `title` | `str` | Yes | - | Non-empty, max recommended 1000 chars | Brief description of the task |
| `description` | `str` | No | `""` (empty string) | Max recommended 5000 chars | Detailed information about the task |
| `completed` | `bool` | Yes | `False` | - | Indicates whether task is done |
| `created_at` | `datetime` | Yes | Current timestamp | ISO 8601 format | Timestamp when task was created |

### Validation Rules

1. **Title Validation** (FR-008):
   - MUST NOT be empty string
   - MUST NOT be whitespace-only
   - SHOULD trim leading/trailing whitespace
   - MAY truncate display to 30 chars in list view (full text preserved in storage)

2. **Description Validation**:
   - MAY be empty string
   - No minimum length requirement
   - MAY truncate display to 30 chars in list view (full text preserved in storage)

3. **ID Validation**:
   - MUST be positive integer
   - MUST be unique within storage
   - MUST NOT be user-modifiable
   - MUST be assigned sequentially starting from 1

4. **Completed Validation**:
   - MUST be boolean (True/False)
   - Toggleable via Mark Complete operation

5. **Created At Validation**:
   - MUST be set on creation
   - MUST NOT be user-modifiable
   - MUST use system local time
   - Format: `datetime.datetime` object (Python stdlib)

### State Transitions

```
[New Task]
    ↓
created_at = now()
completed = False
    ↓
[Incomplete Task] ←→ [Complete Task]
    ↑                    ↑
    |                    |
 Toggle             Toggle
    |                    |
    └────────────────────┘

[Any State]
    ↓
Update (title, description)
    ↓
[Updated Task]

[Any State]
    ↓
Delete
    ↓
[Removed from Storage]
```

### Relationships

**Step 1**: No relationships (single entity model)

**Future (Step 2+)**:
- Task → User (many-to-one)
- Task → Tags (many-to-many)
- Task → Category (many-to-one)

---

## Storage Model

### In-Memory Structure

```python
# Storage container
tasks: Dict[int, Task] = {}

# ID counter
next_id: int = 1
```

### Operations

| Operation | Input | Output | Side Effects |
|-----------|-------|--------|--------------|
| `add` | `title: str, description: str` | `Task` | Increments `next_id`, adds task to `tasks` dict |
| `get` | `task_id: int` | `Optional[Task]` | None |
| `get_all` | None | `List[Task]` | None |
| `update` | `task_id: int, title: Optional[str], description: Optional[str]` | `Optional[Task]` | Modifies task in place |
| `toggle_complete` | `task_id: int` | `Optional[Task]` | Toggles `completed` boolean |
| `delete` | `task_id: int` | `bool` (success/failure) | Removes task from `tasks` dict |

### Invariants

1. All task IDs in `tasks` dict are unique
2. All task IDs are positive integers
3. `next_id` is always greater than any existing task ID
4. All tasks have non-empty titles
5. No two tasks can have the same ID

---

## Python Implementation

### Dataclass Definition

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """
    Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-generated)
        title: Brief task description (required, non-empty)
        description: Detailed task information (optional)
        completed: Completion status (default: False)
        created_at: Creation timestamp (auto-generated)
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task attributes after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        # Normalize title and description
        self.title = self.title.strip()
        self.description = self.description.strip()

    def toggle_completed(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed

    def update(self, title: str | None = None, description: str | None = None) -> None:
        """
        Update task attributes.

        Args:
            title: New title (must be non-empty if provided)
            description: New description (can be empty)

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            self.title = title.strip()

        if description is not None:
            self.description = description.strip()
```

### Storage Interface

```python
from typing import Dict, List, Optional

class TaskStorage:
    """
    In-memory storage for tasks.

    This class will be replaced with database-backed storage in Step 2.
    The interface is designed to minimize migration effort.
    """

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """
        Create and store a new task.

        Args:
            title: Task title (required, non-empty)
            description: Task description (optional)

        Returns:
            The newly created Task

        Raises:
            ValueError: If title is empty
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
        """
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks sorted by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            The updated Task if found, None otherwise

        Raises:
            ValueError: If title is empty
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
            The updated Task if found, None otherwise
        """
        task = self.get(task_id)
        if task:
            task.toggle_completed()
        return task

    def delete(self, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task was deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def count(self) -> int:
        """Return the total number of tasks."""
        return len(self._tasks)
```

---

## Migration Path to Step 2

### Changes Required

1. **Replace `TaskStorage` with SQLModel ORM**:
   ```python
   from sqlmodel import SQLModel, Field

   class Task(SQLModel, table=True):
       id: int = Field(default=None, primary_key=True)
       title: str = Field(min_length=1)
       description: str = Field(default="")
       completed: bool = Field(default=False)
       created_at: datetime = Field(default_factory=datetime.now)
   ```

2. **Add database session management**:
   - Replace dict operations with SQLModel queries
   - Add transaction handling
   - Implement connection pooling

3. **Preserve interface**:
   - Keep same method signatures (`add`, `get`, `update`, etc.)
   - Maintain same validation rules
   - Return same data types

### Backwards Compatibility

The interface is designed so that UI and business logic remain unchanged when migrating to database storage. Only the `TaskStorage` implementation needs to change.

---

## Test Cases

### Task Entity Tests

```python
def test_task_creation_with_valid_data():
    task = Task(id=1, title="Test Task", description="Test Description")
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)

def test_task_creation_with_empty_title_raises_error():
    with pytest.raises(ValueError, match="title cannot be empty"):
        Task(id=1, title="", description="Test")

def test_task_creation_with_whitespace_title_raises_error():
    with pytest.raises(ValueError, match="title cannot be empty"):
        Task(id=1, title="   ", description="Test")

def test_task_toggle_completed():
    task = Task(id=1, title="Test")
    assert task.completed is False
    task.toggle_completed()
    assert task.completed is True
    task.toggle_completed()
    assert task.completed is False

def test_task_update_title():
    task = Task(id=1, title="Original")
    task.update(title="Updated")
    assert task.title == "Updated"

def test_task_update_with_empty_title_raises_error():
    task = Task(id=1, title="Original")
    with pytest.raises(ValueError, match="title cannot be empty"):
        task.update(title="")
```

### Storage Tests

```python
def test_add_task_increments_id():
    storage = TaskStorage()
    task1 = storage.add("Task 1")
    task2 = storage.add("Task 2")
    assert task1.id == 1
    assert task2.id == 2

def test_get_existing_task():
    storage = TaskStorage()
    task = storage.add("Test Task")
    retrieved = storage.get(task.id)
    assert retrieved == task

def test_get_nonexistent_task_returns_none():
    storage = TaskStorage()
    assert storage.get(999) is None

def test_get_all_returns_sorted_list():
    storage = TaskStorage()
    task1 = storage.add("Task 1")
    task2 = storage.add("Task 2")
    all_tasks = storage.get_all()
    assert len(all_tasks) == 2
    assert all_tasks[0].id < all_tasks[1].id

def test_update_existing_task():
    storage = TaskStorage()
    task = storage.add("Original")
    updated = storage.update(task.id, title="Updated")
    assert updated.title == "Updated"

def test_toggle_complete():
    storage = TaskStorage()
    task = storage.add("Test")
    storage.toggle_complete(task.id)
    assert storage.get(task.id).completed is True

def test_delete_existing_task():
    storage = TaskStorage()
    task = storage.add("Test")
    assert storage.delete(task.id) is True
    assert storage.get(task.id) is None

def test_delete_nonexistent_task_returns_false():
    storage = TaskStorage()
    assert storage.delete(999) is False
```

---

## Summary

The data model for Step 1 is intentionally minimal, focusing on core CRUD functionality with clean separation between data (Task) and storage (TaskStorage). The interface is designed to ease migration to database-backed storage in Step 2 while maintaining simplicity for the console application requirements.
