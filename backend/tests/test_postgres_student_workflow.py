"""Opt-in PostgreSQL integration coverage for the student and kiosk workflow.

Run only with FACE_SURE_RUN_DB_TESTS=1 and a disposable database URL.
The test intentionally uses the real FastAPI dependency, SQLAlchemy async
engine, PostgreSQL, and pgvector schema; it contains no database mocks.
"""

import base64
import os
from datetime import datetime, timezone
from uuid import uuid4

import cv2
import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text

pytestmark = pytest.mark.skipif(
    os.getenv("FACE_SURE_RUN_DB_TESTS") != "1",
    reason="requires a disposable PostgreSQL database",
)

from app.config import get_settings
from app.core import database
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.attendance import AttendanceRecord, AttendanceSession, SessionStatus
from app.models.course import Course
from app.models.user import User, UserRole


def _image_data_url(image: np.ndarray) -> str:
    """Encode a controlled test image without persisting it to disk."""
    
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return "data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("ascii")


def _controlled_face(seed: int, glare: bool = False) -> np.ndarray:
    """Create deterministic, distinct face-like test inputs for pipeline regression coverage."""
    image = np.full((300, 300, 3), 185 + seed % 40, dtype=np.uint8)
    center = (150, 150)
    cv2.ellipse(image, center, (80 + seed % 12, 108 + seed % 15), 0, 0, 360, (175, 145, 120), -1)
    eye_y = 120 + seed % 8
    eye_offset = 42 + seed % 7
    cv2.circle(image, (150 - eye_offset, eye_y), 15, (20, 20, 20), -1)
    cv2.circle(image, (150 + eye_offset, eye_y), 15, (20, 20, 20), -1)
    cv2.line(image, (150, eye_y + 12), (150, 170), (80, 60, 40), 4)
    cv2.ellipse(image, (150, 205 + seed % 8), (35, 12), 0, 0, 180, (45, 20, 75), 4)
    if glare:
        cv2.rectangle(image, (75, 75), (225, 225), (255, 255, 255), -1)
    return image


