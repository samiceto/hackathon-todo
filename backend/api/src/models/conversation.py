"""Conversation model for AI chatbot interactions.

Represents a conversation thread between a user and the AI assistant.
Step 3: AI-Powered Chatbot - Conversational Database Models
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation model for AI chatbot.

    Represents a conversation thread containing multiple messages between user and AI.
    Each conversation belongs to a single user and maintains conversation context.

    Attributes:
        id: Unique conversation identifier (auto-generated)
        user_id: Foreign key to user who owns this conversation (indexed for filtering)
        created_at: Conversation creation timestamp
        updated_at: Last update timestamp
        user: Relationship to conversation owner
        messages: Relationship to messages in this conversation (cascade delete)
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
        sa_relationship_kwargs={"order_by": "Message.created_at"}
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "created_at": "2026-01-11T10:00:00Z",
                "updated_at": "2026-01-11T10:30:00Z"
            }
        }
