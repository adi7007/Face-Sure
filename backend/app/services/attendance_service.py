"""
Attendance Processing Service.

Integrates the validated Proposed QMF-Score CV Pipeline with PostgreSQL database persistence
to process live webcam frames, perform duplicate prevention, mark attendance records,
and calculate dashboard analytics summaries.
"""

import base64
import cv2
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.cv.research.proposed_pipeline import ProposedQMFPipeline, QMFConfig
from app.models.attendance import AttendanceSession, AttendanceRecord, SessionStatus, AttendanceStatus, AttendanceMethod
from app.models.student import Student
from app.models.face_embedding import FaceEmbedding
from app.core.exceptions import NotFoundError, DuplicateResourceError, BiometricQualityError, LivenessSpoofError


class AttendanceService:
    """
    Service layer integrating AI CV pipeline with DB records.
    """

    def __init__(self):
        self.qmf_pipeline = ProposedQMFPipeline()

    async def verify_and_mark_attendance(
        self,
        db: AsyncSession,
        session_id: UUID,
        image_base64: str,
    ) -> Dict[str, Any]:
        """
        Verify incoming webcam base64 frame image against active session gallery.

        Steps:
        1. Decode base64 image frame to BGR numpy array.
        2. Validate active session existence.
        3. Load enrolled student templates from DB gallery.
        4. Execute Proposed QMF-Score Pipeline.
        5. Enforce Application & Database level Duplicate Prevention.
        6. Persist AttendanceRecord with full telemetry.

        Returns:
            Dictionary containing verification status, telemetry, and student details.
        """
        # 1. Decode Base64 Image Frame
        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            img_bytes = base64.b64decode(image_base64)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame_bgr is None:
                raise ValueError("Could not decode image frame.")
        except Exception as e:
            raise ValueError(f"Invalid image frame encoding: {str(e)}")

        # 2. Validate Session
        result = await db.execute(
            select(AttendanceSession).where(AttendanceSession.id == session_id)
        )
        session_obj = result.scalars().first()
        if not session_obj:
            raise NotFoundError(f"Attendance session #{session_id} not found.")

        # 3. Load Enrolled Student Embeddings from DB
        embeddings_query = await db.execute(
            select(FaceEmbedding, Student.student_id)
            .join(Student, FaceEmbedding.student_id == Student.id)
            .where(Student.is_active.is_(True), FaceEmbedding.is_active.is_(True))
        )
        enrolled_gallery = []
        for embed_obj, stu_code in embeddings_query.all():
            vec = np.asarray(embed_obj.embedding, dtype=np.float32)
            if vec.shape != (512,) or not np.isfinite(vec).all():
                continue
            enrolled_gallery.append((stu_code, str(embed_obj.id), vec))

        if not enrolled_gallery:
            return {
                "status": "NO_ENROLLED_STUDENTS",
                "message": "No active biometric templates are enrolled; attendance was not recorded.",
                "telemetry": None,
            }

        # 4. Execute Proposed QMF-Score CV Pipeline
        pipeline_results = self.qmf_pipeline.process_frame(frame_bgr, enrolled_gallery)

        if not pipeline_results:
            return {
                "status": "NO_FACE_DETECTED",
                "message": "No human face localized in webcam frame.",
                "telemetry": None,
            }

        top_result = pipeline_results[0]
        telemetry = top_result.telemetry

        # Handle Quality / Liveness / Unknown Rejections
        if top_result.decision == "SPOOF_REJECTED":
            return {
                "status": "SPOOF_REJECTED",
                "message": "Presentation attack detected by FAS Liveness module.",
                "telemetry": telemetry.__dict__,
            }
        elif top_result.decision == "QUALITY_REJECTED":
            return {
                "status": "QUALITY_REJECTED",
                "message": "Face sample quality below minimum threshold.",
                "telemetry": telemetry.__dict__,
            }
        elif top_result.decision == "UNKNOWN_REJECTED" or not top_result.matched_student_id:
            return {
                "status": "UNKNOWN_REJECTED",
                "message": "Face similarity below adaptive threshold.",
                "telemetry": telemetry.__dict__,
            }

        # 5. Lookup Matched Student Record
        stu_query = await db.execute(
            select(Student).where(Student.student_id == top_result.matched_student_id)
        )
        student_obj = stu_query.scalars().first()
        if not student_obj:
            raise NotFoundError(f"Student with ID '{top_result.matched_student_id}' not found in database.")

        student_db_id = student_obj.id
        student_name = student_obj.full_name
        student_email = student_obj.email

        # 6. Application-Level Duplicate Prevention Check
        existing_record = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_db_id,
            )
        )
        if existing_record.scalars().first():
            return {
                "status": "ALREADY_MARKED",
                "message": f"Attendance already logged for student {top_result.matched_student_id}.",
                "student_id": top_result.matched_student_id,
                "student_name": student_name,
                "student_email": student_email,
                "telemetry": telemetry.__dict__,
            }

        # 7. Smart Late/Early Detection
        now = datetime.now(timezone.utc)
        late_cutoff = session_obj.start_time + __import__('datetime').timedelta(minutes=session_obj.late_threshold_minutes)
        
        if session_obj.status == SessionStatus.COMPLETED:
            attendance_status = AttendanceStatus.ABSENT
        elif now > late_cutoff:
            attendance_status = AttendanceStatus.LATE
        else:
            attendance_status = AttendanceStatus.PRESENT

        # 8. Persist Attendance Record into DB (with DB unique constraint safety)
        new_record = AttendanceRecord(
            student_id=student_db_id,
            session_id=session_id,
            marked_at=now,
            confidence_score=float(top_result.similarity_score),
            quality_score=float(top_result.quality_score),
            liveness_score=float(top_result.liveness_score),
            method=AttendanceMethod.FACE_RECOGNITION,
            status=attendance_status,
            remarks=f"QMF-Score: {top_result.composite_score:.3f} | tau(Q): {top_result.dynamic_threshold:.3f}",
        )
        
        db.add(new_record)
        try:
            await db.commit()
            await db.refresh(new_record)
        except Exception:
            await db.rollback()
            return {
                "status": "ALREADY_MARKED",
                "message": f"Duplicate attendance attempt blocked at database level.",
                "student_id": top_result.matched_student_id,
                "student_name": student_name,
                "student_email": student_email,
                "telemetry": telemetry.__dict__,
            }

        # 9. Build Explainable Decision Breakdown
        explainable_decision = {
            "identity_match": {
                "score": round(float(top_result.similarity_score) * 100, 1),
                "verdict": "PASS",
                "detail": f"Matched with {top_result.similarity_score:.3f} confidence"
            },
            "liveness": {
                "score": round(float(top_result.liveness_score) * 100, 1),
                "verdict": "PASS" if top_result.liveness_score >= 0.5 else "FAIL",
                "detail": "Live face verified"
            },
            "quality": {
                "score": round(float(top_result.quality_score) * 100, 1),
                "verdict": "PASS" if top_result.quality_score >= 0.4 else "FAIL",
                "detail": f"Quality score {top_result.quality_score:.3f}"
            },
            "duplicate_check": {
                "verdict": "CLEAR",
                "detail": "No prior attendance in this session"
            },
            "time_status": {
                "verdict": attendance_status.value,
                "detail": f"Marked at {now.strftime('%H:%M:%S UTC')} | "
                          f"Session started {session_obj.start_time.strftime('%H:%M:%S UTC')} | "
                          f"Late threshold: {session_obj.late_threshold_minutes}min"
            },
            "final_decision": attendance_status.value,
            "composite_qmf_score": round(float(top_result.composite_score), 3),
            "dynamic_threshold": round(float(top_result.dynamic_threshold), 3),
        }

        return {
            "status": "SUCCESS",
            "message": f"Attendance marked {attendance_status.value} for {student_name}.",
            "record_id": new_record.id,
            "student_id": top_result.matched_student_id,
            "student_name": student_name,
            "student_email": student_email,
            "attendance_status": attendance_status.value,
            "marked_at": new_record.marked_at.isoformat(),
            "telemetry": telemetry.__dict__,
            "explainable_decision": explainable_decision,
        }

