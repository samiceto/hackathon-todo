# Hackathon Todo

A simple, elegant command-line task manager built with Python. Manage your todos with a clean interactive interface.

## Features

- ✅ **Add Tasks** - Create tasks with title and optional description
- ✅ **View Tasks** - See all tasks in a formatted list with status indicators
- ✅ **Mark Complete** - Toggle tasks between complete (✓) and incomplete (○)
- ✅ **Update Tasks** - Edit task titles and descriptions
- ✅ **Delete Tasks** - Remove tasks from your list
- ✅ **Interactive Menu** - Easy-to-use menu-driven interface
- ✅ **Error Handling** - Robust validation and retry logic
- ✅ **Graceful Exit** - Clean shutdown with Ctrl+C support

## Quick Start

### Prerequisites

- Python 3.13 or higher
- [UV](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon-todo

# UV will automatically install dependencies
uv sync
```

### Running the Application

```bash
# Run the application
uv run hackathon-todo
```

Or alternatively:

```bash
uv run python -m hackathon_todo.main
```

## Usage

### Main Menu

When you start the application, you'll see the main menu:

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

Enter your choice (1-6):
```

### 1. Add Task

Create a new task with a required title and optional description.

**Example:**
```
Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

Task added successfully! (ID: 1)
Title: Buy groceries
Description: Milk, eggs, bread
```

### 2. View Tasks

Display all tasks in a formatted list.

**Example:**
```
--- All Tasks ---

[1] ○ Buy groceries
    Milk, eggs, bread
[2] ✓ Complete project report
[3] ○ Schedule dentist appointment

Total tasks: 3
```

**Status Indicators:**
- `○` - Incomplete task
- `✓` - Complete task

### 3. Mark Complete/Incomplete

Toggle a task's completion status by ID.

**Example:**
```
Enter task ID to toggle completion: 1

Task 1 marked as complete!
[1] ✓ Buy groceries
```

### 4. Update Task

Edit a task's title and/or description. Press Enter to skip a field and keep its current value.

**Example:**
```
Updating task: Buy groceries
Press Enter to skip a field and keep its current value.

New title [current: Buy groceries] (press Enter to skip): Buy groceries and supplies
New description [current: Milk, eggs, bread] (press Enter to skip):

Task 1 updated successfully!
[1] ✓ Buy groceries and supplies
    Milk, eggs, bread
```

### 5. Delete Task

Remove a task from your list by ID.

**Example:**
```
Enter task ID to delete: 1

Task 1 deleted successfully!
Deleted: [1] Buy groceries and supplies

Remaining tasks: 2
```

### 6. Exit

Quit the application.

```
==================================================
Goodbye! Thanks for using Hackathon Todo.
==================================================
```

**Tip:** You can also press `Ctrl+C` at any time to exit gracefully.

## Development

### Project Structure

```
hackathon-todo/
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
├── .python-version          # Python version (3.13)
└── README.md                # This file
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py

# Generate coverage report
uv run pytest --cov=src/hackathon_todo --cov-report=html
```

**Test Coverage:** 97.44% (129 tests passing)

### Code Quality

The project follows these principles:
- **Clean Architecture** - Separation of concerns (models, storage, UI, main)
- **Test-Driven Development** - Comprehensive test coverage
- **Type Hints** - Python 3.13+ type annotations
- **Input Validation** - Robust error handling with retry logic
- **User Experience** - Clear messages and intuitive interface

### Module Guidelines

- `models.py` - Data structures and validation (99 lines)
- `storage.py` - CRUD operations for tasks (209 lines)
- `ui.py` - User interface functions (386 lines) *
- `main.py` - Application entry point and menu loop (88 lines)

\* *Note: ui.py exceeds the 300-line guideline. Refactoring into smaller modules is recommended for future versions.*

## Technical Details

### Architecture

The application uses a layered architecture:

1. **Data Layer** (`models.py`) - Task entity with validation
2. **Storage Layer** (`storage.py`) - In-memory CRUD operations
3. **UI Layer** (`ui.py`) - User interaction and formatting
4. **Application Layer** (`main.py`) - Menu loop and integration

### Data Model

```python
@dataclass
class Task:
    id: int                    # Unique identifier
    title: str                 # Task title (required)
    description: str = ""      # Optional description
    completed: bool = False    # Completion status
    created_at: datetime       # Creation timestamp
```

### Storage

- **Type:** In-memory dictionary
- **Persistence:** Session-based (data lost on exit)
- **ID Assignment:** Sequential auto-increment
- **Future:** Migrateable to database (Step 2)

## Roadmap

### Step 1: Core Todo Features ✅ (Complete)
- ✅ Add, view, update, delete tasks
- ✅ Mark tasks complete/incomplete
- ✅ Interactive CLI interface
- ✅ Comprehensive test coverage (97.44%)

### Step 2: Full-Stack Web Application (Planned)
- FastAPI backend
- Next.js frontend
- PostgreSQL database
- Docker containerization

### Step 3: AI-Powered Chatbot (Planned)
- OpenAI integration
- Natural language task management
- Smart task suggestions

### Step 4: Local Kubernetes Deployment (Planned)
- Minikube setup
- Service orchestration

### Step 5: Advanced Cloud Deployment (Planned)
- Cloud provider integration
- CI/CD pipeline
- Production deployment

## Contributing

This is a hackathon project developed using Spec-Driven Development (SDD) methodology. All features are specified before implementation, and all code is fully tested.

### Development Workflow

1. **Specify** - Define requirements in `specs/`
2. **Plan** - Create implementation plan
3. **Tasks** - Break down into testable tasks
4. **Implement** - Write tests first, then code (TDD)
5. **Validate** - Verify acceptance criteria

## License

[Specify license here]

## Acknowledgments

Built with:
- Python 3.13
- UV package manager
- pytest for testing
- Spec-Driven Development methodology

---

**Made with ❤️ for the Hackathon**

For questions or issues, please open an issue in the repository.
