import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.attendance import AttendanceSession, SessionStatus


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_session_success(mock_db):
    # Mock db.refresh to assign database defaults
    async def mock_refresh(session_obj):
        session_obj.id = uuid4()
        session_obj.created_at = datetime.now(timezone.utc)
    mock_db.refresh = mock_refresh

    app.dependency_overrides[get_db] = lambda: mock_db

    course_id = uuid4()
    payload = {
        "course_id": str(course_id),
        "title": "Lecture 1: Intro to Face Recognition",
        "late_threshold_minutes": 15
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/sessions", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Lecture 1: Intro to Face Recognition"
        assert data["status"] == "ACTIVE"
        assert data["course_id"] == str(course_id)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_sessions(mock_db):
    course_id = uuid4()
    instructor_id = uuid4()
    session_id = uuid4()
    
    mock_session = AttendanceSession(
        id=session_id,
        course_id=course_id,
        created_by=instructor_id,
        title="Session 1",
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(timezone.utc),
        late_threshold_minutes=15,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_session]
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Session 1"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_stop_session(mock_db):
    session_id = uuid4()
    course_id = uuid4()
    instructor_id = uuid4()
    
    mock_session = AttendanceSession(
        id=session_id,
        course_id=course_id,
        created_by=instructor_id,
        title="Session 1",
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(timezone.utc),
        late_threshold_minutes=15,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_session
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"/api/v1/sessions/{session_id}/stop")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "closed" in data["message"]

    app.dependency_overrides.clear()
