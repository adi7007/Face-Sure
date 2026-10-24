import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.course import Course


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_list_courses(mock_db):
    course_id = uuid4()
    instructor_id = uuid4()
    mock_course = Course(
        id=course_id,
        course_code="CS-401",
        course_name="Deep Learning & CV",
        department="Computer Science",
        instructor_id=instructor_id,
        created_at=datetime.now(timezone.utc),
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_course]
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/courses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["course_code"] == "CS-401"
        assert data[0]["course_name"] == "Deep Learning & CV"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_course_success(mock_db):
    # Mock duplicate check lookup returning None
    mock_lookup_result = MagicMock()
    mock_lookup_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_lookup_result

    # Mock db.refresh to assign database defaults
    async def mock_refresh(course_obj):
        course_obj.id = uuid4()
        course_obj.created_at = datetime.now(timezone.utc)
    mock_db.refresh = mock_refresh

    app.dependency_overrides[get_db] = lambda: mock_db

    instructor_id = uuid4()
    payload = {
        "course_code": "CS-402",
        "course_name": "Natural Language Processing",
        "department": "Computer Science",
        "instructor_id": str(instructor_id)
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/courses", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["course_code"] == "CS-402"
        assert data["instructor_id"] == str(instructor_id)

    app.dependency_overrides.clear()
