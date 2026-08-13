"""
Pydantic schemas package init.
"""

from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.course import CourseCreate, CourseResponse
from app.schemas.attendance import (
    SessionCreate,
    SessionResponse,
    AttendanceRecordResponse,
    ManualOverrideRequest,
)

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserCreate",
    "UserResponse",
    "StudentCreate",
    "StudentResponse",
    "CourseCreate",
    "CourseResponse",
    "SessionCreate",
    "SessionResponse",
    "AttendanceRecordResponse",
    "ManualOverrideRequest",
]
