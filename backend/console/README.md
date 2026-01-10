# Hackathon Todo - Console Application (Step 1)

A simple, elegant command-line task manager built with Python. This is the Step 1 implementation of the Hackathon Todo project.

## Quick Start

### Prerequisites
- Python 3.13 or higher
- [UV](https://docs.astral.sh/uv/) package manager

### Installation & Run

```bash
# Navigate to this directory
cd backend/console

# Install dependencies
uv sync

# Run application
uv run hackathon-todo
# OR
uv run python -m hackathon_todo.main
```

## Features

- ✅ **Add Tasks** - Create tasks with title and optional description
- ✅ **View Tasks** - See all tasks in a formatted list with status indicators
- ✅ **Mark Complete** - Toggle tasks between complete (✓) and incomplete (○)
- ✅ **Update Tasks** - Edit task titles and descriptions
- ✅ **Delete Tasks** - Remove tasks from your list
- ✅ **Interactive Menu** - Easy-to-use menu-driven interface
- ✅ **Error Handling** - Robust validation and retry logic
- ✅ **Graceful Exit** - Clean shutdown with Ctrl+C support

## Testing

### Run All Tests
```bash
uv run pytest
```

### Run with Coverage
```bash
uv run pytest --cov=src/hackathon_todo --cov-report=term-missing
```

### Run with HTML Coverage Report
```bash
uv run pytest --cov=src/hackathon_todo --cov-report=html
# Open htmlcov/index.html in browser
```

**Test Coverage**: 97.44% (129 tests passing)

## Project Structure

```
backend/console/
├── src/
│   └── hackathon_todo/
│       ├── __init__.py      # Package initialization
│       ├── main.py          # Application entry point
│       ├── models.py        # Task data model
│       ├── storage.py       # In-memory task storage
│       └── ui.py            # User interface functions
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_models.py       # Task model tests
│   ├── test_storage.py      # Storage layer tests
│   ├── test_ui.py           # UI function tests
│   └── test_integration.py  # Integration tests
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Architecture

**Layered Architecture**:
```
Application Layer (main.py)     ← Menu loop, routing
       ↓
UI Layer (ui.py)                ← User interaction, formatting
       ↓
Storage Layer (storage.py)      ← CRUD operations
       ↓
Data Layer (models.py)          ← Task entity, validation
```

## Data Model

```python
@dataclass
class Task:
    id: int                    # Unique identifier
    title: str                 # Task title (required)
    description: str = ""      # Optional description
    completed: bool = False    # Completion status
    created_at: datetime       # Creation timestamp
```

## Storage

- **Type**: In-memory dictionary
- **Persistence**: Session-based (data lost on exit)
- **ID Assignment**: Sequential auto-increment
- **Future**: Migrateable to database in Step 2 (FastAPI + PostgreSQL)

## Status Indicators

- `○` - Incomplete task
- `✓` - Complete task

## Usage Example

```
==================================================
Welcome to Hackathon Todo!
Your simple command-line task manager
==================================================

==============================
=== Hackathon Todo Menu ===
==============================
1. Add Task
2. View Tasks
3. Mark Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit
==============================

Enter your choice (1-6): 1

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

Task added successfully! (ID: 1)
Title: Buy groceries
Description: Milk, eggs, bread
```

## Development

### Code Quality
- **Clean Architecture** - Separation of concerns
- **Test-Driven Development** - 97.44% test coverage
- **Type Hints** - Python 3.13+ type annotations
- **Input Validation** - Robust error handling
- **User Experience** - Clear messages and intuitive interface

### Manual Tests & Validation
- `manual_test_phase*.py` - Manual test scripts for each phase
- `performance_test.py` - Performance testing
- `final_validation_checklist.md` - Validation checklist
- `quickstart_validation_results.md` - Validation results

## Next Steps

This console application is **Step 1 Complete** ✅

**Future Evolution**:
- **Step 2**: FastAPI backend + Next.js frontend (see `backend/api/` and `frontend/`)
- **Step 3**: AI-powered chatbot with OpenAI integration
- **Step 4**: Kubernetes deployment
- **Step 5**: Cloud-native production deployment

---

**Part of**: Hackathon Todo - Progressive Task Management Application

**See**: `../../README.md` for full project roadmap and monorepo structure
