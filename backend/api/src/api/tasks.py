"""
Tasks API Endpoints

RESTful API endpoints for task management operations.
All endpoints require JWT authentication and enforce data isolation.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
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
from ..services.tag_service import TagService
from ..services.search_service import SearchService
from ..services.filter_service import FilterService
from ..services.event_publisher import EventPublisher
from ..models.event import TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent
from ..models.task_tag import TaskTag

logger = logging.getLogger(__name__)
event_publisher = EventPublisher()

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
    # Search parameter
    search: Optional[str] = Query(None, description="Search query for full-text search on title and description"),
    # Filter parameters
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: 'completed' or 'incomplete'"),
    priority: Optional[str] = Query(None, description="Filter by priority: 'low', 'medium', 'high', or 'urgent'"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (task must have ALL specified tags)"),
    due_date_start: Optional[datetime] = Query(None, description="Filter tasks with due_date >= this date (ISO 8601 format)"),
    due_date_end: Optional[datetime] = Query(None, description="Filter tasks with due_date <= this date (ISO 8601 format)"),
    # Sort parameters
    sort_by: Optional[str] = Query(None, description="Sort by field: 'created_at', 'updated_at', 'due_date', 'priority', or 'title'"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc' (default: desc)"),
    # Pagination parameters
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results (default: 100, max: 1000)"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination (default: 0)"),
) -> TaskListResponse:
    """
    Get tasks for the authenticated user with optional search, filter, and sort.

    Supports full-text search, multi-criteria filtering, and flexible sorting.
    All filtering is combined with AND logic (task must match all specified criteria).

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id in the URL must match the authenticated user's ID.

    **Query Parameters**:
    - `search`: Full-text search on title and description (uses PostgreSQL tsvector)
    - `status`: Filter by completion status ('completed' or 'incomplete')
    - `priority`: Filter by priority level ('low', 'medium', 'high', 'urgent')
    - `tags`: Filter by tag names (task must have ALL specified tags)
    - `due_date_start`: Filter tasks with due_date >= this date
    - `due_date_end`: Filter tasks with due_date <= this date
    - `sort_by`: Sort field (created_at, updated_at, due_date, priority, title)
    - `sort_order`: Sort order ('asc' or 'desc', default: desc)
    - `limit`: Max results (default: 100, max: 1000)
    - `offset`: Pagination offset (default: 0)

    **Response**:
    - `tasks`: List of task objects matching criteria
    - `total`: Total number of tasks returned

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `400 Bad Request`: Invalid filter parameters
    - `500 Internal Server Error`: Database error

    **Examples**:
    - `/1/tasks?search=meeting`: Search for "meeting" in title or description
    - `/1/tasks?status=incomplete&priority=high`: Incomplete high-priority tasks
    - `/1/tasks?tags=urgent&tags=work`: Tasks with both "urgent" AND "work" tags
    - `/1/tasks?due_date_start=2026-01-30T00:00:00Z&sort_by=due_date`: Tasks due after Jan 30, sorted by due date
    """
    # Verify user_id matches authenticated user (data isolation check)
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot access tasks for user {user_id}. You can only access your own tasks.",
        )

    # Validate filter parameters
    if status_filter or priority or due_date_start or due_date_end:
        validation_result = FilterService.validate_filter_params(
            status=status_filter,
            priority=priority,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filter parameters: {', '.join(validation_result['errors'])}"
            )

    # Validate sort parameters
    valid_sort_fields = ["created_at", "updated_at", "due_date", "priority", "title"]
    if sort_by and sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field: {sort_by}. Valid options: {valid_sort_fields}"
        )

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_order: {sort_order}. Valid options: asc, desc"
        )

    # Determine which service to use based on parameters
    tasks = []

    if search:
        # Use SearchService for full-text search
        logger.info(f"Using SearchService for query: '{search}' (user_id={user_id})")
        tasks = SearchService.search_tasks(session, user_id, search, limit, offset)

    elif status_filter or priority or tags or due_date_start or due_date_end:
        # Use FilterService for multi-criteria filtering
        logger.info(f"Using FilterService with criteria (user_id={user_id})")
        tasks = FilterService.filter_tasks(
            session,
            user_id,
            status=status_filter,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            limit=limit,
            offset=offset
        )

    else:
        # Use TaskService for simple retrieval (no search/filter)
        logger.info(f"Using TaskService for simple retrieval (user_id={user_id})")
        tasks = TaskService.get_all_tasks(session, user_id)

    # Apply sorting if specified (and not using SearchService, which has its own ranking)
    if sort_by and not search:
        reverse = (sort_order == "desc")

        # Define sort key functions for each field
        sort_key_map = {
            "created_at": lambda t: t.created_at,
            "updated_at": lambda t: t.updated_at,
            "due_date": lambda t: t.due_date if t.due_date else datetime.min,
            "priority": lambda t: ["low", "medium", "high", "urgent"].index(t.priority.value) if t.priority else -1,
            "title": lambda t: t.title.lower(),
        }

        tasks = sorted(tasks, key=sort_key_map[sort_by], reverse=reverse)
        logger.info(f"Sorted {len(tasks)} tasks by {sort_by} ({sort_order})")

    # Convert to response model
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    logger.info(f"Returning {len(task_responses)} tasks for user_id={user_id}")

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

        # Publish task.created event
        try:
            event = TaskCreatedEvent.create(
                user_id=new_task.user_id,
                task_id=new_task.id,
                title=new_task.title,
                description=new_task.description,
                priority=new_task.priority,
                due_date=new_task.due_date.isoformat() if new_task.due_date else None,
                recurrence_rule=new_task.recurrence_rule,
            )
            event_publisher.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish task.created event: {str(e)}", exc_info=True)
            # Continue even if event publishing fails (non-critical)

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

    # Publish task.updated event
    try:
        event = TaskUpdatedEvent.create(
            user_id=updated_task.user_id,
            task_id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            completed=updated_task.completed,
            priority=updated_task.priority,
            due_date=updated_task.due_date.isoformat() if updated_task.due_date else None,
            recurrence_rule=updated_task.recurrence_rule,
        )
        event_publisher.publish(event)
    except Exception as e:
        logger.error(f"Failed to publish task.updated event: {str(e)}", exc_info=True)
        # Continue even if event publishing fails (non-critical)

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

    # Publish task.completed event if task was just completed
    if updated_task.completed:
        try:
            event = TaskCompletedEvent.create(
                user_id=updated_task.user_id,
                task_id=updated_task.id,
                title=updated_task.title,
                completed_at=updated_task.updated_at.isoformat(),
            )
            event_publisher.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish task.completed event: {str(e)}", exc_info=True)
            # Continue even if event publishing fails (non-critical)

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

    # Get task details before deletion (for event publishing)
    task_to_delete = TaskService.get_task_by_id(session, task_id, user_id)
    if not task_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # Delete task with data isolation
    deleted = TaskService.delete_task(session, task_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # Publish task.deleted event
    try:
        event = TaskDeletedEvent.create(
            user_id=task_to_delete.user_id,
            task_id=task_to_delete.id,
            title=task_to_delete.title,
        )
        event_publisher.publish(event)
    except Exception as e:
        logger.error(f"Failed to publish task.deleted event: {str(e)}", exc_info=True)
        # Continue even if event publishing fails (non-critical)

    # 204 No Content - no return statement needed


# ============================================================================
# Tag Management Endpoints (Step 5 - User Story 3)
# ============================================================================


@router.get("/{user_id}/tasks/{task_id}/tags", response_model=List[str])
async def get_task_tags(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to get tags for"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[str]:
    """
    Get all tags for a specific task.

    Returns a list of tag names (strings) for the task.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Response**: List of tag names (e.g., ["urgent", "work", "meeting"])

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

    # Verify task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # Get tags for task
    tags = TagService.get_tags_for_task(session, task_id)

    # Return tag names only (not full TaskTag objects)
    return [tag.tag_name for tag in tags]


