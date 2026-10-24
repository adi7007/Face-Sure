"""
Course management API endpoints (List, Create, Get, Delete).
"""

import uuid
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError, DuplicateResourceError
from app.models.user import User
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseResponse

router = APIRouter(prefix="/courses", tags=["Course Management"])


def _format_course(course: Course) -> CourseResponse:
    return CourseResponse(
        id=course.id,
        course_code=course.course_code,
        course_name=course.course_name,
        department=course.department,
        instructor_id=course.instructor_id,
        enrolled_students_count=len(course.enrollments) if course.enrollments else 0,
        created_at=course.created_at,
    )


@router.get("", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all courses with enrollment counts."""
    stmt = select(Course).options(selectinload(Course.enrollments)).order_by(Course.course_code)
    result = await db.execute(stmt)
    courses = result.scalars().all()
    return [_format_course(c) for c in courses]


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
        id=uuid.uuid4(),
        course_code=payload.course_code,
        course_name=payload.course_name,
        department=payload.department,
        instructor_id=payload.instructor_id or current_user.id,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return _format_course(course)


@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a course."""
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise NotFoundError(f"Course '{course_id}' not found")

    await db.delete(course)
    await db.commit()
    return {"status": "success", "message": f"Course {course_id} deleted."}
