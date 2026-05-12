"""Reminder model for task reminder notifications."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    """Reminder model for scheduled task notifications.

    Stores reminder records created when tasks have due dates with reminder offsets.
    The reminder service processes these records and publishes reminder.due events.

    Attributes:
        id: Unique identifier for the reminder
        task_id: ID of the task this reminder is for
        user_id: ID of the user who owns the task
        reminder_at: When the reminder should be sent (due_date - reminder_offset)
        sent: Whether the reminder has been sent
        created_at: When this reminder record was created
    """

    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    reminder_at: datetime = Field(nullable=False, index=True)
    sent: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_id": 456,
                "user_id": 123,
                "reminder_at": "2026-01-31T08:30:00Z",
                "sent": False,
                "created_at": "2026-01-30T15:00:00Z"
            }
        }
