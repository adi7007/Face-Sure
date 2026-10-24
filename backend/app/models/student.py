"""
Student ORM model.

Represents a student enrolled in the system. Each student is linked to a User
account and can have multiple face embeddings for recognition.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.face_embedding import FaceEmbedding
    from app.models.course import Enrollment
    from app.models.attendance import AttendanceRecord


class Student(Base):
    """
    Student profile linked to a user account.

    Attributes:
        id: Primary key.
        student_id: Unique institutional student ID / Roll number.
        full_name: Display name.
        email: Unique email.
        department: Academic department.
        academic_year: Academic year of study.
        is_active: Whether the student profile is active.
        user_id: Foreign key to the user account (nullable).
        created_at: Record creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "students"

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True
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
    user: Mapped["User"] = relationship(back_populates="student")  # noqa: F821
    face_embeddings: Mapped[list["FaceEmbedding"]] = relationship(  # noqa: F821
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(  # noqa: F821
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(  # noqa: F821
        back_populates="student", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id='{self.student_id}', dept='{self.department}')>"
