#!/usr/bin/env python3
"""
MCP Server for Hackathon Todo Task Management.

This server provides tools to interact with the Todo application through
the Model Context Protocol, enabling AI agents to manage tasks conversationally.

Step 3: AI-Powered Chatbot - MCP Server Foundation
"""

from typing import Optional, List
from enum import Enum
import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP, Context
from sqlmodel import Session, select

# Import models from the application
from ..models import Task
from ..db import get_session

# Initialize the MCP server
mcp = FastMCP("todo_mcp")


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# Pydantic Models for Input Validation
class AddTaskInput(BaseModel):
    """Input model for adding a new task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: int = Field(..., description="User ID who owns the task", ge=1)
    title: str = Field(
        ...,
        description="Task title (e.g., 'Buy groceries', 'Complete project report')",
        min_length=1,
        max_length=500
    )
    description: Optional[str] = Field(
        default="",
        description="Optional task description with additional details",
        max_length=5000
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class ListTasksInput(BaseModel):
    """Input model for listing tasks."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: int = Field(..., description="User ID to filter tasks", ge=1)
    completed: Optional[bool] = Field(
        default=None,
        description="Filter by completion status (true=completed, false=incomplete, null=all)"
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum number of tasks to return",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of tasks to skip for pagination",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class CompleteTaskInput(BaseModel):
    """Input model for marking a task as complete/incomplete."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: int = Field(..., description="User ID who owns the task", ge=1)
    task_id: int = Field(..., description="Task ID to mark complete/incomplete", ge=1)
    completed: bool = Field(
        ...,
        description="Completion status to set (true=completed, false=incomplete)"
    )


class UpdateTaskInput(BaseModel):
    """Input model for updating a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: int = Field(..., description="User ID who owns the task", ge=1)
    task_id: int = Field(..., description="Task ID to update", ge=1)
    title: Optional[str] = Field(
        default=None,
        description="New task title (leave null to keep existing)",
        min_length=1,
        max_length=500
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description (leave null to keep existing)",
        max_length=5000
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else None


class DeleteTaskInput(BaseModel):
    """Input model for deleting a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: int = Field(..., description="User ID who owns the task", ge=1)
    task_id: int = Field(..., description="Task ID to delete", ge=1)


# Shared utility functions
def _handle_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, ValueError):
        return f"Error: Invalid input - {str(e)}"
    return f"Error: {type(e).__name__} - {str(e)}"


def _format_task_markdown(task: Task) -> str:
    """Format a single task as markdown."""
    status = "✓" if task.completed else "○"
    lines = [
        f"### {status} Task #{task.id}: {task.title}",
        f"- **Status**: {'Completed' if task.completed else 'Incomplete'}",
        f"- **Created**: {task.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]
    if task.description:
        lines.append(f"- **Description**: {task.description}")
    return "\n".join(lines)


def _format_task_json(task: Task) -> dict:
    """Format a single task as JSON-serializable dict."""
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


# Tool definitions
@mcp.tool(
    name="todo_add_task",
    annotations={
        "title": "Add New Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def todo_add_task(params: AddTaskInput) -> str:
    """Add a new task to the user's todo list.

    This tool creates a new task with the specified title and optional description.
    The task starts in an incomplete state and is associated with the authenticated user.

    Args:
        params (AddTaskInput): Validated input parameters containing:
            - user_id (int): User ID who owns the task (1-2147483647)
            - title (str): Task title, required (1-500 characters)
            - description (Optional[str]): Task description, optional (max 5000 characters)

    Returns:
        str: JSON-formatted response containing the created task with the following schema:

        Success response:
        {
            "id": int,              # Auto-generated task ID
            "user_id": int,         # User who owns the task
            "title": str,           # Task title
            "description": str,     # Task description (empty string if not provided)
            "completed": bool,      # Always false for new tasks
            "created_at": str,      # ISO 8601 timestamp
            "updated_at": str       # ISO 8601 timestamp
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: "Add a task to buy groceries" -> params with title="Buy groceries"
        - Use when: "Create task 'Call dentist' with note 'Schedule checkup'" ->
          params with title="Call dentist", description="Schedule checkup"
        - Don't use when: User wants to list tasks (use todo_list_tasks)
        - Don't use when: User wants to update existing task (use todo_update_task)
    """
    try:
        # Get database session
        session: Session = next(get_session())

        # Create new task
        task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description or "",
            completed=False
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        # Return JSON response
        response = _format_task_json(task)
        return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_error(e)
    finally:
        session.close()


@mcp.tool(
    name="todo_list_tasks",
    annotations={
        "title": "List Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def todo_list_tasks(params: ListTasksInput) -> str:
    """List tasks for the authenticated user with optional filtering.

    This tool retrieves tasks for the specified user, with optional filtering by
    completion status. Results are paginated and can be returned in markdown or JSON format.

    Args:
        params (ListTasksInput): Validated input parameters containing:
            - user_id (int): User ID to filter tasks (1-2147483647)
            - completed (Optional[bool]): Filter by status (true/false/null for all)
            - limit (Optional[int]): Max results to return, 1-100 (default: 20)
            - offset (Optional[int]): Results to skip for pagination (default: 0)
            - response_format (ResponseFormat): Output format (default: markdown)

    Returns:
        str: Formatted response containing task list

        Markdown format (response_format="markdown"):
        # Tasks for User {user_id}
        Found {total} tasks (showing {count})

        ### ✓ Task #1: Completed Task
        - **Status**: Completed
        - **Created**: 2026-01-11 10:00:00 UTC
        - **Description**: Task details...

        JSON format (response_format="json"):
        {
            "total": int,           # Total tasks matching filter
            "count": int,           # Tasks in this response
            "offset": int,          # Current pagination offset
            "has_more": bool,       # More results available
            "next_offset": int,     # Offset for next page (null if no more)
            "tasks": [              # Array of task objects
                {
                    "id": int,
                    "user_id": int,
                    "title": str,
                    "description": str,
                    "completed": bool,
                    "created_at": str,
                    "updated_at": str
                }
            ]
        }

        Error response:
        "Error: <error message>" or "No tasks found"

    Examples:
        - Use when: "Show me my tasks" -> params with user_id only
        - Use when: "List completed tasks" -> params with completed=true
        - Use when: "Show incomplete tasks" -> params with completed=false
        - Don't use when: User wants to create a task (use todo_add_task)
    """
    try:
        # Get database session
        session: Session = next(get_session())

        # Build query
        query = select(Task).where(Task.user_id == params.user_id)

        # Apply completion filter if specified
        if params.completed is not None:
            query = query.where(Task.completed == params.completed)

        # Get total count
        count_query = select(Task).where(Task.user_id == params.user_id)
        if params.completed is not None:
            count_query = count_query.where(Task.completed == params.completed)
        total = len(session.exec(count_query).all())

        # Apply pagination
        query = query.offset(params.offset).limit(params.limit)

        # Execute query
        tasks = session.exec(query).all()

        if not tasks and params.offset == 0:
            return "No tasks found"

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# Tasks for User {params.user_id}", ""]
            filter_desc = "all tasks"
            if params.completed is True:
                filter_desc = "completed tasks"
            elif params.completed is False:
                filter_desc = "incomplete tasks"
            lines.append(f"Found {total} {filter_desc} (showing {len(tasks)})")
            lines.append("")

            for task in tasks:
                lines.append(_format_task_markdown(task))
                lines.append("")

            if total > params.offset + len(tasks):
                lines.append(f"*More tasks available. Use offset={params.offset + len(tasks)} to see next page.*")

            return "\n".join(lines)

        else:
            # Machine-readable JSON format
            response = {
                "total": total,
                "count": len(tasks),
                "offset": params.offset,
                "has_more": total > params.offset + len(tasks),
                "next_offset": params.offset + len(tasks) if total > params.offset + len(tasks) else None,
                "tasks": [_format_task_json(task) for task in tasks]
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_error(e)
    finally:
        session.close()


@mcp.tool(
    name="todo_complete_task",
    annotations={
        "title": "Complete/Uncomplete Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def todo_complete_task(params: CompleteTaskInput) -> str:
    """Mark a task as completed or incomplete.

    This tool toggles the completion status of an existing task. It updates the
    task's completed flag and updated_at timestamp.

    Args:
        params (CompleteTaskInput): Validated input parameters containing:
            - user_id (int): User ID who owns the task (1-2147483647)
            - task_id (int): Task ID to update (1-2147483647)
            - completed (bool): Status to set (true=completed, false=incomplete)

    Returns:
        str: JSON-formatted response containing the updated task

        Success response:
        {
            "id": int,
            "user_id": int,
            "title": str,
            "description": str,
            "completed": bool,      # Updated completion status
            "created_at": str,
            "updated_at": str       # Updated timestamp
        }

        Error response:
        "Error: Task not found" or "Error: <error message>"

    Examples:
        - Use when: "Mark task 5 as complete" -> params with task_id=5, completed=true
        - Use when: "Uncomplete task 3" -> params with task_id=3, completed=false
        - Don't use when: User wants to delete the task (use todo_delete_task)
    """
    try:
        # Get database session
        session: Session = next(get_session())

        # Find task
        task = session.exec(
            select(Task).where(Task.id == params.task_id, Task.user_id == params.user_id)
        ).first()

        if not task:
            return "Error: Task not found"

        # Update completion status
        task.completed = params.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        # Return JSON response
        response = _format_task_json(task)
        return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_error(e)
    finally:
        session.close()


@mcp.tool(
    name="todo_update_task",
    annotations={
        "title": "Update Task Details",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def todo_update_task(params: UpdateTaskInput) -> str:
    """Update task title and/or description.

    This tool updates the title and/or description of an existing task. You can
    update one or both fields. Fields not specified will remain unchanged.

    Args:
        params (UpdateTaskInput): Validated input parameters containing:
            - user_id (int): User ID who owns the task (1-2147483647)
            - task_id (int): Task ID to update (1-2147483647)
            - title (Optional[str]): New title (null to keep existing, 1-500 chars)
            - description (Optional[str]): New description (null to keep existing, max 5000 chars)

    Returns:
        str: JSON-formatted response containing the updated task

        Success response:
        {
            "id": int,
            "user_id": int,
            "title": str,           # Updated if specified
            "description": str,     # Updated if specified
            "completed": bool,
            "created_at": str,
            "updated_at": str       # Updated timestamp
        }

        Error response:
        "Error: Task not found" or "Error: No fields to update" or "Error: <error message>"

    Examples:
        - Use when: "Change task 5 title to 'Buy milk'" ->
          params with task_id=5, title="Buy milk"
        - Use when: "Update description of task 3" ->
          params with task_id=3, description="New description"
        - Use when: "Change both title and description" ->
          params with both title and description
        - Don't use when: User wants to mark task complete (use todo_complete_task)
    """
    try:
        # Get database session
        session: Session = next(get_session())

        # Find task
        task = session.exec(
            select(Task).where(Task.id == params.task_id, Task.user_id == params.user_id)
        ).first()

        if not task:
            return "Error: Task not found"

        # Update fields if provided
        updated = False
        if params.title is not None:
            task.title = params.title
            updated = True
        if params.description is not None:
            task.description = params.description
            updated = True

        if not updated:
            return "Error: No fields to update. Provide title and/or description."

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        # Return JSON response
        response = _format_task_json(task)
        return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_error(e)
    finally:
        session.close()


@mcp.tool(
    name="todo_delete_task",
    annotations={
        "title": "Delete Task",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def todo_delete_task(params: DeleteTaskInput) -> str:
    """Delete a task permanently.

    This tool permanently deletes a task from the database. This action cannot
    be undone. The task is completely removed from the user's task list.

    Args:
        params (DeleteTaskInput): Validated input parameters containing:
            - user_id (int): User ID who owns the task (1-2147483647)
            - task_id (int): Task ID to delete (1-2147483647)

    Returns:
        str: JSON-formatted response confirming deletion

        Success response:
        {
            "success": true,
            "message": "Task {task_id} deleted successfully",
            "deleted_task_id": int
        }

        Error response:
        "Error: Task not found" or "Error: <error message>"

    Examples:
        - Use when: "Delete task 5" -> params with task_id=5
        - Use when: "Remove task 3" -> params with task_id=3
        - Don't use when: User wants to mark task complete (use todo_complete_task)
        - Don't use when: User wants to update task (use todo_update_task)

    Warning:
        This operation is DESTRUCTIVE and cannot be undone. The task will be
        permanently removed from the database.
    """
    try:
        # Get database session
        session: Session = next(get_session())

        # Find task
        task = session.exec(
            select(Task).where(Task.id == params.task_id, Task.user_id == params.user_id)
        ).first()

        if not task:
            return "Error: Task not found"

        # Delete task
        session.delete(task)
        session.commit()

        # Return success response
        response = {
            "success": True,
            "message": f"Task {params.task_id} deleted successfully",
            "deleted_task_id": params.task_id
        }
        return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_error(e)
    finally:
        session.close()


if __name__ == "__main__":
    # Run the MCP server using stdio transport (for local integrations)
    mcp.run()
