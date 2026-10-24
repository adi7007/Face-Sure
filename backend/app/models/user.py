"""
User ORM model.

Represents system users who can authenticate and access the application.
Each user has a role (admin, instructor, student) that determines their permissions.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, String, UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.student import Student


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""

    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    STUDENT = "STUDENT"


class User(Base):
    """
    System user account.

    Attributes:
        id: Primary key.
        email: Unique email address used for login.
        username: Unique username.
        hashed_password: Bcrypt-hashed password.
        full_name: Display name.
        role: Authorization role (admin, instructor, student).
        is_active: Whether the account is enabled.
        created_at: Account creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.STUDENT
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    student: Mapped["Student"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"
