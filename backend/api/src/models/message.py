"""Message model for conversation messages.

Represents individual messages within a conversation between user and AI assistant.
Step 3: AI-Powered Chatbot - Conversational Database Models
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message role enumeration.

    Defines who sent the message in the conversation.
    """
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message model for conversation messages.

    Represents a single message within a conversation thread.
    Messages are ordered chronologically within each conversation.

    Attributes:
        id: Unique message identifier (auto-generated)
        user_id: Foreign key to user who owns this conversation (indexed for filtering)
        conversation_id: Foreign key to conversation this message belongs to (indexed)
        role: Message sender role (user or assistant)
        content: Message text content (max 10000 characters)
        created_at: Message creation timestamp
        user: Relationship to message owner
        conversation: Relationship to parent conversation
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"nullable": False})
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="messages")
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-01-11T10:00:00Z"
            }
        }
