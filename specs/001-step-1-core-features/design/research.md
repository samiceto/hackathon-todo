# Research & Technical Decisions - Step 1

**Feature**: Core Todo Features (In-Memory Console App)
**Date**: 2025-12-31
**Phase**: 0 - Research & Outline

## Overview

This document captures technical research and architectural decisions for implementing the Step 1 console todo application with 5 basic operations (Add, View, Mark Complete, Update, Delete).

## Technology Decisions

### 1. Python Data Structures for In-Memory Storage

**Decision**: Use Python `dict` with integer keys for task storage, combined with `dataclass` for Task model

**Rationale**:
- Dictionary provides O(1) lookup by ID
- Dataclass provides type safety and automatic `__init__`, `__repr__` methods
- No external dependencies required (stdlib only)
- Easy migration path to ORM models in Step 2

**Alternatives Considered**:
- Plain dictionaries: Less type safety, no validation
- Lists: O(n) lookup performance, harder to maintain unique IDs
- Pydantic models: External dependency, overkill for in-memory storage

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

# Storage
tasks: Dict[int, Task] = {}
next_id: int = 1
```

---

### 2. Menu-Driven Console Interface

**Decision**: Use numbered menu with `input()` loop and match/case statements (Python 3.10+)

**Rationale**:
- User-friendly for non-technical users
- Clear visual presentation of available options
- Easy to extend with new features in future steps
- Match/case provides clean, readable control flow

**Alternatives Considered**:
- Command-line arguments (argparse): Less interactive, steeper learning curve
- Single-letter commands (vim-style): Less discoverable for new users
- REPL-style: More complex implementation

**Implementation Pattern**:
```python
def display_menu():
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task Complete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")
    return input("\nSelect an option (1-6): ").strip()

def main():
    while True:
        choice = display_menu()
        match choice:
            case "1": add_task()
            case "2": view_tasks()
            # ...
            case "6": break
            case _: print("Invalid option. Please try again.")
