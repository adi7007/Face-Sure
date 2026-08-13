"""
Attendance ORM models.

Represents attendance sessions (class meetings) and individual attendance records
(a student being marked present in a session).
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    """Attendance session lifecycle status."""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendanceMethod(str, enum.Enum):
    """How attendance was recorded."""

    FACIAL_RECOGNITION = "facial_recognition"
    MANUAL = "manual"


class AttendanceStatus(str, enum.Enum):
    """Attendance record status."""

    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"


class AttendanceSession(Base):
    """
    An attendance session represents a single class meeting.

    Instructors create sessions for their courses, and the system
    records attendance against these sessions.

    Attributes:
        id: Primary key.
        course_id: The course this session belongs to.
        instructor_id: The instructor who created the session.
        date: Session date.
        start_time: When the session starts (or was started).
        end_time: When the session ends (or was ended).
        status: Session lifecycle status.
        notes: Optional notes about the session.
        created_at: Record creation timestamp.
    """

    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.SCHEDULED
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
            f"date={self.date}, status={self.status.value})>"
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
        marked_at: When attendance was marked.
        confidence: Face recognition confidence score (0.0–1.0).
        quality_score: Face quality assessment score (0.0–1.0).
        liveness_score: Liveness detection score (0.0–1.0).
        method: How attendance was recorded (facial recognition or manual).
        status: Attendance status (present, late, absent, excused).
        image_hash: SHA-256 hash of the captured image for audit trail.
        notes: Optional notes (e.g., manual override reason).
        created_at: Record creation timestamp.
    """

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("student_id", "session_id", name="uq_student_session"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    liveness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(AttendanceMethod), default=AttendanceMethod.FACIAL_RECOGNITION
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus), default=AttendanceStatus.PRESENT
    )
    image_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
