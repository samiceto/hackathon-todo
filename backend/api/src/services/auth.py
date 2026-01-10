"""Authentication service for user management and JWT operations.

Handles password hashing, JWT token creation, and user authentication.
"""
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

from ..config import settings


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> hashed.startswith("$2b$")
        True
    """
    # Convert password to bytes and hash with bcrypt (12 rounds by default)
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string (decoded from bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    # Convert both to bytes for bcrypt verification
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for a user.

    Args:
        user_id: User's unique identifier
        email: User's email address
        expires_delta: Optional custom expiration time (defaults to 7 days)

    Returns:
        JWT token string

    Example:
        >>> token = create_access_token(user_id=1, email="user@example.com")
        >>> len(token) > 100
        True
    """
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)

    # Create JWT payload
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at time
    }

    # Encode and sign JWT
    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token