@router.post(
    "/{user_id}/tasks/{task_id}/tags",
    response_model=List[str],
    status_code=status.HTTP_201_CREATED,
)
async def add_task_tag(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to add tag to"),
    tag_name: str = ...,
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[str]:
    """
    Add a tag to a task.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Request Body**:
    - `tag_name`: Tag name to add (1-50 characters, case-insensitive)

    **Response**: Updated list of all tag names for the task.

    **Business Rules**:
    - Maximum 10 tags per task
    - Tag names are case-insensitive (stored lowercase)
    - Duplicate tags are ignored (idempotent)

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found or doesn't belong to user
    - `400 Bad Request`: Invalid tag name or max tags exceeded
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot access tasks for user {user_id}.",
        )

    # Verify task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # Add tag
    try:
        TagService.add_tag(session, task_id, tag_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Return updated list of tags
    tags = TagService.get_tags_for_task(session, task_id)
    return [tag.tag_name for tag in tags]


@router.delete("/{user_id}/tasks/{task_id}/tags/{tag_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_tag(
    user_id: int = Path(..., description="User ID (must match authenticated user)"),
    task_id: int = Path(..., description="Task ID to remove tag from"),
    tag_name: str = Path(..., description="Tag name to remove"),
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """
    Remove a tag from a task.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Data Isolation**: The user_id must match authenticated user, and task must belong to that user.

    **Response**: 204 No Content on success (no response body).

    **Errors**:
    - `401 Unauthorized`: Missing or invalid JWT token
    - `403 Forbidden`: user_id doesn't match authenticated user
    - `404 Not Found`: Task not found, doesn't belong to user, or tag doesn't exist
    """
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot access tasks for user {user_id}.",
        )

    # Verify task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or doesn't belong to you.",
        )

    # Remove tag
    try:
        removed = TagService.remove_tag(session, task_id, tag_name)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag '{tag_name}' not found on task {task_id}.",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 204 No Content - no return statement needed
