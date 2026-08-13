"""
Course management API endpoints (List, Create, Get).
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError, DuplicateResourceError
from app.models.user import User
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseResponse

router = APIRouter(prefix="/courses", tags=["Course Management"])


@router.get("", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all courses."""
    stmt = select(Course).order_by(Course.course_code)
    result = await db.execute(stmt)
    courses = result.scalars().all()
    return courses


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new course."""
    stmt = select(Course).where(Course.course_code == payload.course_code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateResourceError(f"Course code '{payload.course_code}' already exists")

    course = Course(
        course_code=payload.course_code,
        course_name=payload.course_name,
        department=payload.department,
        instructor_id=payload.instructor_id,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course
