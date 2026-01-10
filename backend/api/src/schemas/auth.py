"""Authentication request and response schemas.

Pydantic models for user signup, signin, and authentication responses.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class SignupRequest(BaseModel):
    """Request schema for user signup.

    Attributes:
        email: Valid email address (unique)
        password: Password with minimum 8 characters
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123"
            }
        }


class SigninRequest(BaseModel):
    """Request schema for user signin.

    Attributes:
        email: User's email address
        password: User's password
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123"
            }
        }


class UserResponse(BaseModel):
    """User data in responses (excludes sensitive fields).

    Attributes:
        id: User's unique identifier
        email: User's email address
        created_at: Account creation timestamp
    """

    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow ORM model conversion
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2026-01-08T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Authentication response with user data and JWT token.

    Attributes:
        user: User information (excluding password)
        token: JWT access token for API authentication
    """

    user: UserResponse
    token: str = Field(..., description="JWT access token")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "created_at": "2026-01-08T12:00:00Z"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
