"""Event model and schemas for event-driven architecture."""

from datetime import datetime, timezone
from typing import Any, Dict, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


# Event type literals for type safety
EventType = Literal[
    "task.created",
    "task.updated",
    "task.completed",
    "task.deleted",
    "reminder.due"
]


class Event(BaseModel):
    """Base event model for all domain events.

    All events follow a consistent structure with event metadata and a payload.
    Events are published to Kafka topics via Dapr Pub/Sub.

    Attributes:
        event_id: Unique identifier for this event (UUID v4)
        event_type: Type of event (task.created, task.updated, etc.)
        timestamp: When the event was created (ISO 8601 UTC)
        user_id: ID of the user who triggered the event
        payload: Event-specific data (varies by event_type)
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this event"
    )
    event_type: EventType = Field(
        description="Event type identifier"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event was created (ISO 8601 UTC)"
    )
    user_id: int = Field(
        description="ID of the user who triggered the event"
    )
    payload: Dict[str, Any] = Field(
        description="Event-specific data"
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "event_type": "task.created",
                "timestamp": "2026-01-30T15:00:00Z",
                "user_id": 123,
                "payload": {
                    "task_id": 456,
                    "title": "Daily Standup",
                    "priority": "high",
                    "due_date": "2026-01-31T09:00:00Z"
                }
            }
        }


class TaskCreatedEvent(Event):
    """Event published when a task is created."""

    event_type: Literal["task.created"] = "task.created"

    @classmethod
    def create(
        cls,
        user_id: int,
        task_id: int,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: datetime | None = None,
        recurrence_rule: str | None = None,
        reminder_offset: int | None = None
    ) -> "TaskCreatedEvent":
        """Create a task.created event."""
        payload = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
        }
        if due_date:
            payload["due_date"] = due_date.isoformat()
        if recurrence_rule:
            payload["recurrence_rule"] = recurrence_rule
        if reminder_offset:
            payload["reminder_offset"] = reminder_offset

        return cls(user_id=user_id, payload=payload)


class TaskUpdatedEvent(Event):
    """Event published when a task is updated."""

    event_type: Literal["task.updated"] = "task.updated"

    @classmethod
    def create(
        cls,
        user_id: int,
        task_id: int,
        changes: Dict[str, Dict[str, Any]]
    ) -> "TaskUpdatedEvent":
        """Create a task.updated event with change tracking."""
        return cls(
            user_id=user_id,
            payload={
                "task_id": task_id,
                "changes": changes
            }
        )


class TaskCompletedEvent(Event):
    """Event published when a task is marked as complete."""

    event_type: Literal["task.completed"] = "task.completed"

    @classmethod
    def create(
        cls,
        user_id: int,
        task_id: int,
        completed_at: datetime | None = None
    ) -> "TaskCompletedEvent":
        """Create a task.completed event."""
        if completed_at is None:
            completed_at = datetime.now(timezone.utc)

        return cls(
            user_id=user_id,
            payload={
                "task_id": task_id,
                "completed_at": completed_at.isoformat()
            }
        )


class TaskDeletedEvent(Event):
    """Event published when a task is deleted."""

    event_type: Literal["task.deleted"] = "task.deleted"

    @classmethod
    def create(cls, user_id: int, task_id: int) -> "TaskDeletedEvent":
        """Create a task.deleted event."""
        return cls(
            user_id=user_id,
            payload={"task_id": task_id}
        )


class ReminderDueEvent(Event):
    """Event published when a reminder is due."""

    event_type: Literal["reminder.due"] = "reminder.due"

    @classmethod
    def create(
        cls,
        user_id: int,
        reminder_id: int,
        task_id: int,
        task_title: str,
        due_date: datetime,
        reminder_offset: int
    ) -> "ReminderDueEvent":
        """Create a reminder.due event."""
        return cls(
            user_id=user_id,
            payload={
                "reminder_id": reminder_id,
                "task_id": task_id,
                "task_title": task_title,
                "due_date": due_date.isoformat(),
                "reminder_offset": reminder_offset
            }
        )
