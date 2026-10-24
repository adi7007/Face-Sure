"""
Student Portal API Endpoints.

Provides self-service endpoints for students to view their own
attendance data, courses, and alerts.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.student import Student
from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceStatus
from app.models.course import Course, Enrollment
from app.models.alert import Alert

router = APIRouter(prefix="/portal", tags=["Student Portal"])


@router.get("/my-attendance/{student_id}", summary="Student's attendance history")
async def my_attendance(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a student's complete attendance history across all courses."""
    # Verify student exists
    stu_res = await db.execute(select(Student).where(Student.id == student_id))
    student = stu_res.scalars().first()
    if not student:
        return {"error": "Student not found"}

    # Get all attendance records for this student
    records_res = await db.execute(
        select(AttendanceRecord, AttendanceSession, Course)
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .join(Course, AttendanceSession.course_id == Course.id)
        .where(AttendanceRecord.student_id == student_id)
        .order_by(AttendanceRecord.marked_at.desc())
    )

    records = []
    for rec, sess, course in records_res.all():
        records.append({
            "id": str(rec.id),
            "course_code": course.course_code,
            "course_name": course.course_name,
            "session_title": sess.title,
            "status": rec.status.value,
            "method": rec.method.value,
            "marked_at": rec.marked_at.isoformat(),
            "confidence": rec.confidence_score,
        })

    # Compute overall stats
    total_res = await db.execute(select(func.count(AttendanceSession.id)))
    total_sessions = total_res.scalar() or 1
    attended = len(records)
    overall_pct = round((attended / total_sessions) * 100, 1) if total_sessions > 0 else 0.0

    return {
        "student": {
            "id": str(student.id),
            "student_code": student.student_id,
            "full_name": student.full_name,
            "department": student.department,
        },
        "overall_attendance_pct": min(overall_pct, 100.0),
        "sessions_attended": attended,
        "total_sessions": total_sessions,
        "records": records,
    }


@router.get("/my-courses/{student_id}", summary="Student's enrolled courses")
async def my_courses(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get student's enrolled courses with per-course attendance percentages."""
    # Get enrolled courses
    enrollments_res = await db.execute(
        select(Enrollment, Course)
        .join(Course, Enrollment.course_id == Course.id)
        .where(Enrollment.student_id == student_id)
    )

    courses = []
    for enrollment, course in enrollments_res.all():
        # Count sessions for this course
        sess_count_res = await db.execute(
            select(func.count(AttendanceSession.id))
            .where(AttendanceSession.course_id == course.id)
        )
        session_count = sess_count_res.scalar() or 0

        # Count attended sessions
        attended_res = await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.course_id == course.id,
                AttendanceRecord.student_id == student_id,
            )
        )
        attended = attended_res.scalar() or 0
        pct = round((attended / session_count) * 100, 1) if session_count > 0 else 0.0

        courses.append({
            "course_id": str(course.id),
            "course_code": course.course_code,
            "course_name": course.course_name,
            "department": course.department,
            "sessions_total": session_count,
            "sessions_attended": attended,
            "attendance_pct": min(pct, 100.0),
            "enrolled_at": enrollment.enrolled_at.isoformat(),
        })

    return {"courses": courses}


@router.get("/my-alerts/{student_id}", summary="Student's alerts")
async def my_alerts(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get active alerts for a specific student."""
    alerts_res = await db.execute(
        select(Alert)
        .where(Alert.student_id == student_id, Alert.is_dismissed == False)
        .order_by(Alert.created_at.desc())
    )
    alerts = alerts_res.scalars().all()

    return {
        "count": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "type": a.alert_type.value,
                "severity": a.severity.value,
                "message": a.message,
                "course_code": a.course_code,
                "attendance_pct": a.attendance_pct,
                "is_read": a.is_read,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
    }


@router.put("/alerts/{alert_id}/read", summary="Mark alert as read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Mark an alert as read."""
    alert_res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = alert_res.scalars().first()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_read = True
    await db.commit()
    return {"status": "ok"}
