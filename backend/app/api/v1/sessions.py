"""
Attendance session management API endpoints (Create, List, Close).
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
from app.models.attendance import AttendanceSession, SessionStatus
from app.schemas.attendance import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["Attendance Sessions"])


@router.get("", response_model=List[SessionResponse], status_code=status.HTTP_200_OK)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List attendance sessions."""
    stmt = select(AttendanceSession).order_by(AttendanceSession.created_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return sessions


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new active attendance session."""
    session = AttendanceSession(
        course_id=payload.course_id,
        created_by=current_user.id,
        title=payload.title,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(timezone.utc),
        late_threshold_minutes=payload.late_threshold_minutes,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/{session_id}/close", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def close_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close an active attendance session."""
    stmt = select(AttendanceSession).where(AttendanceSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Attendance session not found")

    session.status = SessionStatus.COMPLETED
    session.end_time = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session
