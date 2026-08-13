"""
Pydantic schemas for user creation, update, and response.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    """User creation schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.STUDENT


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
