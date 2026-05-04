"""
Task Schemas

Pydantic schemas for task-related API requests and responses.
Provides data validation and serialization for task endpoints.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator

from ..services.recurrence_service import RecurrenceService


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

    # Step 5: Advanced task fields
    priority: str = Field(default="medium", description="Task priority (low, medium, high, urgent)")
    due_date: Optional[datetime] = Field(None, description="Task due date (optional)")
    recurrence_rule: Optional[str] = Field(None, description="iCal RRULE format recurrence rule (optional)")
    reminder_offset: Optional[int] = Field(None, description="Minutes before due_date to send reminder (optional)")
    next_occurrence: Optional[datetime] = Field(None, description="Next occurrence time for recurring tasks (optional)")

    model_config = {"from_attributes": True}

    @field_serializer('created_at', 'updated_at')
    def serialize_utc(self, v: datetime) -> str:
        return v.isoformat() + 'Z' if v.tzinfo is None else v.isoformat()

    @field_serializer('due_date', 'next_occurrence')
    def serialize_utc_optional(self, v: Optional[datetime]) -> Optional[str]:
        if v is None:
            return None
        return v.isoformat() + 'Z' if v.tzinfo is None else v.isoformat()


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

    # Step 5: Advanced task fields
    priority: str = Field(
        default="medium",
        description="Task priority: low, medium, high, or urgent"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task due date (optional)"
    )
    recurrence_rule: Optional[str] = Field(
        None,
        max_length=100,
        description="iCal RRULE format recurrence rule (optional, e.g., 'FREQ=DAILY')"
    )
    reminder_offset: Optional[int] = Field(
        None,
        gt=0,
        description="Minutes before due_date to send reminder (optional, must be positive)"
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

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of the allowed values"""
        allowed_priorities = ["low", "medium", "high", "urgent"]
        if v not in allowed_priorities:
            raise ValueError(
                f"Priority must be one of: {', '.join(allowed_priorities)}"
            )
        return v

    @field_validator("recurrence_rule")
    @classmethod
    def validate_recurrence_rule(cls, v: Optional[str]) -> Optional[str]:
        """Validate RRULE format using RecurrenceService"""
        if v is None:
            return v

        # Strip whitespace
        v = v.strip()
        if not v:
            return None

        # Validate RRULE format
        if not RecurrenceService.validate_rrule(v):
            raise ValueError(
                "Invalid RRULE format. Must be valid iCal recurrence rule "
                "(e.g., 'FREQ=DAILY', 'FREQ=WEEKLY;BYDAY=MO')"
            )

        return v

    @field_validator("reminder_offset")
    @classmethod
    def validate_reminder_offset_with_due_date(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure reminder_offset is only set when due_date is provided"""
        if v is not None and info.data.get("due_date") is None:
            raise ValueError("reminder_offset can only be set when due_date is provided")
        return v


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

    # Step 5: Advanced task fields
    priority: Optional[str] = Field(
        None,
        description="Updated task priority: low, medium, high, or urgent"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Updated task due date"
    )
    recurrence_rule: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated iCal RRULE format recurrence rule"
    )
    reminder_offset: Optional[int] = Field(
        None,
        gt=0,
        description="Updated minutes before due_date to send reminder (must be positive)"
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

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority is one of the allowed values if provided"""
        if v is None:
            return v

        allowed_priorities = ["low", "medium", "high", "urgent"]
        if v not in allowed_priorities:
            raise ValueError(
                f"Priority must be one of: {', '.join(allowed_priorities)}"
            )
        return v

    @field_validator("recurrence_rule")
    @classmethod
    def validate_recurrence_rule(cls, v: Optional[str]) -> Optional[str]:
        """Validate RRULE format using RecurrenceService if provided"""
        if v is None:
            return v

        # Strip whitespace
        v = v.strip()
        if not v:
            return None

        # Validate RRULE format
        if not RecurrenceService.validate_rrule(v):
            raise ValueError(
                "Invalid RRULE format. Must be valid iCal recurrence rule "
                "(e.g., 'FREQ=DAILY', 'FREQ=WEEKLY;BYDAY=MO')"
            )

        return v

    def has_updates(self) -> bool:
        """Check if at least one field is being updated"""
        return (
            self.title is not None
            or self.description is not None
            or self.priority is not None
            or self.due_date is not None
            or self.recurrence_rule is not None
            or self.reminder_offset is not None
        )
