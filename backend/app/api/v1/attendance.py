"""
Attendance records and manual override API endpoints.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.models.attendance import AttendanceRecord, AttendanceMethod
from app.schemas.attendance import AttendanceRecordResponse, ManualOverrideRequest

router = APIRouter(prefix="/attendance", tags=["Attendance Records"])


@router.get("/session/{session_id}", response_model=List[AttendanceRecordResponse], status_code=status.HTTP_200_OK)
async def get_session_attendance(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all attendance records for a specific session."""
    stmt = select(AttendanceRecord).where(AttendanceRecord.session_id == session_id)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return records


@router.post("/session/{session_id}/override", response_model=AttendanceRecordResponse, status_code=status.HTTP_200_OK)
async def manual_override(
    session_id: UUID,
    payload: ManualOverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually create or override student attendance status."""
    stmt = select(AttendanceRecord).where(
        (AttendanceRecord.session_id == session_id) & (AttendanceRecord.student_id == payload.student_id)
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record:
        record.status = payload.status
        record.method = AttendanceMethod.MANUAL_OVERRIDE
        record.marked_by = current_user.id
        record.remarks = payload.remarks
        record.marked_at = datetime.now(timezone.utc)
    else:
        record = AttendanceRecord(
            session_id=session_id,
            student_id=payload.student_id,
            status=payload.status,
            method=AttendanceMethod.MANUAL_OVERRIDE,
            marked_by=current_user.id,
            remarks=payload.remarks,
            marked_at=datetime.now(timezone.utc),
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record
