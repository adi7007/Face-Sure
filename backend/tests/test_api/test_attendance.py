import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.student import Student
from app.models.attendance import AttendanceSession, AttendanceRecord, SessionStatus, AttendanceStatus


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_verify_and_mark_attendance(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    session_id = uuid4()
    record_id = uuid4()

    mock_response = {
        "status": "SUCCESS",
        "message": "Attendance marked PRESENT for Test Student One.",
        "record_id": str(record_id),
        "student_id": "STU-2026-001",
        "student_name": "Test Student One",
        "marked_at": datetime.now(timezone.utc).isoformat(),
        "telemetry": {
            "quality_score": 0.88,
            "liveness_score": 0.99,
            "similarity_score": 0.942
        }
    }

    with patch("app.api.v1.attendance.attendance_service.verify_and_mark_attendance", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_response

        payload = {
            "session_id": str(session_id),
            "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/attendance/verify-and-mark", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"
            assert data["student_id"] == "STU-2026-001"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_dashboard_summary(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db

    session_id = uuid4()
    student_id = uuid4()

    mock_session = AttendanceSession(
        id=session_id,
        course_id=uuid4(),
        created_by=uuid4(),
        title="Session 1",
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(timezone.utc),
        late_threshold_minutes=15,
    )

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

    mock_record = AttendanceRecord(
        id=uuid4(),
        student_id=student_id,
        session_id=session_id,
        status=AttendanceStatus.PRESENT,
        marked_at=datetime.now(timezone.utc),
        confidence_score=0.942,
        quality_score=0.88,
        liveness_score=0.99
    )

    # We need to mock 4 database execution queries in sequence:
    # 1. Total students count
    # 2. Active session
    # 3. Present count for active session
    # 4. Recent records (join of AttendanceRecord and Student)

    res1 = MagicMock()
    res1.scalar.return_value = 100

    res2 = MagicMock()
    res2.scalars.return_value.first.return_value = mock_session

    res3 = MagicMock()
    res3.scalar.return_value = 45

    res4 = MagicMock()
    res4.all.return_value = [(mock_record, mock_student)]

    mock_db.execute.side_effect = [res1, res2, res3, res4]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/attendance/dashboard-summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 100
        assert data["present_count"] == 45
        assert data["absent_count"] == 55
        assert data["active_session"]["id"] == str(session_id)
        assert len(data["recent_records"]) == 1
        assert data["recent_records"][0]["student_id"] == "STU-2026-001"
        assert data["recent_records"][0]["name"] == "Test Student One"

    app.dependency_overrides.clear()
