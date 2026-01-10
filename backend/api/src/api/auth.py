"""Authentication API endpoints.

Public endpoints for user signup and signin.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db.session import get_session
from ..models.user import User
from ..schemas.auth import SignupRequest, SigninRequest, AuthResponse, UserResponse
from ..services.auth import hash_password, verify_password, create_access_token


router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """Create a new user account.

    Args:
        signup_data: User email and password
        session: Database session

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Invalid email or password format
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == signup_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(signup_data.password)

    # Create new user
    new_user = User(
        email=signup_data.email,
        hashed_password=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    token = create_access_token(
        user_id=new_user.id,
        email=new_user.email
    )

    # Return user data and token
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        token=token
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    signin_data: SigninRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """Sign in an existing user.

    Args:
        signin_data: User email and password
        session: Database session

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 401: Invalid email or password
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == signin_data.email)
    ).first()

    # Verify user exists and password is correct
    if not user or not verify_password(signin_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    # Return user data and token
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token
    )
