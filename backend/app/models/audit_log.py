"""
AuditLog ORM model.

Immutable audit trail for all security-sensitive and recognition events.
Used for compliance, debugging, and the research paper's data analysis.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """
    Immutable audit log entry.

    Records all significant system events including:
    - Authentication events (login, logout, failed attempts)
    - Face recognition attempts (success, failure, spoof detected)
    - Data modifications (student CRUD, attendance changes)
    - Administrative actions

    Attributes:
        id: Primary key.
        timestamp: When the event occurred.
        action: Event type (e.g., 'login', 'recognition_attempt', 'student_created').
        user_id: The user who triggered the event (null for system events).
        ip_address: Client IP address.
        user_agent: Client user agent string.
        resource_type: Type of resource affected (e.g., 'student', 'attendance').
        resource_id: ID of the affected resource.
        details: JSON object with event-specific metadata.
        status: Outcome ('success', 'failure', 'error').
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"user_id={self.user_id}, status='{self.status}')>"
        )
