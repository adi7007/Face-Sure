"""
Reports & CSV Export API Endpoints.
"""

import csv
import io
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.student import Student

router = APIRouter(prefix="/reports", tags=["Reports & Export"])


@router.get("/export-csv", summary="Export Attendance Records to CSV")
async def export_attendance_csv(
    session_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate downloadable CSV report of attendance records with telemetry.
    """
    query = select(AttendanceRecord, Student, AttendanceSession).join(
        Student, AttendanceRecord.student_id == Student.id
    ).join(
        AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id
    )

    if session_id:
        query = query.where(AttendanceRecord.session_id == session_id)

    result = await db.execute(query.order_by(AttendanceRecord.id.desc()))
    records = result.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header Row
    writer.writerow([
        "Record ID",
        "Student ID",
        "Student Name",
        "Department",
        "Session ID",
        "Date & Time (UTC)",
        "Recognition Confidence (S)",
        "Quality Score (Q)",
        "Liveness Score (L)",
        "Attendance Status",
        "Method",
    ])

    for rec, stu, sess in records:
        writer.writerow([
            rec.id,
            stu.student_id,
            stu.full_name,
            stu.department,
            sess.id,
            rec.marked_at.strftime("%Y-%m-%d %H:%M:%S"),
            f"{rec.confidence_score:.3f}" if rec.confidence_score else "N/A",
            f"{rec.quality_score:.3f}" if rec.quality_score else "N/A",
            f"{rec.liveness_score:.3f}" if rec.liveness_score else "N/A",
            rec.status.value,
            rec.method.value,
        ])

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"},
    )
