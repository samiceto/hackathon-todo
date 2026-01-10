"""User model for authentication and task ownership.

Represents a user account with email, password, and timestamp tracking.
"""
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """User account model.

    Attributes:
        id: Unique user identifier (auto-generated)
        email: User's email address (unique, indexed)
        hashed_password: Bcrypt-hashed password (never return in API responses)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        tasks: Relationship to user's tasks (cascade delete)
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255, sa_column_kwargs={"unique": True})
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks (cascade delete: when user deleted, all tasks deleted)
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "$2b$12$...",  # Bcrypt hash
                "created_at": "2026-01-08T12:00:00Z",
                "updated_at": "2026-01-08T12:00:00Z"
            }
        }
