"""
Alert ORM model.

Represents system-generated alerts for students with low attendance,
consecutive absences, or sudden attendance drops.
"""

import enum
import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(str, enum.Enum):
    """Types of attendance alerts."""
    LOW_ATTENDANCE = "LOW_ATTENDANCE"
    CONSECUTIVE_ABSENCES = "CONSECUTIVE_ABSENCES"
    ATTENDANCE_DROP = "ATTENDANCE_DROP"
    BELOW_MINIMUM = "BELOW_MINIMUM"


class Alert(Base):
    """
    System-generated attendance alert.

    Attributes:
        id: Primary key.
        student_id: The student this alert concerns.
        alert_type: Category of alert.
        severity: Alert severity level.
        message: Human-readable alert description.
        is_read: Whether the alert has been acknowledged.
        is_dismissed: Whether the alert has been dismissed.
        created_at: When the alert was generated.
    """

    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    course_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    attendance_pct: Mapped[float | None] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type.value}, severity={self.severity.value})>"
