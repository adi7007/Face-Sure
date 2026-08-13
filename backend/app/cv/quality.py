"""
Advanced Face Quality Assessment (FQA) Module.

Evaluates multi-factor image quality attributes:
1. Blur / Sharpness (Laplacian variance)
2. Brightness (Mean intensity)
3. Contrast (Standard deviation)
4. Face Size & Aspect Ratio (Bounding box resolution)
5. Pose Estimation (Yaw / Pitch angles via eye-nose geometry)
6. Occlusion & Facial Symmetry (Left-right structural similarity)

Produces a normalized quality score Q in [0.0, 1.0] with configurable thresholds.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
import cv2
import numpy as np


@dataclass
class QualityThresholds:
    """Configurable quality assessment thresholds and weights."""

    min_face_width: int = 60
    min_face_height: int = 60
    min_sharpness: float = 40.0
    min_brightness: float = 30.0
    max_brightness: float = 225.0
    min_contrast: float = 25.0
    max_yaw_angle: float = 30.0
    max_pitch_angle: float = 25.0
    min_symmetry_score: float = 0.50

    # Composite weights (sum to 1.0)
    weight_sharpness: float = 0.30
    weight_brightness: float = 0.15
    weight_contrast: float = 0.15
    weight_size: float = 0.15
    weight_pose: float = 0.15
    weight_symmetry: float = 0.10


@dataclass
class QualityResult:
    """Detailed quality assessment metrics breakdown."""

    is_acceptable: bool
    quality_score: float  # Composite quality in [0.0, 1.0]
    sharpness_score: float
    brightness_score: float
    contrast_score: float
    size_score: float
    pose_score: float
    symmetry_score: float
    face_width: int
    face_height: int
    estimated_yaw: float
    estimated_pitch: float
    rejection_reason: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


class QualityAssessor:
    """
    Multi-Factor Face Quality Assessor with configurable thresholds.
    """

    def __init__(
        self,
        thresholds: Optional[QualityThresholds] = None,
        min_face_size: Optional[int] = None,
        min_laplacian_variance: Optional[float] = None,
        min_brightness: Optional[float] = None,
        max_brightness: Optional[float] = None,
    ):
        if thresholds is not None:
            self.config = thresholds
        else:
            self.config = QualityThresholds()

        if min_face_size is not None:
            self.config.min_face_width = min_face_size
            self.config.min_face_height = min_face_size
        if min_laplacian_variance is not None:
            self.config.min_sharpness = min_laplacian_variance
        if min_brightness is not None:
            self.config.min_brightness = min_brightness
        if max_brightness is not None:
            self.config.max_brightness = max_brightness

    def estimate_pose(self, landmarks: np.ndarray) -> Tuple[float, float]:
        """
        Estimate facial yaw and pitch angles from 5-point landmarks.

        Args:
            landmarks: Shape (5, 2) - [right_eye, left_eye, nose, right_mouth, left_mouth]

        Returns:
            Tuple of (yaw_degrees, pitch_degrees).
        """
        if landmarks is None or len(landmarks) != 5:
            return 0.0, 0.0

        r_eye, l_eye, nose, r_mouth, l_mouth = landmarks

        # Eye midpoint
        eye_center = (r_eye + l_eye) / 2.0
        eye_dist = float(np.linalg.norm(l_eye - r_eye))
        if eye_dist < 1e-5:
            return 0.0, 0.0

        # Horizontal offset of nose from eye center -> Yaw
        eye_to_nose_x = nose[0] - eye_center[0]
        yaw_ratio = eye_to_nose_x / eye_dist
        yaw_deg = float(np.clip(yaw_ratio * 90.0, -90.0, 90.0))

        # Vertical offset of nose relative to mouth -> Pitch
        mouth_center = (r_mouth + l_mouth) / 2.0
        nose_to_mouth_y = mouth_center[1] - nose[1]
        eye_to_nose_y = nose[1] - eye_center[1]
        if eye_to_nose_y < 1e-5:
            pitch_deg = 0.0
        else:
            vertical_ratio = (nose_to_mouth_y / eye_to_nose_y) - 1.2
            pitch_deg = float(np.clip(vertical_ratio * 45.0, -45.0, 45.0))

        return yaw_deg, pitch_deg

    def evaluate_symmetry(self, face_crop: np.ndarray) -> float:
        """
        Evaluate facial symmetry by comparing left and right image halves.

        Returns:
            Symmetry score in [0.0, 1.0].
        """
        if face_crop is None or face_crop.size == 0:
            return 0.0

        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop
        h, w = gray.shape
        half_w = w // 2

        left_half = gray[:, :half_w]
        right_half = cv2.flip(gray[:, half_w : 2 * half_w], 1)

        if left_half.shape != right_half.shape or left_half.size == 0:
            return 0.50

        # Normalize halves
        l_norm = cv2.normalize(left_half.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
        r_norm = cv2.normalize(right_half.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)

        mse = float(np.mean((l_norm - r_norm) ** 2))
        symmetry_score = max(0.0, 1.0 - (mse * 4.0))
        return float(symmetry_score)

    def assess_quality(
        self,
        face_crop: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]] = None,
        landmarks: Optional[np.ndarray] = None,
    ) -> QualityResult:
        """
        Execute comprehensive multi-factor quality assessment.

        Args:
            face_crop: BGR aligned face crop patch.
            bbox: Bounding box tuple (x1, y1, x2, y2).
            landmarks: 5-point facial landmark array.

        Returns:
            QualityResult detailing pass/fail status and component scores.
        """
        if face_crop is None or face_crop.size == 0:
            return QualityResult(
                is_acceptable=False,
                quality_score=0.0,
                sharpness_score=0.0,
                brightness_score=0.0,
                contrast_score=0.0,
                size_score=0.0,
                pose_score=0.0,
                symmetry_score=0.0,
                face_width=0,
                face_height=0,
                estimated_yaw=0.0,
                estimated_pitch=0.0,
                rejection_reason="Empty face crop patch",
            )

        h, w = face_crop.shape[:2]
        face_w = (bbox[2] - bbox[0]) if bbox else w
        face_h = (bbox[3] - bbox[1]) if bbox else h
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop

        # 1. Size Assessment
        size_score = min(1.0, (face_w * face_h) / (112.0 * 112.0))
        if face_w < self.config.min_face_width or face_h < self.config.min_face_height:
            return QualityResult(
                is_acceptable=False,
                quality_score=size_score * 0.2,
                sharpness_score=0.0,
                brightness_score=0.0,
                contrast_score=0.0,
                size_score=size_score,
                pose_score=0.0,
                symmetry_score=0.0,
                face_width=face_w,
                face_height=face_h,
                estimated_yaw=0.0,
                estimated_pitch=0.0,
                rejection_reason=f"Face resolution ({face_w}x{face_h}) below threshold ({self.config.min_face_width}px)",
            )

        # 2. Sharpness / Blur (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_score = min(1.0, laplacian_var / 250.0)
        if laplacian_var < self.config.min_sharpness:
            return QualityResult(
                is_acceptable=False,
                quality_score=sharpness_score * 0.3,
                sharpness_score=sharpness_score,
                brightness_score=0.0,
                contrast_score=0.0,
                size_score=size_score,
                pose_score=0.0,
                symmetry_score=0.0,
                face_width=face_w,
                face_height=face_h,
                estimated_yaw=0.0,
                estimated_pitch=0.0,
                rejection_reason=f"Image blur detected (Laplacian variance {laplacian_var:.1f} < {self.config.min_sharpness})",
            )

        # 3. Brightness Assessment
        mean_brightness = float(np.mean(gray))
        brightness_score = max(0.0, 1.0 - abs(mean_brightness - 128.0) / 128.0)
        if mean_brightness < self.config.min_brightness or mean_brightness > self.config.max_brightness:
            return QualityResult(
                is_acceptable=False,
                quality_score=brightness_score * 0.3,
                sharpness_score=sharpness_score,
                brightness_score=brightness_score,
                contrast_score=0.0,
                size_score=size_score,
                pose_score=0.0,
                symmetry_score=0.0,
                face_width=face_w,
                face_height=face_h,
                estimated_yaw=0.0,
                estimated_pitch=0.0,
                rejection_reason=f"Poor lighting (Mean brightness {mean_brightness:.1f})",
            )

        # 4. Contrast Assessment
        std_contrast = float(np.std(gray))
        contrast_score = min(1.0, std_contrast / 64.0)
        if std_contrast < self.config.min_contrast:
            return QualityResult(
                is_acceptable=False,
                quality_score=contrast_score * 0.3,
                sharpness_score=sharpness_score,
                brightness_score=brightness_score,
                contrast_score=contrast_score,
                size_score=size_score,
                pose_score=0.0,
                symmetry_score=0.0,
                face_width=face_w,
                face_height=face_h,
                estimated_yaw=0.0,
                estimated_pitch=0.0,
                rejection_reason=f"Low image contrast (Std dev {std_contrast:.1f} < {self.config.min_contrast})",
            )

        # 5. Pose Estimation
        yaw, pitch = self.estimate_pose(landmarks) if landmarks is not None else (0.0, 0.0)
        pose_penalty = max(abs(yaw) / self.config.max_yaw_angle, abs(pitch) / self.config.max_pitch_angle)
        pose_score = max(0.0, 1.0 - pose_penalty)
        if abs(yaw) > self.config.max_yaw_angle or abs(pitch) > self.config.max_pitch_angle:
            return QualityResult(
                is_acceptable=False,
                quality_score=pose_score * 0.4,
                sharpness_score=sharpness_score,
                brightness_score=brightness_score,
                contrast_score=contrast_score,
                size_score=size_score,
                pose_score=pose_score,
                symmetry_score=0.0,
                face_width=face_w,
                face_height=face_h,
                estimated_yaw=yaw,
                estimated_pitch=pitch,
                rejection_reason=f"Excessive head pose rotation (Yaw: {yaw:.1f}°, Pitch: {pitch:.1f}°)",
            )

        # 6. Symmetry & Occlusion
        symmetry_score = self.evaluate_symmetry(face_crop)

        # Compute Normalized Weighted Composite Score Q in [0.0, 1.0]
        Q = float(
            self.config.weight_sharpness * sharpness_score
            + self.config.weight_brightness * brightness_score
            + self.config.weight_contrast * contrast_score
            + self.config.weight_size * size_score
            + self.config.weight_pose * pose_score
            + self.config.weight_symmetry * symmetry_score
        )
        Q_normalized = float(np.clip(Q, 0.0, 1.0))

        return QualityResult(
            is_acceptable=True,
            quality_score=Q_normalized,
            sharpness_score=sharpness_score,
            brightness_score=brightness_score,
            contrast_score=contrast_score,
            size_score=size_score,
            pose_score=pose_score,
            symmetry_score=symmetry_score,
            face_width=face_w,
            face_height=face_h,
            estimated_yaw=yaw,
            estimated_pitch=pitch,
            rejection_reason="",
            metrics={
                "laplacian_variance": laplacian_var,
                "mean_brightness": mean_brightness,
                "std_contrast": std_contrast,
            },
        )
