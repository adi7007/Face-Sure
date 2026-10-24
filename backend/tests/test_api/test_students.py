import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.student import Student
from app.schemas.student import StudentResponse


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_list_students(mock_db):
    # Mocking Student query result
    student_id = uuid4()
    mock_student = Student(
        id=student_id,
        student_id="STU-2026-001",
        full_name="Test Student One",
        email="alex@project.edu",
        department="Computer Science",
        academic_year="4th Year",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_student]
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/students")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["student_id"] == "STU-2026-001"
        assert data[0]["full_name"] == "Test Student One"
        assert data[0]["email"] == "alex@project.edu"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_student_success(mock_db):
    # The create_student endpoint performs:
    #   1. db.execute(select check for duplicate) -> scalar_one_or_none() -> None
    #   2. db.add(student) + db.flush()
    #   3. db.commit()
    #   4. db.execute(select reload with embeddings) -> scalar_one() -> Student object

    student_uuid = uuid4()

    # Build a proper Student object that _format_student can serialize
    reloaded_student = Student(
        id=student_uuid,
        student_id="STU-2026-999",
        full_name="New Student",
        email="new@project.edu",
        department="Mechanical Engineering",
        academic_year="1st Year",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    # Set the face_embeddings relationship to an empty list (no photos submitted)
    reloaded_student.face_embeddings = []

    # Mock the two db.execute calls in sequence
    mock_dup_check = MagicMock()
    mock_dup_check.scalar_one_or_none.return_value = None

    mock_reload = MagicMock()
    mock_reload.scalar_one.return_value = reloaded_student

    mock_db.execute.side_effect = [mock_dup_check, mock_reload]

    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "student_id": "STU-2026-999",
        "full_name": "New Student",
        "email": "new@project.edu",
        "department": "Mechanical Engineering",
        "academic_year": "1st Year"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/students", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == "STU-2026-999"
        assert data["full_name"] == "New Student"
        assert data["email"] == "new@project.edu"
        assert "id" in data
        assert data["is_active"] is True

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_student_success(mock_db):
    student_id = uuid4()
    mock_student = Student(
        id=student_id,
        student_id="STU-2026-001",
        full_name="Test Student One",
        email="alex@project.edu",
        department="Computer Science",
        academic_year="4th Year",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_student
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/v1/students/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(student_id)
        assert data["student_id"] == "STU-2026-001"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_student_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db
    non_existent_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/v1/students/{non_existent_id}")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["message"].lower()

    app.dependency_overrides.clear()
