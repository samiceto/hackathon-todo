"""Task model for todo items.

Represents a todo task with title, description, completion status, and user ownership.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


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
        user: Relationship to task owner
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Complete Step 2",
                "description": "Build full-stack web app",
                "completed": False,
                "created_at": "2026-01-08T12:00:00Z",
                "updated_at": "2026-01-08T12:00:00Z"
            }
        }
