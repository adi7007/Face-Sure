"""
Student management API endpoints (List, Create, Get, Delete).
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
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Student Management"])


@router.get("", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
async def list_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all active students."""
    stmt = select(Student).where(Student.is_active == True).order_by(Student.student_id)
    result = await db.execute(stmt)
    students = result.scalars().all()
    return students


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new student profile."""
    # Check duplicate student_id or email
    stmt = select(Student).where(
        (Student.student_id == payload.student_id) | (Student.email == payload.email)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateResourceError("Student with this ID or Email already exists")

    student = Student(
        student_id=payload.student_id,
        full_name=payload.full_name,
        email=payload.email,
        department=payload.department,
        academic_year=payload.academic_year,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student details by ID."""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student with ID '{student_id}' not found")
    return student
