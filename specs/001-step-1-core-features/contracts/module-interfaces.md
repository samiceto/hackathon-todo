# Module Interface Contracts - Step 1

**Feature**: Core Todo Features
**Date**: 2025-12-31
**Phase**: 1 - Design & Contracts

## Overview

This document defines the interface contracts between modules in the Step 1 console application. These contracts ensure clean separation of concerns and facilitate testing and future migration.

---

## Module Architecture

```
┌─────────────────┐
│    main.py      │  Entry point, orchestration
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│     ui.py       │  User interface, input/output
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   storage.py    │  Business logic, CRUD operations
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   models.py     │  Data structures
└─────────────────┘
```

---

## 1. models.py

### Purpose
Defines data structures with validation logic.

### Public Interface

#### Class: `Task`

```python
@dataclass
class Task:
    """Represents a single todo item."""

    # Attributes
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # Methods
    def __post_init__(self) -> None:
        """Validate and normalize attributes."""

    def toggle_completed(self) -> None:
        """Toggle the completion status."""

    def update(self, title: str | None = None,
               description: str | None = None) -> None:
        """Update task attributes with validation."""
```

### Contract Guarantees

- `Task.__post_init__()` validates that title is non-empty
- `Task.title` and `Task.description` are always stripped of whitespace
- `Task.update()` raises `ValueError` if title is empty
- `Task.id` is immutable after creation
- `Task.created_at` is immutable after creation

### Dependencies
- Python stdlib: `dataclasses`, `datetime`

---

## 2. storage.py

### Purpose
Manages in-memory task storage and CRUD operations.

### Public Interface

#### Class: `TaskStorage`

```python
class TaskStorage:
    """In-memory storage for tasks."""

    def __init__(self) -> None:
        """Initialize empty storage."""

    def add(self, title: str, description: str = "") -> Task:
        """
        Create and store a new task.

        Args:
            title: Task title (required, non-empty)
            description: Task description (optional, default="")

        Returns:
            The newly created Task with auto-generated ID

        Raises:
            ValueError: If title is empty or whitespace-only
        """

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: The task ID to retrieve

        Returns:
            Task if found, None otherwise
        """

    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks sorted by ID.

        Returns:
            List of all tasks (empty list if none exist)
        """

    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            title: New title (optional, must be non-empty if provided)
            description: New description (optional)

        Returns:
            Updated Task if found, None if task doesn't exist

        Raises:
            ValueError: If title is empty or whitespace-only
        """

    def toggle_complete(self, task_id: int) -> Optional[Task]:
        """
        Toggle completion status of a task.

        Args:
            task_id: ID of task to toggle

        Returns:
            Updated Task if found, None if task doesn't exist
        """

    def delete(self, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task was deleted, False if task didn't exist
        """

    def count(self) -> int:
        """
        Count total number of tasks.

        Returns:
            Number of tasks in storage
        """
```

### Contract Guarantees

- Task IDs start at 1 and increment sequentially
- `get()` returns None (not exception) for non-existent IDs
- `get_all()` returns tasks sorted by ID ascending
- `update()` with None arguments leaves those fields unchanged
- `toggle_complete()` flips boolean state (incomplete ↔ complete)
- `delete()` is idempotent (safe to call multiple times)
- All methods that modify tasks return the modified Task (or None if not found)

### Dependencies
- `models.Task`
- Python stdlib: `typing`

---

## 3. ui.py

### Purpose
Handles all user interaction (input, output, display formatting).

### Public Interface

#### Display Functions

```python
def display_menu() -> str:
    """
    Display the main menu and get user choice.

    Returns:
        User's menu selection as string ("1"-"6")
    """

def view_tasks_ui(storage: TaskStorage) -> None:
    """
    Display all tasks in formatted table.

    Args:
        storage: TaskStorage instance to read from

    Side Effects:
        Prints formatted task list to stdout
        Prints friendly message if no tasks exist
    """
```

#### Input Functions

