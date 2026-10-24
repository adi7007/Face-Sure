"""
Analytics Service.

Provides analytical computations for attendance data:
- Daily attendance trends
- Per-course statistics
- At-risk student detection
- Attendance prediction
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceStatus
from app.models.course import Course, Enrollment


class AnalyticsService:
    """Service for computing attendance analytics."""

    async def compute_daily_attendance(
        self, db: AsyncSession, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Compute daily attendance counts for the last N days.

        Returns list of {date, present, late, absent, total} dicts.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        daily = []

        for i in range(days):
            day = cutoff + timedelta(days=i + 1)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # Count records by status for this day
            present_res = await db.execute(
                select(func.count(AttendanceRecord.id)).where(
                    and_(
                        AttendanceRecord.marked_at >= day_start,
                        AttendanceRecord.marked_at < day_end,
                        AttendanceRecord.status == AttendanceStatus.PRESENT,
                    )
                )
            )
            late_res = await db.execute(
                select(func.count(AttendanceRecord.id)).where(
                    and_(
                        AttendanceRecord.marked_at >= day_start,
                        AttendanceRecord.marked_at < day_end,
                        AttendanceRecord.status == AttendanceStatus.LATE,
                    )
                )
            )

            present = present_res.scalar() or 0
            late = late_res.scalar() or 0

            daily.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "day_name": day_start.strftime("%a"),
                "present": present,
                "late": late,
                "total": present + late,
            })

        return daily

    async def compute_at_risk_students(
        self, db: AsyncSession, threshold: float = 75.0
    ) -> List[Dict[str, Any]]:
        """
        Identify students whose overall attendance is below the threshold.

        Returns list of at-risk students with their attendance stats.
        """
        students_res = await db.execute(
            select(Student).where(Student.is_active == True)
        )
        students = students_res.scalars().all()

        # Total sessions
        total_sessions_res = await db.execute(
            select(func.count(AttendanceSession.id))
        )
        total_sessions = total_sessions_res.scalar() or 1

        at_risk = []
        for student in students:
            # Count attendance records for this student
            records_res = await db.execute(
                select(func.count(AttendanceRecord.id)).where(
                    AttendanceRecord.student_id == student.id
                )
            )
            attended = records_res.scalar() or 0
            attendance_pct = round((attended / total_sessions) * 100, 1) if total_sessions > 0 else 0.0

            if attendance_pct < threshold:
                # Determine risk level
                if attendance_pct < 60:
                    risk_level = "CRITICAL"
                elif attendance_pct < threshold:
                    risk_level = "HIGH" if attendance_pct < 70 else "MEDIUM"
                else:
                    risk_level = "LOW"

                at_risk.append({
                    "student_id": str(student.id),
                    "student_code": student.student_id,
                    "full_name": student.full_name,
                    "department": student.department,
                    "attendance_pct": attendance_pct,
                    "sessions_attended": attended,
                    "total_sessions": total_sessions,
                    "risk_level": risk_level,
                    "classes_needed": max(0, int(
                        (threshold * total_sessions / 100) - attended
                    )),
                })

        # Sort by attendance % ascending (most at-risk first)
        at_risk.sort(key=lambda x: x["attendance_pct"])
        return at_risk

    async def predict_attendance(
        self, db: AsyncSession, student_id: UUID, remaining_sessions: int = 20, required_pct: float = 75.0
    ) -> Dict[str, Any]:
        """
        Predict how many classes a student needs to attend to meet the minimum.

        Args:
            student_id: UUID of the student.
            remaining_sessions: Estimated remaining sessions in the semester.
            required_pct: Minimum attendance percentage required.
        """
        # Count current attendance
        total_sessions_res = await db.execute(
            select(func.count(AttendanceSession.id))
        )
        total_sessions = total_sessions_res.scalar() or 0

        attended_res = await db.execute(
            select(func.count(AttendanceRecord.id)).where(
                AttendanceRecord.student_id == student_id
            )
        )
        attended = attended_res.scalar() or 0

        current_pct = round((attended / total_sessions) * 100, 1) if total_sessions > 0 else 0.0

        # Calculate minimum classes needed
        total_future = total_sessions + remaining_sessions
        needed_total = int((required_pct / 100) * total_future)
        classes_needed = max(0, needed_total - attended)

        # Can they meet the target?
        can_achieve = classes_needed <= remaining_sessions

        return {
            "student_id": str(student_id),
            "current_attendance_pct": current_pct,
            "sessions_attended": attended,
            "total_sessions_so_far": total_sessions,
            "remaining_sessions": remaining_sessions,
            "required_pct": required_pct,
            "classes_needed_to_meet_target": classes_needed,
            "can_achieve_target": can_achieve,
            "projected_pct": round(
                ((attended + remaining_sessions) / total_future) * 100, 1
            ) if total_future > 0 else 0.0,
        }
