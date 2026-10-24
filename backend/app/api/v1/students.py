"""
Student management API endpoints (List, Create, Get, Update, Delete, Enroll Face).
"""

import base64
import uuid
import cv2
import numpy as np
from typing import List, Tuple
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError, DuplicateResourceError
from app.models.user import User
from app.models.student import Student
from app.models.face_embedding import FaceEmbedding
from app.models.attendance import AttendanceRecord
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, EnrollPhotoRequest
from app.cv.aligner import FaceAligner
from app.cv.detector import FaceDetector
from app.cv.embedder import FaceEmbedder
from app.cv.liveness import LivenessDetector
from app.cv.quality import QualityAssessor

router = APIRouter(prefix="/students", tags=["Student Management"])
face_embedder = FaceEmbedder()
face_detector = FaceDetector(min_detection_confidence=0.5)
face_aligner = FaceAligner()
quality_assessor = QualityAssessor()
liveness_detector = LivenessDetector()
EMBEDDING_DIMENSION = 512


def _prepare_enrollment_template(photo_base64: str) -> Tuple[List[float], float]:
    """Validate an enrollment image and produce an aligned normalized 512D vector."""
    try:
        clean_b64 = photo_base64.split(",", 1)[1] if "," in photo_base64 else photo_base64
        img_bytes = base64.b64decode(clean_b64, validate=True)
        image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception as exc:
        raise ValueError("Photo is not a valid base64-encoded image") from exc

    if image is None:
        raise ValueError("Photo could not be decoded")

    faces = face_detector.detect_faces(image)
    if len(faces) != 1:
        raise ValueError("Enrollment photo must contain exactly one face")

    face = faces[0]
    aligned_face = face_aligner.align(image, face.landmarks, crop_size=112)
    quality = quality_assessor.assess_quality(
        aligned_face, bbox=face.bbox, landmarks=face.landmarks
    )
    if not quality.is_acceptable:
        raise ValueError("Enrollment photo did not meet face-quality requirements")

    liveness = liveness_detector.assess_liveness(aligned_face)
    if not liveness.is_live:
        raise ValueError("Enrollment photo did not pass liveness verification")

    vector = face_embedder.extract_embedding(aligned_face)
    if vector.shape != (EMBEDDING_DIMENSION,) or not np.isfinite(vector).all():
        raise ValueError("Face embedding has an invalid dimension or value")
    if not np.isclose(np.linalg.norm(vector), 1.0, atol=1e-3):
        raise ValueError("Face embedding is not normalized")

    return vector.astype(np.float32).tolist(), float(quality.quality_score)


def _format_student(student: Student) -> StudentResponse:
    """Helper to convert Student model to response schema with embedding count."""
    return StudentResponse(
        id=student.id,
        student_id=student.student_id,
        full_name=student.full_name,
        email=student.email,
        department=student.department,
        academic_year=student.academic_year,
        is_active=student.is_active,
        user_id=student.user_id,
        embedding_count=len(student.face_embeddings) if student.face_embeddings else 0,
        created_at=student.created_at,
        photo_url=student.face_embeddings[0].image_path if (student.face_embeddings and student.face_embeddings[0].image_path) else None,
    )


@router.get("", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
async def list_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all students with face embedding count."""
    stmt = (
        select(Student)
        .options(selectinload(Student.face_embeddings))
        .order_by(Student.student_id)
    )
    result = await db.execute(stmt)
    students = result.scalars().all()
    return [_format_student(s) for s in students]


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a student and optional biometric templates as one transaction."""
    email = str(payload.email).lower()

    templates: List[Tuple[List[float], float]] = []
    if payload.photos_base64:
        try:
            templates = [_prepare_enrollment_template(photo) for photo in payload.photos_base64]
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    # Check duplicate student_id or email
    stmt = select(Student).where(
        (Student.student_id == payload.student_id) | (Student.email == email)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateResourceError(f"Student with ID '{payload.student_id}' or Email '{email}' already exists")

    student = Student(
        id=uuid.uuid4(),
        student_id=payload.student_id,
        full_name=payload.full_name,
        email=email,
        department=payload.department,
        academic_year=payload.academic_year,
        is_active=True,
    )
    db.add(student)
    await db.flush()

    for index, (vector, quality_score) in enumerate(templates):
        db.add(FaceEmbedding(
            id=uuid.uuid4(), student_id=student.id, embedding=vector, image_path=None,
            quality_score=quality_score, capture_angle=f"Angle {index + 1}", is_active=True,
        ))

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateResourceError(
            f"Student with ID '{payload.student_id}' or Email '{email}' already exists"
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student registration could not be saved",
        ) from exc

    # Reload with embeddings
    stmt_reload = (
        select(Student)
        .where(Student.id == student.id)
        .options(selectinload(Student.face_embeddings))
    )
    res_reload = await db.execute(stmt_reload)
    reloaded = res_reload.scalar_one()
    return _format_student(reloaded)


@router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student details by UUID."""
    stmt = (
        select(Student)
        .where(Student.id == student_id)
        .options(selectinload(Student.face_embeddings))
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student with ID '{student_id}' not found")
    return _format_student(student)


@router.put("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def update_student(
    student_id: UUID,
    payload: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update student profile fields."""
    stmt = (
        select(Student)
        .where(Student.id == student_id)
        .options(selectinload(Student.face_embeddings))
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student with ID '{student_id}' not found")

    if payload.full_name is not None:
        student.full_name = payload.full_name
    if payload.email is not None:
        student.email = payload.email
    if payload.department is not None:
        student.department = payload.department
    if payload.academic_year is not None:
        student.academic_year = payload.academic_year
    if payload.is_active is not None:
        student.is_active = payload.is_active

    await db.commit()
    await db.refresh(student)
    return _format_student(student)


@router.delete("/{student_id}", status_code=status.HTTP_200_OK)
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a student only when doing so cannot erase attendance history."""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student with ID '{student_id}' not found")

    attendance_result = await db.execute(
        select(AttendanceRecord.id).where(AttendanceRecord.student_id == student_id).limit(1)
    )
    if attendance_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student has attendance history and cannot be deleted; deactivate the profile instead",
        )

    await db.delete(student)
    await db.commit()
    return {"status": "success", "message": f"Student {student_id} deleted successfully."}


@router.post("/{student_id}/enroll-photo", status_code=status.HTTP_200_OK)
async def enroll_student_photo(
    student_id: UUID,
    payload: EnrollPhotoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enroll a new face photo for an existing student."""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student with ID '{student_id}' not found")

    try:
        vector, quality_score = _prepare_enrollment_template(payload.photo_base64)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    embedding = FaceEmbedding(
        id=uuid.uuid4(), student_id=student.id, embedding=vector, image_path=None,
        quality_score=quality_score, capture_angle=payload.angle or "Front", is_active=True,
    )
    db.add(embedding)
    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face template could not be saved",
        ) from exc
    return {"status": "success", "message": "Face template enrolled as a 512D vector.", "embedding_id": str(embedding.id)}