```python
def get_non_empty_input(prompt: str) -> str:
    """
    Get non-empty input from user with retry loop.

    Args:
        prompt: Message to display to user

    Returns:
        Non-empty, whitespace-stripped string

    Side Effects:
        Loops until valid input received
        Prints error message on empty input
    """

def get_task_id(storage: TaskStorage, prompt: str) -> int:
    """
    Get valid task ID from user with retry loop.

    Args:
        storage: TaskStorage to validate ID against
        prompt: Message to display to user

    Returns:
        Valid task ID that exists in storage

    Side Effects:
        Loops until valid ID entered
        Prints error for non-numeric or non-existent IDs
    """

def get_optional_input(prompt: str, current_value: str) -> str:
    """
    Get input that can be empty (for updates).

    Args:
        prompt: Message to display, should include current value
        current_value: Existing value to use if input is empty

    Returns:
        User input if provided, otherwise current_value
    """
```

#### Operation Functions

```python
def add_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for adding a new task.

    Args:
        storage: TaskStorage to add task to

    Side Effects:
        Prompts user for title and description
        Creates task in storage
        Prints success message
    """

def mark_complete_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for marking task complete/incomplete.

    Args:
        storage: TaskStorage containing tasks

    Side Effects:
        Prompts user for task ID
        Toggles task completion status
        Prints success message
    """

def update_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for updating task details.

    Args:
        storage: TaskStorage containing tasks

    Side Effects:
        Prompts user for task ID and new values
        Updates task in storage
        Prints success message
    """

def delete_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for deleting a task.

    Args:
        storage: TaskStorage containing tasks

    Side Effects:
        Prompts user for task ID
        Deletes task from storage
        Prints success message
    """
```

### Contract Guarantees

- All `*_ui()` functions handle their own errors (don't raise exceptions to caller)
- Input functions loop until valid input received (never return invalid data)
- `get_task_id()` only returns IDs that exist in storage
- `get_non_empty_input()` never returns empty strings
- Display functions handle empty storage gracefully
- All user-facing messages are clear and actionable

### Dependencies
- `storage.TaskStorage`
- `models.Task`
- Python stdlib: `typing`

---

## 4. main.py

### Purpose
Application entry point and main event loop.

### Public Interface

```python
def main() -> None:
    """
    Main application entry point.

    Initializes storage and runs the interactive menu loop.

    Side Effects:
        Creates TaskStorage instance
        Loops until user chooses to exit
        Handles KeyboardInterrupt gracefully
        Prints welcome and goodbye messages
    """
```

### Contract Guarantees

- Initializes one TaskStorage instance for entire session
- Handles Ctrl+C (KeyboardInterrupt) gracefully
- Catches unexpected exceptions and prints user-friendly message
- Exits cleanly on user's exit command

### Dependencies
- `storage.TaskStorage`
- `ui.*` functions

---

## Error Handling Contract

### General Principles

1. **User Input Errors**: Caught and handled with retry loops (never crash)
2. **Validation Errors**: Caught and presented with clear messages
3. **Unexpected Errors**: Caught at top level, logged, user notified
4. **Keyboard Interrupt**: Caught and handled gracefully

### Error Message Format

```python
# User errors (input validation)
"Error: Title cannot be empty. Please try again."
"Error: Task ID 999 not found."
"Error: Please enter a valid task ID (number)."

# Unexpected errors
"Unexpected error: {error_details}"
"Please report this issue."
```

---

## Testing Contracts

### Unit Test Requirements

Each module must have unit tests covering:

- **models.py**: Task creation, validation, state changes
- **storage.py**: All CRUD operations, edge cases (empty storage, non-existent IDs)
- **ui.py**: Input validation, display formatting, error handling
- **main.py**: Integration test for full application flow

### Test Isolation

- Each test gets fresh `TaskStorage` instance (via fixture)
- No tests depend on state from previous tests
- Mock `input()` and `print()` for UI tests

---

## Migration Contract for Step 2

### Interface Stability

The following interfaces MUST remain stable during Step 2 migration:

1. **`TaskStorage` method signatures**: Same inputs/outputs
2. **`Task` dataclass attributes**: Same names and types
3. **UI function signatures**: Same parameters

### Allowed Changes

1. **`TaskStorage` implementation**: Replace dict with database
2. **Add new methods**: Extend interfaces without breaking existing
3. **Add new attributes to Task**: Only if they have defaults

This ensures UI and main.py require no changes when migrating to database storage.

---

## Summary

These interface contracts define clear boundaries between modules:

- **models.py**: Data + validation
- **storage.py**: Business logic + persistence
- **ui.py**: User interaction
- **main.py**: Orchestration

All modules follow the dependency rule (dependencies flow downward), enabling independent testing and future refactoring.
