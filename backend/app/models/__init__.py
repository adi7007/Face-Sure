"""
ORM models package.

Imports all models so that SQLAlchemy and Alembic can discover them.
"""

from app.models.user import User, UserRole
from app.models.student import Student
from app.models.course import Course, Enrollment
from app.models.attendance import (
    AttendanceSession,
    AttendanceRecord,
    SessionStatus,
    AttendanceMethod,
    AttendanceStatus,
)
from app.models.face_embedding import FaceEmbedding
from app.models.audit_log import AuditLog
from app.models.alert import Alert, AlertSeverity, AlertType

__all__ = [
    "User",
    "UserRole",
    "Student",
    "Course",
    "Enrollment",
    "AttendanceSession",
    "AttendanceRecord",
    "SessionStatus",
    "AttendanceMethod",
    "AttendanceStatus",
    "FaceEmbedding",
    "AuditLog",
    "Alert",
    "AlertSeverity",
    "AlertType",
]
