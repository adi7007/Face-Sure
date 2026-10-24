"""
Course and Enrollment ORM models.

Represents academic courses and the many-to-many enrollment relationship
between students and courses.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.attendance import AttendanceSession
    from app.models.student import Student


class Course(Base):
    """
    Academic course.

    Attributes:
        id: Primary key.
        course_code: Unique course code (e.g., 'CS-401').
        course_name: Course name.
        department: Academic department.
        instructor_id: Foreign key to the instructor's user account.
        created_at: Record creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    course_name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    instructor_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    instructor: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    sessions: Mapped[list["AttendanceSession"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, course_code='{self.course_code}', course_name='{self.course_name}')>"


class Enrollment(Base):
    """
    Student-Course enrollment (many-to-many junction table).

    Attributes:
        id: Primary key.
        student_id: Foreign key to the student.
        course_id: Foreign key to the course.
        enrolled_at: Enrollment timestamp.
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="enrollments")  # noqa: F821
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<Enrollment(student_id={self.student_id}, course_id={self.course_id})>"
