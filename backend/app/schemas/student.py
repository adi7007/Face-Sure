"""
Pydantic schemas for student profile management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    """Student creation schema."""

    student_id: str = Field(..., min_length=2, max_length=50, example="STU-2026-001")
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    department: str = Field(..., example="Computer Science & Engineering")
    academic_year: str = Field(..., example="4th Year")


class StudentResponse(BaseModel):
    """Student response schema."""

    id: UUID
    student_id: str
    full_name: str
    email: EmailStr
    department: str
    academic_year: str
    is_active: bool
    user_id: Optional[UUID] = None
    embedding_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
