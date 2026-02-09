"""
MCP Tools Package - Shared Utilities and Base Patterns

This package provides shared utilities and patterns for MCP tool implementations,
including database session management, error handling, and response formatting.

Step 3: AI-Powered Chatbot - MCP Tool Utilities
"""

from typing import Optional, Generator
from contextlib import contextmanager
from datetime import datetime
from sqlmodel import Session

from ...db import get_session
from ...models import Task


# Database Session Management
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions in MCP tools.

    Provides automatic session cleanup and error handling for MCP tools.
    Use this in MCP tools to ensure proper database connection management.

    Yields:
        Session: SQLModel database session

    Example:
        with get_db_session() as session:
            task = session.get(Task, task_id)
            # ... perform operations ...
    """
    session: Session = next(get_session())
    try:
        yield session
    finally:
        session.close()


# Error Handling Utilities
def handle_tool_error(e: Exception) -> str:
    """Standardized error formatting for MCP tools.

    Converts exceptions into user-friendly error messages that guide
    AI agents toward correct usage and resolution.

    Args:
        e (Exception): The exception to format

    Returns:
        str: Formatted error message string

    Examples:
        ValueError -> "Error: Invalid input - {message}"
        Other -> "Error: {ExceptionType} - {message}"
    """
    if isinstance(e, ValueError):
        return f"Error: Invalid input - {str(e)}"
    return f"Error: {type(e).__name__} - {str(e)}"


# Task Formatting Utilities
def format_task_markdown(task: Task) -> str:
    """Format a task as human-readable markdown.

    Args:
        task (Task): Task model instance

    Returns:
        str: Markdown-formatted task display

    Example:
        ### ✓ Task #5: Buy groceries
        - **Status**: Completed
        - **Created**: 2026-01-11 10:00:00 UTC
        - **Description**: Milk, eggs, bread
    """
    status = "✓" if task.completed else "○"
    lines = [
        f"### {status} Task #{task.id}: {task.title}",
        f"- **Status**: {'Completed' if task.completed else 'Incomplete'}",
        f"- **Created**: {task.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]
    if task.description:
        lines.append(f"- **Description**: {task.description}")
    return "\n".join(lines)


def format_task_json(task: Task) -> dict:
    """Format a task as JSON-serializable dictionary.

    Args:
        task (Task): Task model instance

    Returns:
        dict: JSON-serializable task representation

    Example:
        {
            "id": 5,
            "user_id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": true,
            "created_at": "2026-01-11T10:00:00",
            "updated_at": "2026-01-11T10:30:00"
        }
    """
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


# User Authentication Utilities
def verify_task_ownership(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Verify that a user owns a specific task.

    This enforces ownership-based access control for task operations,
    ensuring users can only access their own tasks.

    Args:
        session (Session): Database session
        task_id (int): Task ID to verify
        user_id (int): User ID to verify ownership

    Returns:
        Optional[Task]: Task if found and owned by user, None otherwise

    Example:
        task = verify_task_ownership(session, task_id=5, user_id=1)
        if not task:
            return "Error: Task not found or access denied"
    """
    from sqlmodel import select
    return session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()


# Response Construction Utilities
def success_response(data: dict) -> str:
    """Create a standardized success response in JSON format.

    Args:
        data (dict): Response data to serialize

    Returns:
        str: JSON-formatted success response

    Example:
        return success_response({
            "success": True,
            "task": format_task_json(task)
        })
    """
    import json
    return json.dumps(data, indent=2)


def error_response(message: str) -> str:
    """Create a standardized error response.

    Args:
        message (str): Error message to return

    Returns:
        str: Formatted error response

    Example:
        return error_response("Task not found")
        # Returns: "Error: Task not found"
    """
    if not message.startswith("Error:"):
        return f"Error: {message}"
    return message


__all__ = [
    "get_db_session",
    "handle_tool_error",
    "format_task_markdown",
    "format_task_json",
    "verify_task_ownership",
    "success_response",
    "error_response"
]
