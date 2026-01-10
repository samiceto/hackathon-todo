"""
Task Schemas

Pydantic schemas for task-related API requests and responses.
Provides data validation and serialization for task endpoints.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
    """Base task schema with common fields"""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str = Field(
        default="", max_length=5000, description="Task description (optional)"
    )


class TaskResponse(BaseModel):
    """
    Task response schema.

    Returned when fetching individual tasks or after create/update operations.
    Includes all task fields plus metadata.
    """

    id: int = Field(..., description="Unique task identifier")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """
    Task list response schema.

    Wraps a list of tasks with metadata for pagination support (future).
    Currently returns all tasks for the authenticated user.
    """

    tasks: List[TaskResponse] = Field(..., description="List of user's tasks")
    total: int = Field(..., description="Total number of tasks")

    @field_validator("tasks")
    @classmethod
    def sort_tasks_by_created_at(cls, v: List[TaskResponse]) -> List[TaskResponse]:
        """Sort tasks by created_at descending (newest first)"""
        return sorted(v, key=lambda task: task.created_at, reverse=True)


class CreateTaskRequest(BaseModel):
    """
    Create task request schema.

    Validates data for creating a new task.
    user_id is extracted from JWT token, not from request body.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str = Field(
        default="", max_length=5000, description="Task description (optional)"
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace"""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: str) -> str:
        """Strip leading/trailing whitespace from description"""
        return v.strip() if v else ""


class UpdateTaskRequest(BaseModel):
    """
    Update task request schema.

    Allows partial updates - all fields are optional.
    At least one field must be provided.
    """

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Updated task title"
    )
    description: Optional[str] = Field(
        None, max_length=5000, description="Updated task description"
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not just whitespace if provided"""
        if v is not None and v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from description if provided"""
        return v.strip() if v else v

    def has_updates(self) -> bool:
        """Check if at least one field is being updated"""
        return self.title is not None or self.description is not None
