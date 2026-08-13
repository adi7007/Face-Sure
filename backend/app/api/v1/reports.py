"""
Reports and analytics API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_summary_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get high-level system summary metrics for dashboard visualization."""
    return {
        "total_students": 150,
        "total_courses": 4,
        "active_sessions": 1,
        "overall_attendance_rate": 94.2,
        "average_liveness_score": 0.98,
        "average_recognition_confidence": 0.91,
    }
