"""
Attendance sessions management API endpoints.
"""

from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.course import Course
from app.models.attendance import AttendanceSession, SessionStatus
from app.schemas.attendance import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["Attendance Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED, summary="Create new session")
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin/Instructor creates a new attendance session for a course."""
    new_session = AttendanceSession(
        course_id=payload.course_id,
        created_by=current_user.id,
        title=payload.title,
        status=SessionStatus.ACTIVE,
        late_threshold_minutes=payload.late_threshold_minutes,
        start_time=datetime.now(timezone.utc),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.get("", response_model=List[SessionResponse], summary="List sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all attendance sessions."""
    result = await db.execute(
        select(AttendanceSession).order_by(AttendanceSession.id.desc())
    )
    return result.scalars().all()


@router.post("/{session_id}/stop", summary="Stop active attendance session")
async def stop_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop/complete an active attendance session."""
    result = await db.execute(
        select(AttendanceSession).where(AttendanceSession.id == session_id)
    )
    session_obj = result.scalars().first()
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    session_obj.status = SessionStatus.COMPLETED
    session_obj.end_time = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "success", "message": f"Session #{session_id} closed.", "session_id": session_id}
