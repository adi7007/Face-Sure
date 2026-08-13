"""
Face Quality Assessment module.

Evaluates physical image quality attributes (blur variance, face size, brightness)
to filter unusable or unidentifiable facial frames.
"""

from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class QualityResult:
    """Quality metrics for a candidate face crop."""

    is_acceptable: bool
    quality_score: float  # Composite quality in [0.0, 1.0]
    laplacian_variance: float
    face_width: int
    face_height: int
    brightness_mean: float
    rejection_reason: str = ""


class QualityAssessor:
    """
    Evaluates image quality metrics to enforce registration and verification standards.
    """

    def __init__(
        self,
        min_face_size: int = 50,
        min_laplacian_variance: float = 40.0,
        min_brightness: float = 30.0,
        max_brightness: float = 235.0,
    ):
        self.min_face_size = min_face_size
        self.min_laplacian_var = min_laplacian_variance
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def assess_quality(self, face_crop: np.ndarray, bbox: tuple[int, int, int, int] | None = None) -> QualityResult:
        """
        Assess face image quality attributes.

        Args:
            face_crop: Aligned BGR face crop array.
            bbox: Optional (x1, y1, x2, y2) bounding box.

        Returns:
            QualityResult containing scores and pass/fail status.
        """
        if face_crop is None or face_crop.size == 0:
            return QualityResult(
                is_acceptable=False,
                quality_score=0.0,
                laplacian_variance=0.0,
                face_width=0,
                face_height=0,
                brightness_mean=0.0,
                rejection_reason="Empty image crop",
            )

        h, w = face_crop.shape[:2]
        face_w = (bbox[2] - bbox[0]) if bbox else w
        face_h = (bbox[3] - bbox[1]) if bbox else h

        # 1. Size Check
        if face_w < self.min_face_size or face_h < self.min_face_size:
            return QualityResult(
                is_acceptable=False,
                quality_score=0.1,
                laplacian_variance=0.0,
                face_width=face_w,
                face_height=face_h,
                brightness_mean=0.0,
                rejection_reason=f"Face size ({face_w}x{face_h}) smaller than minimum ({self.min_face_size}px)",
            )

        # 2. Laplacian Blur Assessment
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        if laplacian_var < self.min_laplacian_var:
            return QualityResult(
                is_acceptable=False,
                quality_score=max(0.0, laplacian_var / 100.0),
                laplacian_variance=laplacian_var,
                face_width=face_w,
                face_height=face_h,
                brightness_mean=float(np.mean(gray)),
                rejection_reason=f"Image too blurry (Laplacian variance {laplacian_var:.1f} < {self.min_laplacian_var})",
            )

        # 3. Brightness Assessment
        brightness_mean = float(np.mean(gray))
        if brightness_mean < self.min_brightness or brightness_mean > self.max_brightness:
            return QualityResult(
                is_acceptable=False,
                quality_score=0.2,
                laplacian_variance=laplacian_var,
                face_width=face_w,
                face_height=face_h,
                brightness_mean=brightness_mean,
                rejection_reason=f"Poor lighting conditions (Mean brightness {brightness_mean:.1f})",
            )

        # Compute normalized composite quality score in [0.0, 1.0]
        norm_sharpness = min(1.0, laplacian_var / 300.0)
        norm_brightness = 1.0 - (abs(brightness_mean - 128.0) / 128.0)
        composite_score = float(0.6 * norm_sharpness + 0.4 * norm_brightness)

        return QualityResult(
            is_acceptable=True,
            quality_score=composite_score,
            laplacian_variance=laplacian_var,
            face_width=face_w,
            face_height=face_h,
            brightness_mean=brightness_mean,
            rejection_reason="",
        )
