"""
Computer Vision pipeline package init.
"""

from app.cv.detector import FaceDetector, DetectedFace
from app.cv.aligner import FaceAligner
from app.cv.quality import QualityAssessor, QualityResult, QualityThresholds
from app.cv.embedder import FaceEmbedder
from app.cv.matcher import FaceMatcher, MatchResult
from app.cv.liveness import LivenessDetector, LivenessResult
from app.cv.pipeline import RecognitionPipeline, PipelineFrameResult

__all__ = [
    "FaceDetector",
    "DetectedFace",
    "FaceAligner",
    "QualityAssessor",
    "QualityResult",
    "QualityThresholds",
    "FaceEmbedder",
    "FaceMatcher",
    "MatchResult",
    "LivenessDetector",
    "LivenessResult",
    "RecognitionPipeline",
    "PipelineFrameResult",
]
