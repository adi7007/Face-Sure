"""
Attendance marking, telemetry verification, and reporting API endpoints.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.services.attendance_service import AttendanceService
from app.models.attendance import AttendanceSession, AttendanceRecord, SessionStatus, AttendanceStatus
from app.models.student import Student
from app.models.course import Course

router = APIRouter(prefix="/attendance", tags=["Attendance Processing"])
attendance_service = AttendanceService()


class VerifyFrameRequest(BaseModel):
    """Payload for live webcam frame verification."""
    session_id: Optional[UUID] = Field(default=None, json_schema_extra={"example": "a3b2c1d0-e9f8-a7b6-c5d4-e3f2a1b0c9d8"})
    image_base64: str = Field(..., json_schema_extra={"example": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."})


@router.post("/verify-and-mark", summary="Verify webcam frame and mark attendance")
async def verify_and_mark(
    payload: VerifyFrameRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes Proposed QMF-Score CV pipeline on incoming frame, verifies liveness, quality,
    matches identity, checks duplicate attendance, and records entry in database.
    """
    session_id = payload.session_id
    if not session_id:
        # Pick latest active session or first session
        active_res = await db.execute(
            select(AttendanceSession)
            .where(AttendanceSession.status == SessionStatus.ACTIVE)
            .order_by(AttendanceSession.id.desc())
        )
        active_sess = active_res.scalars().first()
        if active_sess:
            session_id = active_sess.id
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No active attendance session is available; attendance was not recorded.",
            )

    res = await attendance_service.verify_and_mark_attendance(
        db=db,
        session_id=session_id,
        image_base64=payload.image_base64,
    )
    return res


@router.get("/dashboard-summary", summary="Retrieve live dashboard summary metrics")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Computes real-time admin dashboard metrics:
    total students, present count, absent count, attendance percentage, active session, and recent history.
    """
    # Total students
    total_students_res = await db.execute(select(func.count(Student.id)))
    total_students = total_students_res.scalar() or 0

    # Active session
    active_sess_res = await db.execute(
        select(AttendanceSession)
        .options(selectinload(AttendanceSession.course))
        .where(AttendanceSession.status == SessionStatus.ACTIVE)
        .order_by(AttendanceSession.id.desc())
    )
    active_session = active_sess_res.scalars().first()
    active_course = active_session.course if active_session else None

    present_count = 0
    if active_session:
        rec_count_res = await db.execute(
            select(func.count(AttendanceRecord.id)).where(AttendanceRecord.session_id == active_session.id)
        )
        present_count = rec_count_res.scalar() or 0

    absent_count = max(0, total_students - present_count)
    attn_pct = round((present_count / total_students * 100.0), 1) if total_students > 0 else 0.0

    # Recent history
    recent_recs_res = await db.execute(
        select(AttendanceRecord, Student)
        .join(Student, AttendanceRecord.student_id == Student.id)
        .order_by(AttendanceRecord.id.desc())
        .limit(10)
    )
    recent_records = []
    for rec, stu in recent_recs_res.all():
        recent_records.append({
            "id": str(rec.id),
            "student_id": stu.student_id,
            "name": stu.full_name,
            "marked_at": rec.marked_at.isoformat(),
            "status": rec.status.value,
            "confidence": rec.confidence_score,
            "quality": rec.quality_score,
            "liveness": rec.liveness_score,
        })

    return {
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": attn_pct,
        "active_session": {
            "id": str(active_session.id) if active_session else None,
            "course_code": active_course.course_code if active_course else None,
            "course_name": active_course.course_name if active_course else None,
            "status": active_session.status.value if active_session else "NONE",
        },
        "recent_records": recent_records,
    }


class ManualOverrideRequest(BaseModel):
    """Manual attendance override payload."""
    student_id: UUID
    status: str = Field(default="PRESENT", json_schema_extra={"example": "PRESENT"})
    remarks: str = Field(default="Manual override by instructor", min_length=3)


@router.post("/session/{session_id}/manual-override", summary="Manually mark attendance")
async def manual_override(
    session_id: UUID,
    payload: ManualOverrideRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Allow instructor/admin to manually mark attendance for a student.
    Used as fallback when face recognition fails, camera issues, or student has changed appearance.
    """
    from app.models.attendance import AttendanceMethod, AttendanceStatus

    # Validate session exists
    sess_res = await db.execute(
        select(AttendanceSession).where(AttendanceSession.id == session_id)
    )
    session_obj = sess_res.scalars().first()
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    # Validate student exists
    stu_res = await db.execute(
        select(Student).where(Student.id == payload.student_id)
    )
    student_obj = stu_res.scalars().first()
    if not student_obj:
        raise HTTPException(status_code=404, detail=f"Student #{payload.student_id} not found.")

    # Check for existing record
    existing = await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == payload.student_id,
        )
    )
    existing_rec = existing.scalars().first()

    try:
        att_status = AttendanceStatus(payload.status)
    except ValueError:
        att_status = AttendanceStatus.PRESENT

    if existing_rec:
        # Update existing record
        existing_rec.status = att_status
        existing_rec.method = AttendanceMethod.MANUAL_OVERRIDE
        existing_rec.remarks = payload.remarks
        await db.commit()
        return {
            "status": "UPDATED",
            "message": f"Attendance updated to {att_status.value} for {student_obj.full_name}.",
            "record_id": str(existing_rec.id),
        }
    else:
        # Create new manual record
        import uuid
        from datetime import datetime, timezone
        new_record = AttendanceRecord(
            id=uuid.uuid4(),
            student_id=payload.student_id,
            session_id=session_id,
            status=att_status,
            method=AttendanceMethod.MANUAL_OVERRIDE,
            remarks=payload.remarks,
            confidence_score=1.0,
            quality_score=1.0,
            liveness_score=1.0,
            marked_at=datetime.now(timezone.utc),
        )
        db.add(new_record)
        await db.commit()
        return {
            "status": "SUCCESS",
            "message": f"Attendance manually marked {att_status.value} for {student_obj.full_name}.",
            "record_id": str(new_record.id),
        }


