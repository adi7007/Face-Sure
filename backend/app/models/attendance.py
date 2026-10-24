"""
Attendance ORM models.

Represents attendance sessions (class meetings) and individual attendance records
(a student being marked present in a session).
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint, UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User
    from app.models.student import Student


class SessionStatus(str, enum.Enum):
    """Attendance session lifecycle status."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AttendanceMethod(str, enum.Enum):
    """How attendance was recorded."""

    FACE_RECOGNITION = "FACE_RECOGNITION"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"


class AttendanceStatus(str, enum.Enum):
    """Attendance record status."""

    PRESENT = "PRESENT"
    LATE = "LATE"
    ABSENT = "ABSENT"
    EXCUSED = "EXCUSED"


class AttendanceSession(Base):
    """
    An attendance session represents a single class meeting.

    Instructors create sessions for their courses, and the system
    records attendance against these sessions.

    Attributes:
        id: Primary key.
        course_id: The course this session belongs to.
        created_by: The instructor who created the session.
        title: Session title.
        status: Session lifecycle status.
        start_time: When the session starts.
        end_time: When the session ends.
        late_threshold_minutes: Late threshold.
        created_at: Record creation timestamp.
    """

    __tablename__ = "attendance_sessions"

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.ACTIVE
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    late_threshold_minutes: Mapped[int] = mapped_column(default=15, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="sessions")  # noqa: F821
    instructor: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<AttendanceSession(id={self.id}, course_id={self.course_id}, "
            f"title='{self.title}', status={self.status.value})>"
        )


class AttendanceRecord(Base):
    """
    Individual attendance record — one student marked in one session.

    Stores recognition metadata (confidence scores, quality, liveness)
    for audit and research purposes.

    Attributes:
        id: Primary key.
        student_id: The student being marked.
        session_id: The session this record belongs to.
        status: Attendance status (present, late, absent, excused).
        method: How attendance was recorded (facial recognition or manual).
        confidence_score: Face recognition confidence score (0.0–1.0).
        marked_at: When attendance was marked.
        marked_by: Who marked this attendance.
        remarks: Optional remarks (e.g., manual override reason).
        quality_score: Face quality assessment score (0.0–1.0).
        liveness_score: Liveness detection score (0.0–1.0).
        image_hash: SHA-256 hash of the captured image for audit trail.
        created_at: Record creation timestamp.
    """

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("student_id", "session_id", name="uq_session_student"),
    )

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus), default=AttendanceStatus.PRESENT
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(AttendanceMethod), default=AttendanceMethod.FACE_RECOGNITION
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    marked_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Telemetry and audit
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    liveness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="attendance_records")  # noqa: F821
    session: Mapped["AttendanceSession"] = relationship(back_populates="records")

    def __repr__(self) -> str:
        return (
            f"<AttendanceRecord(id={self.id}, student_id={self.student_id}, "
            f"session_id={self.session_id}, status={self.status.value})>"
        )
