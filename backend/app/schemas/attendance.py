"""
Pydantic schemas for attendance sessions and records.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.attendance import SessionStatus, AttendanceMethod, AttendanceStatus


class SessionCreate(BaseModel):
    """Attendance session creation schema."""

    course_id: UUID
    title: str = Field(..., min_length=2, max_length=150, json_schema_extra={"example": "Lecture 12: ArcFace Geometry"})
    late_threshold_minutes: int = Field(default=15, ge=1, le=120)


class SessionResponse(BaseModel):
    """Attendance session response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    created_by: UUID
    title: str
    status: SessionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    late_threshold_minutes: int
    present_count: int = 0
    late_count: int = 0
    absent_count: int = 0


class AttendanceRecordResponse(BaseModel):
    """Attendance record response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    status: AttendanceStatus
    method: AttendanceMethod
    confidence_score: Optional[float] = None
    marked_at: datetime
    remarks: Optional[str] = None


class ManualOverrideRequest(BaseModel):
    """Manual attendance override request schema."""

    student_id: UUID
    status: AttendanceStatus
    remarks: str = Field(..., min_length=3, max_length=255, json_schema_extra={"example": "Medical excuse presented"})
