"""FastAPI dependencies for authentication and database access.

Provides reusable dependencies for JWT verification and database sessions.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlmodel import Session
from typing import Dict

from ..config import settings
from ..db.session import get_session


# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, any]:
    """Verify JWT token and extract user information.

    This dependency verifies the JWT token from the Authorization header
    and returns the authenticated user's information.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        Dict with user_id and email from the JWT payload

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Example:
        @app.get("/api/{user_id}/tasks")
        def get_tasks(
            user_id: int,
            current_user: dict = Depends(get_current_user)
        ):
            # Verify user_id matches authenticated user
            if current_user["user_id"] != user_id:
                raise HTTPException(status_code=403)
            ...
    """
    token = credentials.credentials

    try:
        # Decode and verify JWT signature
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user_id from 'sub' claim
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        # Extract email
        email: str | None = payload.get("email")

        return {
            "user_id": int(user_id),
            "email": email
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except ValueError as e:
        # Handle invalid user_id format
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed user ID"
        ) from e


def verify_user_access(
    user_id: int,
    current_user: Dict[str, any] = Depends(get_current_user)
) -> Dict[str, any]:
    """Verify that the authenticated user matches the user_id in the URL.

    This dependency ensures users can only access their own resources.

    Args:
        user_id: User ID from URL path parameter
        current_user: Authenticated user from get_current_user dependency

    Returns:
        The current_user dict if user_id matches

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user

    Example:
        @app.get("/api/{user_id}/tasks")
        def get_tasks(
            user_id: int,
            current_user: dict = Depends(verify_user_access)
        ):
            # user_id is guaranteed to match current_user["user_id"]
            ...
    """
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's resources"
        )
    return current_user


__all__ = ["get_session", "get_current_user", "verify_user_access", "security"]