```

---

### 3. Input Validation Strategy

**Decision**: Validate at point of entry with clear error messages and retry loops

**Rationale**:
- Prevents invalid data from entering the system
- Provides immediate feedback to users
- Satisfies FR-008 (non-empty titles) and FR-009 (clear error messages)
- Graceful degradation (no crashes on bad input)

**Alternatives Considered**:
- Exception-based validation: Harder to provide user-friendly messages
- Schema validation (cerberus, marshmallow): External dependencies
- Post-hoc validation: Allows bad data into system

**Implementation Pattern**:
```python
def get_non_empty_input(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Error: Input cannot be empty. Please try again.")

def get_task_id(prompt: str) -> int:
    while True:
        value = input(prompt).strip()
        try:
            task_id = int(value)
            if task_id in tasks:
                return task_id
            print(f"Error: Task ID {task_id} not found.")
        except ValueError:
            print("Error: Please enter a valid task ID (number).")
```

---

### 4. Display Formatting

**Decision**: Use Python f-strings with manual column alignment for task list display

**Rationale**:
- No external dependencies (pure stdlib)
- Readable output with clear visual separation
- Sufficient for Step 1 requirements
- Can upgrade to `rich` library in future steps if needed

**Alternatives Considered**:
- `tabulate` library: External dependency, violates constraint
- `rich` library: External dependency, overkill for simple display
- CSV format: Less human-readable

**Implementation Pattern**:
```python
def view_tasks():
    if not tasks:
        print("\nNo tasks found. Add your first task to get started!")
        return

    print("\n" + "="*80)
    print(f"{'ID':<5} {'Status':<12} {'Title':<30} {'Description':<30}")
    print("="*80)

    for task in tasks.values():
        status = "✓ Complete" if task.completed else "○ Incomplete"
        title = task.title[:28] + ".." if len(task.title) > 30 else task.title
        desc = task.description[:28] + ".." if len(task.description) > 30 else task.description
        print(f"{task.id:<5} {status:<12} {title:<30} {desc:<30}")

    print("="*80)
```

---

### 5. Module Structure & Separation of Concerns

**Decision**: Split functionality across 4 modules: `models.py`, `storage.py`, `ui.py`, `main.py`

**Rationale**:
- Adheres to Clean Architecture principle (Constitution III)
- Each module under 300 lines (Constitution III requirement)
- Clear separation enables easy testing
- Prepares for Step 2 migration (storage layer abstraction)

**Module Responsibilities**:

| Module | Responsibility | Key Functions/Classes |
|--------|---------------|----------------------|
| `models.py` | Data structures | `Task` dataclass |
| `storage.py` | In-memory CRUD | `add_task()`, `get_task()`, `update_task()`, `delete_task()`, `get_all_tasks()`, `toggle_complete()` |
| `ui.py` | User interaction | `display_menu()`, `add_task_ui()`, `view_tasks_ui()`, `get_task_id()`, `get_non_empty_input()` |
| `main.py` | Application entry | `main()` function with event loop |

**Dependency Flow**: `main.py` → `ui.py` → `storage.py` → `models.py`

---

### 6. ID Generation Strategy

**Decision**: Use simple integer counter starting at 1, incremented on each add

**Rationale**:
- Simple and predictable for users
- Sufficient for in-memory storage (no concurrency issues)
- Easy to migrate to database auto-increment in Step 2
- Handles arbitrary large numbers (Python arbitrary precision)

**Alternatives Considered**:
- UUID: Overkill for single-user console app, less user-friendly
- Timestamp-based: Potential collisions, harder to type
- Hash-based: Not sequential, harder to remember

**Implementation Pattern**:
```python
class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        task = Task(
            id=self._next_id,
            title=title,
            description=description
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task
```

---

### 7. Error Handling Philosophy

**Decision**: Use defensive programming with input validation; no exception propagation to user

**Rationale**:
- Satisfies SC-009 (no crashes)
- Provides user-friendly experience
- Clear error messages (FR-009)
- Graceful degradation

**Patterns**:
- Validate all inputs before processing
- Return to menu on errors (don't crash)
- Use Optional return types for operations that might fail
- Print clear error messages with actionable guidance

---

### 8. Testing Strategy

**Decision**: Use pytest with fixtures for task storage, focus on unit and integration tests

**Rationale**:
- pytest is Python standard for testing
- Fixtures enable test isolation
- Supports TDD workflow (Red-Green-Refactor)
- Satisfies Constitution V (Test-Driven Development)

**Test Structure**:
```
tests/
├── test_models.py        # Task dataclass validation
├── test_storage.py       # CRUD operations
├── test_ui.py           # Input validation, display formatting
└── conftest.py          # Shared fixtures
```

**Key Fixtures**:
```python
@pytest.fixture
def empty_storage():
    return TaskStorage()

@pytest.fixture
def storage_with_tasks():
    storage = TaskStorage()
    storage.add("Task 1", "Description 1")
    storage.add("Task 2", "Description 2")
    return storage
```

---

### 9. Project Setup with UV

**Decision**: Use UV for dependency management with pyproject.toml configuration

**Rationale**:
- Required by constitution (Technology Constraints)
- Fast, modern Python package manager
- Supports lock files for reproducibility
- Compatible with standard Python packaging

**Configuration** (`pyproject.toml`):
```toml
[project]
name = "hackathon-todo"
version = "0.1.0"
description = "Step 1: In-memory console todo application"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

---

### 10. Ctrl+C Interrupt Handling

**Decision**: Use try/except KeyboardInterrupt in main loop

**Rationale**:
- Handles edge case from spec (graceful Ctrl+C handling)
- Prevents ugly stack traces
- Professional user experience

**Implementation**:
```python
def main():
    try:
        while True:
            choice = display_menu()
            # ... handle choices
    except KeyboardInterrupt:
        print("\n\nExiting application. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please report this issue.")
```

---

## Architecture Decisions Summary

| Decision Area | Choice | Migration Path to Step 2 |
|--------------|--------|-------------------------|
| Storage | Dict + Dataclass | Replace with SQLModel + PostgreSQL |
| Interface | Menu-driven CLI | Add FastAPI endpoints |
| Validation | Input validation functions | Move to Pydantic models |
| Display | Manual f-string formatting | JSON responses for API |
| Testing | pytest unit tests | Add API integration tests |
| ID Generation | Integer counter | Database auto-increment |

---

## Open Questions

None - all technical decisions resolved for Step 1 implementation.

---

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with Task entity specification
- Define internal contracts (interfaces between modules)
- Write quickstart.md for development setup
