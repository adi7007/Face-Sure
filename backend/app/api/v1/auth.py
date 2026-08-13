"""
Authentication API endpoints (Login, Refresh, Current User Info).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user with username or email and return JWT access token."""
    # Find user by username or email
    stmt = select(User).where(
        (User.email == payload.username_or_email) | (User.username == payload.username_or_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Invalid username/email or password")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    # Create access token
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        extra_claims={"email": user.email, "name": user.full_name},
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes
        user_id=str(user.id),
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user
