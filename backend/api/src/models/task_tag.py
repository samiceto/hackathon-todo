"""TaskTag model for many-to-many relationship between tasks and tags."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskTag(SQLModel, table=True):
    """Task tag model for categorizing tasks.

    Represents a many-to-many relationship between tasks and tags.
    Each task can have multiple tags (max 10), and each tag can be associated with multiple tasks.

    Attributes:
        id: Unique identifier for the task-tag association
        task_id: ID of the task this tag is associated with
        tag_name: Name of the tag (e.g., "work", "urgent", "q1-goals")
        created_at: When this tag was added to the task
    """

    __tablename__ = "task_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    tag_name: str = Field(max_length=50, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_id": 123,
                "tag_name": "work",
                "created_at": "2026-01-30T15:00:00Z"
            }
        }
