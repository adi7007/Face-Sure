import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.student import Student
from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceStatus, AttendanceMethod, SessionStatus


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_export_csv_empty_db(mock_db):
    # Mocking database select returning no rows
    mock_result = MagicMock()
    mock_result.all.return_value = []
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/reports/export-csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        content = response.text
        assert "Record ID,Student ID,Student Name" in content
        # An empty database must not fabricate attendance rows.
        assert "STU-2026-001" not in content
        assert content.count("\n") == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_export_csv_with_records(mock_db):
    session_id = uuid4()
    student_id = uuid4()
    record_id = uuid4()

    mock_session = AttendanceSession(
        id=session_id,
        course_id=uuid4(),
        created_by=uuid4(),
        title="Session 1",
        status=SessionStatus.ACTIVE if False else None,  # We just need it to have some attributes
        start_time=datetime.now(timezone.utc),
        late_threshold_minutes=15,
    )
    mock_session.id = session_id  # explicitly set

    mock_student = Student(
        id=student_id,
        student_id="STU-2026-999",
        full_name="Jane Doe",
        email="jane@project.edu",
        department="Data Science",
        academic_year="3rd Year",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    mock_record = AttendanceRecord(
        id=record_id,
        student_id=student_id,
        session_id=session_id,
        status=AttendanceStatus.PRESENT,
        method=AttendanceMethod.FACE_RECOGNITION,
        marked_at=datetime.now(timezone.utc),
        confidence_score=0.975,
        quality_score=0.91,
        liveness_score=0.98
    )

    mock_result = MagicMock()
    mock_result.all.return_value = [(mock_record, mock_student, mock_session)]
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Request with session_id query param
        response = await client.get(f"/api/v1/reports/export-csv?session_id={session_id}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        content = response.text
        assert "STU-2026-999" in content
        assert "Jane Doe" in content
        assert "Data Science" in content
        assert "0.975" in content

    app.dependency_overrides.clear()
