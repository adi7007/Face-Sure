"""
Analytics API Endpoints.

Provides deep attendance analytics including daily trends,
per-course stats, at-risk student detection, and attendance prediction.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
analytics_service = AnalyticsService()


@router.get("/daily", summary="Daily attendance trend")
async def daily_attendance_trend(
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
):
    """Get day-by-day attendance counts for trend visualization."""
    data = await analytics_service.compute_daily_attendance(db, days=days)
    return {"days": days, "trend": data}


@router.get("/at-risk", summary="At-risk students")
async def at_risk_students(
    threshold: float = Query(default=75.0, ge=10.0, le=100.0, description="Attendance % threshold"),
    db: AsyncSession = Depends(get_db),
):
    """Identify students below the attendance threshold."""
    students = await analytics_service.compute_at_risk_students(db, threshold=threshold)
    return {
        "threshold": threshold,
        "count": len(students),
        "students": students,
    }


@router.get("/prediction/{student_id}", summary="Attendance prediction")
async def attendance_prediction(
    student_id: UUID,
    remaining_sessions: int = Query(default=20, ge=1, le=100),
    required_pct: float = Query(default=75.0, ge=10.0, le=100.0),
    db: AsyncSession = Depends(get_db),
):
    """Predict how many classes a student needs to attend to meet minimum requirements."""
    prediction = await analytics_service.predict_attendance(
        db,
        student_id=student_id,
        remaining_sessions=remaining_sessions,
        required_pct=required_pct,
    )
    return prediction


@router.get("/overview", summary="System-wide analytics overview")
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
):
    """
    Comprehensive analytics overview with key metrics.
    Used by the AnalyticsPage frontend.
    """
    from sqlalchemy import select, func
    from app.models.student import Student
    from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceStatus
    from app.models.course import Course

    # Total counts
    total_students_res = await db.execute(select(func.count(Student.id)).where(Student.is_active == True))
    total_students = total_students_res.scalar() or 0

    total_sessions_res = await db.execute(select(func.count(AttendanceSession.id)))
    total_sessions = total_sessions_res.scalar() or 0

    total_records_res = await db.execute(select(func.count(AttendanceRecord.id)))
    total_records = total_records_res.scalar() or 0

    total_courses_res = await db.execute(select(func.count(Course.id)))
    total_courses = total_courses_res.scalar() or 0

    # Status breakdown
    present_res = await db.execute(
        select(func.count(AttendanceRecord.id)).where(AttendanceRecord.status == AttendanceStatus.PRESENT)
    )
    present_count = present_res.scalar() or 0

    late_res = await db.execute(
        select(func.count(AttendanceRecord.id)).where(AttendanceRecord.status == AttendanceStatus.LATE)
    )
    late_count = late_res.scalar() or 0

    # Overall attendance rate
    avg_rate = round((total_records / (total_sessions * total_students)) * 100, 1) if total_sessions > 0 and total_students > 0 else 0.0

    # At-risk count
    at_risk = await analytics_service.compute_at_risk_students(db, threshold=75.0)

    # Daily trend (last 14 days for overview)
    daily = await analytics_service.compute_daily_attendance(db, days=14)

    return {
        "total_students": total_students,
        "total_sessions": total_sessions,
        "total_records": total_records,
        "total_courses": total_courses,
        "present_count": present_count,
        "late_count": late_count,
        "overall_attendance_rate": min(avg_rate, 100.0),
        "at_risk_count": len(at_risk),
        "at_risk_students": at_risk[:5],  # Top 5 most at-risk
        "daily_trend": daily,
    }
