"""
Recognition Pipeline Orchestrator module.

Integrates Face Detection, Facial Alignment, Quality Assessment,
Embedding Extraction, and Similarity Matching into an incremental CV pipeline.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

from app.cv.detector import FaceDetector, DetectedFace
from app.cv.aligner import FaceAligner
from app.cv.quality import QualityAssessor, QualityResult
from app.cv.embedder import FaceEmbedder
from app.cv.matcher import FaceMatcher, MatchResult


@dataclass
class PipelineFrameResult:
    """Comprehensive result of executing recognition pipeline on a single frame."""

    face_found: bool
    quality_result: Optional[QualityResult]
    match_result: Optional[MatchResult]
    bounding_box: Optional[Tuple[int, int, int, int]]
    embedding: Optional[np.ndarray]


class RecognitionPipeline:
    """
    Incremental Face Recognition Pipeline orchestrator.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_face_size: int = 50,
        min_laplacian_variance: float = 40.0,
        matching_threshold: float = 0.60,
    ):
        self.detector = FaceDetector(min_detection_confidence=min_detection_confidence)
        self.aligner = FaceAligner()
        self.quality_assessor = QualityAssessor(
            min_face_size=min_face_size,
            min_laplacian_variance=min_laplacian_variance,
        )
        self.embedder = FaceEmbedder(embedding_dim=512)
        self.matcher = FaceMatcher(default_threshold=matching_threshold)

    def process_frame(
        self,
        image: np.ndarray,
        enrolled_gallery: List[Tuple[str, str, np.ndarray]],  # List of (student_id, template_id, vector)
        matching_threshold: Optional[float] = None,
    ) -> List[PipelineFrameResult]:
        """
        Execute end-to-end recognition pipeline on an incoming video frame.

        Args:
            image: BGR image array.
            enrolled_gallery: List of (student_id, template_id, vector) tuples.
            matching_threshold: Optional override for matching threshold.

        Returns:
            List of PipelineFrameResult for all detected faces in the frame.
        """
        detected_faces = self.detector.detect_faces(image)

        if not detected_faces:
            return []

        results = []
        for face in detected_faces:
            # 1. Align face patch
            aligned_crop = self.aligner.align(image, face.landmarks, crop_size=112)

            # 2. Quality assessment
            quality_res = self.quality_assessor.assess_quality(aligned_crop, bbox=face.bbox)

            if not quality_res.is_acceptable:
                results.append(
                    PipelineFrameResult(
                        face_found=True,
                        quality_result=quality_res,
                        match_result=MatchResult(
                            is_known=False,
                            matched_student_id=None,
                            confidence_score=0.0,
                            distance=1.0,
                        ),
                        bounding_box=face.bbox,
                        embedding=None,
                    )
                )
                continue

            # 3. Embedding extraction
            embedding_vec = self.embedder.extract_embedding(aligned_crop)

            # 4. Identity matching against enrolled gallery
            match_res = self.matcher.match(
                query_embedding=embedding_vec,
                enrolled_embeddings=enrolled_gallery,
                threshold=matching_threshold,
            )

            results.append(
                PipelineFrameResult(
                    face_found=True,
                    quality_result=quality_res,
                    match_result=match_res,
                    bounding_box=face.bbox,
                    embedding=embedding_vec,
                )
            )

        return results
