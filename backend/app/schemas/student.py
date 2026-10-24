"""
Pydantic schemas for student profile management.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StudentCreate(BaseModel):
    """Student creation schema."""

    student_id: str = Field(..., min_length=2, max_length=50, json_schema_extra={"example": "STU-2026-001"})
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    department: str = Field(..., json_schema_extra={"example": "Computer Science & Engineering"})
    academic_year: str = Field(..., json_schema_extra={"example": "4th Year"})
    photos_base64: Optional[List[str]] = Field(
        default=None, min_length=1, max_length=5,
        description="Optional base64 encoded face images for enrollment",
    )

    @field_validator("student_id")
    @classmethod
    def normalize_student_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Student ID is required")
        return normalized

    @field_validator("full_name", "department", "academic_year")
    @classmethod
    def reject_blank_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required")
        return normalized


class StudentUpdate(BaseModel):
    """Student update schema."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    academic_year: Optional[str] = None
    is_active: Optional[bool] = None


class EnrollPhotoRequest(BaseModel):
    """Photo enrollment payload."""

    photo_base64: str = Field(..., description="Base64 encoded JPEG/PNG face image")
    angle: Optional[str] = Field(default="Front", description="Angle or pose tag (e.g. Front, Left, Right)")


class StudentResponse(BaseModel):
    """Student response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: str
    full_name: str
    email: str
    department: str
    academic_year: str
    is_active: bool
    user_id: Optional[UUID] = None
    embedding_count: int = 0
    created_at: datetime
    photo_url: Optional[str] = None
