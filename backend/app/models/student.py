"""
Student ORM model.

Represents a student enrolled in the system. Each student is linked to a User
account and can have multiple face embeddings for recognition.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
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
        user_id: Foreign key to the user account.
        roll_number: Unique institutional roll number / student ID.
        department: Academic department.
        year: Current year of study.
        section: Class section.
        is_face_registered: Whether the student has enrolled face data.
        created_at: Record creation timestamp.
    """

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    roll_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=True)
    is_face_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
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
        back_populates="student", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, roll='{self.roll_number}', dept='{self.department}')>"
