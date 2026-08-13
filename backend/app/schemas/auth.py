"""
Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    """User login request schema."""

    username_or_email: str = Field(..., json_schema_extra={"example": "admin@project.edu"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "Admin@123456"})


class TokenResponse(BaseModel):
    """JWT Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds
    user_id: str
    role: UserRole
    full_name: str


class RefreshTokenRequest(BaseModel):
    """Token refresh request schema."""

    refresh_token: str
