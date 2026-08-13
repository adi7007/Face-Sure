"""
Course and Enrollment ORM models.

Represents academic courses and the many-to-many enrollment relationship
between students and courses.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Course(Base):
    """
    Academic course.

    Attributes:
        id: Primary key.
        code: Unique course code (e.g., 'CS301').
        name: Course name.
        semester: Semester identifier (e.g., 'Fall 2026').
        year: Academic year.
        instructor_id: Foreign key to the instructor's user account.
        created_at: Record creation timestamp.
    """

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instructor: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    sessions: Mapped[list["AttendanceSession"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code='{self.code}', name='{self.name}')>"


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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
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
