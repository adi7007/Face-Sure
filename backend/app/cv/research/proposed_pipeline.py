"""
Proposed Research Facial Recognition Pipeline (QMF-Score Engine).

Architecture:
Face Detection -> Face Quality -> Liveness -> Face Embedding -> QMF-Score Engine -> Result & Telemetry
"""

from typing import List, Tuple, Optional
import numpy as np

from app.cv.detector import FaceDetector
from app.cv.aligner import FaceAligner
from app.cv.quality import QualityAssessor
from app.cv.liveness import LivenessDetector
from app.cv.embedder import FaceEmbedder
from app.cv.matcher import FaceMatcher
from app.cv.research.config import QMFConfig, TelemetryRecord
from app.cv.research.qmf_engine import QMFScoreEngine, QMFDecisionResult


class ProposedQMFPipeline:
    """
    Proposed Pipeline integrating Face Quality, Anti-Spoofing Liveness, and QMF-Score Decision Fusion.
    """

    def __init__(self, config: Optional[QMFConfig] = None):
        self.config = config if config is not None else QMFConfig()
        self.detector = FaceDetector(min_detection_confidence=0.5)
        self.aligner = FaceAligner()
        self.quality_assessor = QualityAssessor()
        self.liveness_detector = LivenessDetector(min_liveness_threshold=self.config.tau_liveness_min)
        self.embedder = FaceEmbedder(embedding_dim=512)
        self.matcher = FaceMatcher(default_threshold=self.config.tau_base)
        self.qmf_engine = QMFScoreEngine(config=self.config)

    def process_frame(
        self,
        image: np.ndarray,
        enrolled_gallery: List[Tuple[str, str, np.ndarray]],
        landmark_history: Optional[List[np.ndarray]] = None,
    ) -> List[QMFDecisionResult]:
        """
        Execute full Proposed QMF-Score Pipeline on an incoming image frame.

        Args:
            image: BGR input image frame.
            enrolled_gallery: List of (student_id, template_id, embedding_vector) tuples.
            landmark_history: Optional historical landmark tracking data for multi-frame motion analysis.

        Returns:
            List of QMFDecisionResult objects for every detected face.
        """
        detected_faces = self.detector.detect_faces(image)
        if not detected_faces:
            return []

        results = []
        for face in detected_faces:
            # 1. Face Alignment
            aligned_crop = self.aligner.align(image, face.landmarks, crop_size=112)

            # 2. Quality Assessment
            quality_res = self.quality_assessor.assess_quality(
                aligned_crop, bbox=face.bbox, landmarks=face.landmarks
            )

            # 3. Liveness Anti-Spoofing Assessment
            liveness_res = self.liveness_detector.assess_liveness(
                aligned_crop, landmark_history=landmark_history
            )

            # 4. Feature Embedding Extraction
            embedding_vec = self.embedder.extract_embedding(aligned_crop)

            # 5. Raw Cosine Match Evaluation against gallery
            match_res = self.matcher.match(
                query_embedding=embedding_vec,
                enrolled_embeddings=enrolled_gallery,
                threshold=0.0,  # Raw match evaluation to feed QMF decision engine
            )

            top_similarity = match_res.confidence_score if match_res.confidence_score > 0 else 0.0
            candidate_id = match_res.matched_student_id

            # 6. Proposed QMF-Score Decision Fusion
            qmf_res = self.qmf_engine.evaluate_decision(
                similarity_score=top_similarity,
                quality_score=quality_res.quality_score,
                liveness_score=liveness_res.liveness_score,
                candidate_student_id=candidate_id,
            )

            results.append(qmf_res)

        return results
