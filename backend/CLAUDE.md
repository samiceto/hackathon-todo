# Backend Development Context

## Overview

This directory contains all backend services for the Hackathon Todo application:

- **console/**: Step 1 - Original Python console application (✅ COMPLETE)
- **api/**: Step 2+ - FastAPI web application (📋 PLANNED)

**Current Status**: Console app complete and working. Preparing for FastAPI migration.

---

## Console Application (Step 1) ✅

**Location**: `backend/console/`

### Architecture

Clean layered architecture with separation of concerns:

```
┌─────────────────────────────────────────┐
│  Application Layer (main.py)           │  ← Entry point, menu loop
├─────────────────────────────────────────┤
│  UI Layer (ui.py)                      │  ← User interaction, formatting
├─────────────────────────────────────────┤
│  Storage Layer (storage.py)            │  ← CRUD operations
├─────────────────────────────────────────┤
│  Data Layer (models.py)                │  ← Task entity, validation
└─────────────────────────────────────────┘
```

### Module Details

**models.py** (99 lines) ✅
- `Task` dataclass with validation
- Fields: id, title, description, completed, created_at
- Type hints for all fields
- Immutable ID and created_at after creation

```python
@dataclass
class Task:
    id: int                    # Unique identifier (auto-assigned)
    title: str                 # Required, non-empty
    description: str = ""      # Optional
    completed: bool = False    # Status (incomplete by default)
    created_at: datetime       # Creation timestamp (auto-assigned)
```

**storage.py** (209 lines) ✅
- `TaskStorage` class for in-memory CRUD operations
- Methods:
  - `add(title, description)` → Task
  - `get(task_id)` → Task | None
  - `get_all()` → list[Task]
  - `update(task_id, title, description)` → Task | None
  - `toggle_complete(task_id)` → Task | None
  - `delete(task_id)` → bool
  - `count()` → int
- Sequential ID assignment (auto-increment)
- Error handling for invalid IDs
- Thread-safe for single-process use

**ui.py** (386 lines) ⚠️
- All user interface functions
- Input helpers:
  - `get_non_empty_input(prompt)`: Retry loop for required fields
  - `get_task_id(storage, prompt)`: Numeric validation + existence check
  - `get_optional_input(prompt)`: Skip with Enter, whitespace treated as skip
- UI operations:
  - `add_task_ui(storage)`
  - `view_tasks_ui(storage)`
  - `mark_complete_ui(storage)`
  - `update_task_ui(storage)`
  - `delete_task_ui(storage)`
- `display_menu()` function
- **Note**: Exceeds 300-line guideline; refactoring recommended for Step 2

**main.py** (88 lines) ✅
- Application entry point
- Menu loop with choice routing
- Welcome/goodbye messages
- KeyboardInterrupt (Ctrl+C) handling
- Integrates all 5 user stories

### Test Coverage

**Location**: `backend/console/tests/`

**Coverage**: 97.44% (129 tests passing)

**Test files**:
- **conftest.py**: pytest fixtures, TaskStorage fixture with clean state per test
- **test_models.py**: Task dataclass tests, validation tests
- **test_storage.py**: CRUD operation tests, edge case handling
- **test_ui.py**: UI function tests, input validation tests, error handling tests
- **test_integration.py**: End-to-end workflow tests
  - TestDisplayMenu (1 test)
  - TestFullCRUDWorkflow (2 tests)
  - TestEdgeCaseWorkflows (3 tests)
  - TestDataPersistence (2 tests)
  - TestMainFunction (7 tests)

### Running the Console App

```bash
# Navigate to console directory
cd backend/console

# Install dependencies
uv sync

# Run application
uv run hackathon-todo
# OR
uv run python -m hackathon_todo.main

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/hackathon_todo --cov-report=html

# Verbose test output
uv run pytest -v
```

### Storage Pattern (Step 1)

- **Type**: In-memory dictionary `{task_id: Task}`
- **ID Generation**: Sequential auto-increment (next_id counter)
- **Persistence**: Session-based (data lost on exit)
- **Migration Path**: Ready for PostgreSQL in Step 2 (same interface)

### Known Technical Debt

1. **Module Size**: ui.py (386 lines) exceeds 300-line guideline
   - **Acceptable**: For Step 1 MVP
   - **Refactoring Plan**: Split into input_helpers.py, task_operations.py, menu.py in Step 2

2. **Data Persistence**: In-memory (data lost on exit)
   - **Acceptable**: For Step 1 CLI application
   - **Migration**: PostgreSQL + SQLModel in Step 2

3. **Concurrency**: Single-process, no threading
   - **Acceptable**: For Step 1 CLI application
   - **Enhancement**: Thread-safe storage in Step 2 web application

---

## FastAPI Application (Step 2+) 📋

**Location**: `backend/api/` (planned)

**Status**: Not yet implemented. Structure prepared for future development.

### Planned Architecture

**Tech Stack**:
- FastAPI (async/await)
- SQLModel (ORM)
- Neon PostgreSQL (serverless database)
- Better Auth (JWT authentication)
- Pydantic v2 (validation)

**Planned Structure**:
```
backend/api/
├── app/
│   ├── main.py           # FastAPI application entry
│   ├── models.py         # SQLModel database models
│   ├── routes/           # API endpoints
│   │   ├── tasks.py      # Task CRUD endpoints
│   │   └── auth.py       # Authentication endpoints
│   ├── db.py             # Database connection
│   ├── auth.py           # JWT middleware
│   └── config.py         # Environment configuration
├── tests/                # API integration tests
├── pyproject.toml        # FastAPI project config
└── README.md             # API documentation
```

### Planned Migration Path

**Models Migration** (console → FastAPI):
```python
# Current (Console): src/hackathon_todo/models.py
@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime

# Future (FastAPI): backend/api/app/models.py
from sqlmodel import SQLModel, Field
from uuid import UUID

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**Storage → API Routes Migration**:
```python
# Current (Console): storage.add()
def add(self, title: str, description: str = "") -> Task:
    task = Task(id=self._next_id, title=title, description=description)
    self._tasks[task.id] = task
    self._next_id += 1
    return task

# Future (FastAPI): POST /api/{user_id}/tasks
@router.post("/api/{user_id}/tasks", response_model=Task)
async def create_task(
    user_id: str,
    title: str,
    description: str = "",
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    task = Task(user_id=current_user.id, title=title, description=description)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Planned API Endpoints

**Authentication**:
- All endpoints require: `Authorization: Bearer <jwt_token>`

**Task CRUD**:
- `GET /api/{user_id}/tasks` - List all tasks for authenticated user
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get single task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

### Planned Test Migration

**Console Tests → API Tests**:
```python
# Current (Console Test): test_storage.py
def test_add_task(storage):
    task = storage.add("Buy groceries", "Milk, eggs")
    assert task.id == 1
    assert task.title == "Buy groceries"

# Future (API Test): test_api_tasks.py
def test_create_task_api(client):
    response = client.post(
        "/api/user-123/tasks",
        json={"title": "Buy groceries", "description": "Milk, eggs"},
        headers={"Authorization": "Bearer mock-jwt-token"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Buy groceries"
```

---

## Development Guidelines

### Code Style
- **Type Hints**: Required for all functions
- **Docstrings**: Required for public functions
- **Error Handling**: User-friendly messages, retry loops (console) or HTTP errors (API)
- **Testing**: >90% coverage required
- **Naming**: Descriptive, clear intent

### Testing Requirements
- Minimum 90% test coverage (current: 97.44%)
- All CRUD operations tested
- Edge cases covered
- Integration tests for workflows

### Adding New Features

1. Check scope (console vs API)
2. Update relevant specs in `specs/`
3. Follow TDD: Write tests first
4. Implement feature
5. Verify all tests pass
6. Create PHR documenting work

---

## Quick Reference

### Console App Paths
- **Source**: `backend/console/src/hackathon_todo/`
- **Tests**: `backend/console/tests/`
- **Config**: `backend/console/pyproject.toml`
- **Specs**: `specs/001-step-1-core-features/`

### Commands
```bash
# Console app
cd backend/console && uv run hackathon-todo

# Tests
cd backend/console && uv run pytest

# Coverage
cd backend/console && uv run pytest --cov=src/hackathon_todo
```

---

**Last Updated**: 2026-01-05 (Monorepo restructuring - Phase 1)
