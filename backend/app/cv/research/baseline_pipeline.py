"""
Baseline Facial Recognition Pipeline.

Architecture:
Face Detection -> Face Embedding -> Fixed Similarity Threshold Matching -> Result & Telemetry
"""

import uuid
from typing import List, Tuple, Optional
import numpy as np

from app.cv.detector import FaceDetector
from app.cv.embedder import FaceEmbedder
from app.cv.matcher import FaceMatcher
from app.cv.research.config import BaselineConfig, TelemetryRecord


class BaselinePipeline:
    """
    Standard Baseline Pipeline using a fixed similarity threshold without quality adaptation or liveness fusion.
    """

    def __init__(self, config: Optional[BaselineConfig] = None):
        self.config = config if config is not None else BaselineConfig()
        self.detector = FaceDetector(min_detection_confidence=0.5)
        self.embedder = FaceEmbedder(embedding_dim=512)
        self.matcher = FaceMatcher(default_threshold=self.config.fixed_similarity_threshold)

    def process_frame(
        self,
        image: np.ndarray,
        enrolled_gallery: List[Tuple[str, str, np.ndarray]],
    ) -> List[TelemetryRecord]:
        """
        Process incoming image through the Baseline Pipeline.

        Args:
            image: BGR input frame.
            enrolled_gallery: List of (student_id, template_id, embedding_vector) tuples.

        Returns:
            List of TelemetryRecord objects for every detected face.
        """
        detected_faces = self.detector.detect_faces(image)
        if not detected_faces:
            return []

        telemetry_records = []
        for face in detected_faces:
            pred_id = f"BASE-PRED-{uuid.uuid4().hex[:10].upper()}"
            x1, y1, x2, y2 = face.bbox
            
            # Crop face patch
            h, w = image.shape[:2]
            crop = image[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
            
            # Extract 512D embedding
            embedding_vec = self.embedder.extract_embedding(crop)
            
            # Perform similarity matching with fixed threshold
            match_res = self.matcher.match(
                query_embedding=embedding_vec,
                enrolled_embeddings=enrolled_gallery,
                threshold=self.config.fixed_similarity_threshold,
            )

            decision = "AUTHENTICATED" if match_res.is_known else "UNKNOWN_REJECTED"
            matched_id = match_res.matched_student_id if match_res.is_known else None

            record = TelemetryRecord(
                prediction_id=pred_id,
                pipeline_type="BASELINE",
                similarity_score=match_res.confidence_score,
                quality_score=1.0,   # Baseline assumes unmeasured 1.0 quality
                liveness_score=1.0,  # Baseline assumes unmeasured 1.0 liveness
                composite_score=match_res.confidence_score,
                dynamic_threshold=self.config.fixed_similarity_threshold,
                final_decision=decision,
                matched_student_id=matched_id,
                threshold_parameters={
                    "fixed_similarity_threshold": self.config.fixed_similarity_threshold,
                },
                model_version=self.config.model_version,
                experimental_config={
                    "pipeline_name": self.config.pipeline_name,
                },
            )
            telemetry_records.append(record)

        return telemetry_records
