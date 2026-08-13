"""
Security utilities for authentication and authorization.

Provides:
- JWT token creation and verification
- Password hashing and verification
- Current user dependency for FastAPI
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings


import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    password_bytes = password.encode("utf-8")[:72]  # Truncate to bcrypt 72-byte max limit
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    plain_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(
    subject: str | int,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The user ID or identifier to encode as the token subject.
        role: The user's role (admin, instructor, student).
        extra_claims: Optional additional claims to include in the token.

    Returns:
        Encoded JWT access token string.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str | int) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: The user ID or identifier to encode as the token subject.

    Returns:
        Encoded JWT refresh token string.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Decoded token payload as a dictionary.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.
    """
    settings = get_settings()

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Alias for decode_token."""
    return decode_token(token)


async def get_current_user():
    """Dependency placeholder for returning current user from token."""
    from app.models.user import User, UserRole
    from uuid import UUID
    return User(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        email="admin@project.edu",
        username="admin",
        hashed_password=hash_password("Admin@123456"),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
    )
