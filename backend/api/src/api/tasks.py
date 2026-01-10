"""
Tasks API Endpoints

RESTful API endpoints for task management operations.
All endpoints require JWT authentication and enforce data isolation.
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from ..api.deps import get_current_user
from ..db.session import get_session
from ..schemas.task import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from ..services.tasks import TaskService

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskListResponse:
    """
    Get all tasks for the authenticated user.

    Returns a list of tasks ordered by creation date (newest first).
    Enforces data isolation - users can only see their own tasks.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id in the URL must match the authenticated user's ID.

    **Response**:
    - `tasks`: List of task objects with all fields
    - `total`: Total number of tasks for the user

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `500 Internal Server Error`: Database error
    """
    # Verify user_id matches authenticated user (data isolation check)
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot access tasks for user {user_id}. You can only access your own tasks.",
        )

    # Retrieve tasks from service
    tasks = TaskService.get_all_tasks(session, user_id)

    # Convert to response model
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return TaskListResponse(tasks=task_responses, total=len(task_responses))


@router.post(
    "/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_task(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_data: CreateTaskRequest = ...,
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id in the URL must match the authenticated user's ID.

    **Request Body**:
    - `title`: Task title (required, 1-500 characters)
    - `description`: Task description (optional, max 5000 characters)

    **Response**: Newly created task object with all fields including ID and timestamps.

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `422 Validation Error`: Invalid request data (empty title, too long, etc.)
    - `500 Internal Server Error`: Database error
    """
    # Verify user_id matches authenticated user (data isolation check)
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot create tasks for user {user_id}. You can only create your own tasks.",
        )

    # Create task via service
    try:
        new_task = TaskService.create_task(session, user_id, task_data)
        return TaskResponse.model_validate(new_task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to retrieve"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Get a specific task by ID.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Response**: Task object with all fields.

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found or doesn't belong to user
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot access tasks for user {user_id}.",
        )

    # Retrieve task with data isolation
    task = TaskService.get_task_by_id(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to update"),
    task_data: UpdateTaskRequest = ...,
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Update an existing task.

    Allows partial updates - provide only the fields you want to change.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Request Body** (all optional, but at least one required):
    - `title`: Updated task title (1-500 characters)
    - `description`: Updated task description (max 5000 characters)

    **Response**: Updated task object with new updated_at timestamp.

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found or doesn't belong to user
    - `422 Validation Error`: Invalid update data
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot update tasks for user {user_id}.",
        )

    # Validate that at least one field is being updated
    if not task_data.has_updates():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field (title or description) must be provided for update.",
        )

    # Update task with data isolation
    updated_task = TaskService.update_task(session, task_id, user_id, task_data)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    return TaskResponse.model_validate(updated_task)


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to toggle"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Toggle the completion status of a task.

    If the task is incomplete, marks it as complete.
    If the task is complete, marks it as incomplete.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Response**: Updated task object with toggled `completed` field and new updated_at timestamp.

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found or doesn't belong to user
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot update tasks for user {user_id}.",
        )

    # Toggle completion with data isolation
    updated_task = TaskService.toggle_completion(session, task_id, user_id)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    return TaskResponse.model_validate(updated_task)


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to delete"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """
    Delete a task permanently.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Response**: 204 No Content on success (no response body).

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found or doesn't belong to user
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot delete tasks for user {user_id}.",
        )

    # Delete task with data isolation
    deleted = TaskService.delete_task(session, task_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # 204 No Content - no return statement needed
