"""Task model for todo items.

Represents a todo task with title, description, completion status, and user ownership.
Extended in Step 5 with priority, due dates, recurrence rules, and reminders.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Literal
from enum import Enum

if TYPE_CHECKING:
    from .user import User


# Step 5: Priority levels for task categorization
class PriorityLevel(str, Enum):
    """Task priority levels.

    Values:
        LOW: Low priority task
        MEDIUM: Medium priority task (default)
        HIGH: High priority task
        URGENT: Urgent priority task
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """Task model for todo items.

    Attributes:
        id: Unique task identifier (auto-generated)
        user_id: Foreign key to user who owns this task (indexed for filtering)
        title: Task title (required, 1-500 characters)
        description: Task description (optional, max 5000 characters)
        completed: Completion status (default: False)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        priority: Task priority level (Step 5, default: medium)
        due_date: Task due date (Step 5, optional)
        recurrence_rule: iCal RRULE format recurrence rule (Step 5, optional)
        reminder_offset: Minutes before due_date to send reminder (Step 5, optional)
        next_occurrence: Next occurrence time for recurring tasks (Step 5, optional)
        user: Relationship to task owner
    """

    __tablename__ = "tasks"

    # Core fields (Step 1-2)
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Advanced fields (Step 5)
    priority: str = Field(default="medium", max_length=20)  # Stored as VARCHAR for DB compatibility
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None, max_length=100)
    reminder_offset: Optional[int] = Field(default=None, gt=0)  # Must be positive
    next_occurrence: Optional[datetime] = Field(default=None)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Complete Step 5",
                "description": "Implement advanced cloud deployment",
                "completed": False,
                "priority": "high",
                "due_date": "2026-02-01T09:00:00Z",
                "recurrence_rule": "FREQ=DAILY",
                "reminder_offset": 30,
                "created_at": "2026-01-08T12:00:00Z",
                "updated_at": "2026-01-08T12:00:00Z"
            }
        }