@router.get("/session/{session_id}/records", summary="List attendance records for a session")
async def list_session_records(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all attendance records for a specific session with student details."""
    result = await db.execute(
        select(AttendanceRecord, Student)
        .join(Student, AttendanceRecord.student_id == Student.id)
        .where(AttendanceRecord.session_id == session_id)
        .order_by(AttendanceRecord.marked_at.desc())
    )
    records = []
    for rec, stu in result.all():
        records.append({
            "id": str(rec.id),
            "student_id": str(stu.id),
            "student_code": stu.student_id,
            "student_name": stu.full_name,
            "department": stu.department,
            "status": rec.status.value,
            "method": rec.method.value,
            "confidence": rec.confidence_score,
            "quality": rec.quality_score,
            "liveness": rec.liveness_score,
            "marked_at": rec.marked_at.isoformat(),
            "remarks": rec.remarks,
        })
    return {"session_id": str(session_id), "records": records, "count": len(records)}


@router.get("/stats/per-course", summary="Attendance statistics per course")
async def attendance_stats_per_course(
    db: AsyncSession = Depends(get_db),
):
    """Compute attendance statistics grouped by course."""
    from app.models.course import Course

    courses_res = await db.execute(select(Course))
    courses = courses_res.scalars().all()

    stats = []
    for course in courses:
        # Count sessions for this course
        sessions_res = await db.execute(
            select(func.count(AttendanceSession.id)).where(AttendanceSession.course_id == course.id)
        )
        session_count = sessions_res.scalar() or 0

        # Count total records across all sessions of this course
        records_res = await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(AttendanceSession.course_id == course.id)
        )
        total_records = records_res.scalar() or 0

        # Count enrolled students
        from app.models.course import Enrollment
        enrolled_res = await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id)
        )
        enrolled_count = enrolled_res.scalar() or 0

        # Calculate average attendance rate
        if session_count > 0 and enrolled_count > 0:
            avg_attendance = round((total_records / (session_count * enrolled_count)) * 100, 1)
        else:
            avg_attendance = 0.0

        stats.append({
            "course_id": str(course.id),
            "course_code": course.course_code,
            "course_name": course.course_name,
            "department": course.department,
            "session_count": session_count,
            "enrolled_students": enrolled_count,
            "total_records": total_records,
            "avg_attendance_pct": min(avg_attendance, 100.0),
        })

    return {"courses": stats}