@pytest.mark.asyncio
async def test_postgres_student_registration_and_empty_gallery_rejection():
    settings = get_settings()
    assert "test" in settings.database_url, "integration tests require a disposable test database"
    get_settings.cache_clear()
    database.init_engine()
    assert database._async_session_factory is not None
    async with database._async_session_factory() as db:
        await db.execute(text(
            "TRUNCATE attendance_records, attendance_sessions, enrollments, face_embeddings, "
            "students, courses, users RESTART IDENTITY CASCADE"
        ))
        await db.commit()
    user_id = uuid4()
    course_id = uuid4()
    session_id = uuid4()
    async with database._async_session_factory() as db:
        user = User(
            id=user_id,
            username="integration-admin",
            email="integration-admin@example.test",
            hashed_password=hash_password("integration-only-password"),
            full_name="Integration Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        course = Course(
            id=course_id,
            course_code="TEST-101",
            course_name="Integration Test Course",
            department="Testing",
            instructor_id=user_id,
        )
        attendance_session = AttendanceSession(
            id=session_id,
            course_id=course_id,
            created_by=user_id,
            title="Integration attendance session",
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(timezone.utc),
            late_threshold_minutes=15,
        )
        db.add_all([user, course, attendance_session])
        await db.commit()

    token = create_access_token(subject=str(user_id), role=UserRole.ADMIN.value)
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        initial = await client.get("/api/v1/students")
        assert initial.status_code == 200
        assert initial.json() == []

        first_image = _image_data_url(_controlled_face(17))
        second_image = _image_data_url(_controlled_face(83))
        first = {
            "student_id": "TEST-DB-001",
            "full_name": "Integration Student One",
            "email": "student.one@example.com",
            "department": "Testing",
            "academic_year": "1st Year",
            "photos_base64": [first_image],
        }
        second = {
            "student_id": "TEST-DB-002",
            "full_name": "Integration Student Two",
            "email": "student.two@example.com",
            "department": "Testing",
            "academic_year": "2nd Year",
            "photos_base64": [second_image],
        }
        assert (await client.post("/api/v1/students", json=first)).status_code == 201
        assert (await client.post("/api/v1/students", json=second)).status_code == 201
        disposable = {
            "student_id": "TEST-DB-005",
            "full_name": "Integration Student Disposable",
            "email": "student.disposable@example.com",
            "department": "Testing",
            "academic_year": "3rd Year",
        }
        assert (await client.post("/api/v1/students", json=disposable)).status_code == 201

        duplicate = await client.post("/api/v1/students", json=first)
        assert duplicate.status_code == 409
        invalid = await client.post("/api/v1/students", json={**first, "student_id": "TEST-DB-003", "email": None})
        assert invalid.status_code == 422
        failed_biometric = await client.post(
            "/api/v1/students",
            json={**first, "student_id": "TEST-DB-004", "email": "student.four@example.com", "photos_base64": ["not-base64"]},
        )
        assert failed_biometric.status_code == 422

        directory = await client.get("/api/v1/students")
        assert directory.status_code == 200
        students = directory.json()
        assert {student["student_id"] for student in students} == {"TEST-DB-001", "TEST-DB-002", "TEST-DB-005"}
        embedding_counts = {student["student_id"]: student["embedding_count"] for student in students}
        assert embedding_counts == {"TEST-DB-001": 1, "TEST-DB-002": 1, "TEST-DB-005": 0}

        first_id = next(student["id"] for student in students if student["student_id"] == "TEST-DB-001")
        second_id = next(student["id"] for student in students if student["student_id"] == "TEST-DB-002")
        disposable_id = next(student["id"] for student in students if student["student_id"] == "TEST-DB-005")
        updated = await client.put(
            f"/api/v1/students/{first_id}",
            json={"full_name": "Integration Student One Updated"},
        )
        assert updated.status_code == 200
        assert updated.json()["full_name"] == "Integration Student One Updated"

        unknown = await client.post(
            "/api/v1/attendance/verify-and-mark",
            json={"session_id": str(session_id), "image_base64": _image_data_url(np.zeros((48, 48, 3), dtype=np.uint8))},
        )
        assert unknown.status_code == 200
        assert unknown.json()["status"] == "NO_FACE_DETECTED"
        assert "student_id" not in unknown.json()

        first_scan = await client.post(
            "/api/v1/attendance/verify-and-mark",
            json={"session_id": str(session_id), "image_base64": first_image},
        )
        assert first_scan.status_code == 200
        assert first_scan.json()["status"] == "SUCCESS"
        assert first_scan.json()["student_id"] == "TEST-DB-001"
        assert first_scan.json()["student_name"] == "Integration Student One Updated"
        assert first_scan.json()["student_email"] == "student.one@example.com"

        second_scan = await client.post(
            "/api/v1/attendance/verify-and-mark",
            json={"session_id": str(session_id), "image_base64": second_image},
        )
        assert second_scan.status_code == 200
        assert second_scan.json()["status"] == "SUCCESS"
        assert second_scan.json()["student_id"] == "TEST-DB-002"
        assert second_scan.json()["student_name"] == "Integration Student Two"
        assert second_scan.json()["student_email"] == "student.two@example.com"

        duplicate_scan = await client.post(
            "/api/v1/attendance/verify-and-mark",
            json={"session_id": str(session_id), "image_base64": first_image},
        )
        assert duplicate_scan.status_code == 200
        assert duplicate_scan.json()["status"] == "ALREADY_MARKED"
        assert duplicate_scan.json()["student_id"] == "TEST-DB-001"

        rejected_glare = await client.post(
            "/api/v1/attendance/verify-and-mark",
            json={"session_id": str(session_id), "image_base64": _image_data_url(_controlled_face(17, glare=True))},
        )
        assert rejected_glare.status_code == 200
        assert rejected_glare.json()["status"] in {"SPOOF_REJECTED", "QUALITY_REJECTED"}
        assert "student_id" not in rejected_glare.json()

        # Attendance created by verified scans prevents profile deletion.
        protected_delete = await client.delete(f"/api/v1/students/{second_id}")
        assert protected_delete.status_code == 409
        assert (await client.delete(f"/api/v1/students/{first_id}")).status_code == 409

        deleted = await client.delete(f"/api/v1/students/{disposable_id}")
        assert deleted.status_code == 200

    # A new engine/session verifies that the directory is database-backed, not cached state.
    await database.close_engine()
    database.init_engine()
    assert database._async_session_factory is not None
    async with database._async_session_factory() as db:
        remaining = (await db.execute(select(func.count()).select_from(AttendanceRecord))).scalar_one()
        assert remaining == 2

    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        persisted = await client.get("/api/v1/students")
        assert persisted.status_code == 200
        assert {student["student_id"] for student in persisted.json()} == {"TEST-DB-001", "TEST-DB-002"}

    await database.close_engine()
