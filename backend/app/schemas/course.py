"""
Pydantic schemas for course and enrollment management.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    """Course creation schema."""

    course_code: str = Field(..., min_length=2, max_length=50, json_schema_extra={"example": "CS-401"})
    course_name: str = Field(..., min_length=2, max_length=150, json_schema_extra={"example": "Deep Learning & Computer Vision"})
    department: str = Field(..., json_schema_extra={"example": "Computer Science & Engineering"})
    instructor_id: UUID


class CourseResponse(BaseModel):
    """Course response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_code: str
    course_name: str
    department: str
    instructor_id: UUID
    enrolled_students_count: int = 0
    created_at: datetime
