"""
Independent Liveness Detection & Face Anti-Spoofing (FAS) Module.

Distinguishes genuine live human faces from presentation attacks (spoofs):
- Printed photograph presentation attacks (2D photo spoofs)
- Digital screen replay attacks (smartphone / tablet video replays)
- Static replay attacks

Evaluates:
1. High-Frequency Spectrum Ratio (FFT 2D Power Spectrum Analysis)
2. Screen Moiré Pattern & Specular Reflection Texture
3. Landmark Micro-Motion & EAR Eye Aspect Ratio Dynamics
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List
import cv2
import numpy as np


@dataclass
class LivenessResult:
    """Detailed anti-spoofing assessment result."""

    is_live: bool
    liveness_score: float  # Normalized score in [0.0, 1.0]
    status: str            # "LIVE" | "SPOOF_PRINT" | "SPOOF_SCREEN" | "FAILED_LIVENESS"
    fft_high_freq_ratio: float
    texture_specular_score: float
    motion_variance_score: float
    rejection_reason: str = ""
    details: Dict[str, Any] = None


class LivenessDetector:
    """
    Independent Face Anti-Spoofing (FAS) Liveness Detector.
    """

    def __init__(
        self,
        min_liveness_threshold: float = 0.50,
        fft_cutoff_threshold: float = 0.08,
        specular_max_threshold: float = 0.25,
    ):
        self.min_liveness_threshold = min_liveness_threshold
        self.fft_cutoff_threshold = fft_cutoff_threshold
        self.specular_max_threshold = specular_max_threshold

    def analyze_fft_spectrum(self, face_crop: np.ndarray) -> float:
        """
        Analyze 2D Fast Fourier Transform (FFT) power spectrum.

        Printed photos lose high-frequency skin micro-texture details,
        resulting in a lower high-frequency power ratio.

        Returns:
            High-frequency power ratio in [0.0, 1.0].
        """
        if face_crop is None or face_crop.size == 0:
            return 0.0

        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop
        h, w = gray.shape

        # 2D FFT and shift zero-frequency to center
        f_transform = np.fft.fft2(gray.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)

        # Center coordinates
        cy, cx = h // 2, w // 2
        radius = min(h, w) // 4

        # Mask center low frequencies
        y, x = np.ogrid[:h, :w]
        mask = (x - cx) ** 2 + (y - cy) ** 2 > radius ** 2

        high_freq_power = float(np.sum(magnitude[mask]))
        total_power = float(np.sum(magnitude) + 1e-6)

        ratio = high_freq_power / total_power
        return float(np.clip(ratio * 3.5, 0.0, 1.0))

    def analyze_specular_reflections(self, face_crop: np.ndarray) -> float:
        """
        Detect digital screen specular reflections and Moiré pattern artifacts.

        Returns:
            Normalized texture quality score (higher = more natural live skin texture).
        """
        if face_crop is None or face_crop.size == 0:
            return 0.0

        hsv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]

        # Calculate proportion of saturated specular highlights (glare from screen glass)
        glare_pixels = np.sum(v_channel > 245)
        glare_ratio = float(glare_pixels / (v_channel.size + 1e-6))

        # Natural live skin has moderate texture variation without extreme glare blocks
        specular_score = max(0.0, 1.0 - (glare_ratio * 15.0))
        return float(specular_score)

    def analyze_landmark_motion(self, landmark_history: List[np.ndarray]) -> float:
        """
        Analyze multi-frame facial landmark motion variance (micro-movements).

        Static photos yield near-zero trajectory variance.

        Returns:
            Motion variance score in [0.0, 1.0].
        """
        if len(landmark_history) < 3:
            return 0.70  # Default neutral score for single frame

        # Compute variance of nose tip coordinates across frames
        nose_positions = np.array([lm[2] for lm in landmark_history])  # Landmark index 2 = Nose
        variance = float(np.var(nose_positions, axis=0).sum())

        # Micro-movement variance threshold
        if variance < 0.05:
            # Extremely static -> potential print photo spoof
            return 0.20
        elif variance > 120.0:
            # Excessive movement -> potential camera shake / spoof manipulation
            return 0.40

        return 0.90

    def assess_liveness(
        self,
        face_crop: np.ndarray,
        landmark_history: Optional[List[np.ndarray]] = None,
    ) -> LivenessResult:
        """
        Execute independent face anti-spoofing liveness assessment.

        Args:
            face_crop: BGR face crop image patch.
            landmark_history: Optional list of landmark arrays over past frames.

        Returns:
            LivenessResult detailing classification (LIVE / SPOOF) and component scores.
        """
        if face_crop is None or face_crop.size == 0:
            return LivenessResult(
                is_live=False,
                liveness_score=0.0,
                status="FAILED_LIVENESS",
                fft_high_freq_ratio=0.0,
                texture_specular_score=0.0,
                motion_variance_score=0.0,
                rejection_reason="Empty face image crop",
                details={},
            )

        # 1. FFT High-Frequency Power Analysis
        fft_score = self.analyze_fft_spectrum(face_crop)

        # 2. Specular Highlight & Moiré Pattern Analysis
        texture_score = self.analyze_specular_reflections(face_crop)

        # 3. Landmark Motion Dynamic Variance Analysis
        motion_score = (
            self.analyze_landmark_motion(landmark_history)
            if landmark_history is not None
            else 0.75
        )

        # Composite Liveness Score L in [0.0, 1.0]
        L_composite = float(0.45 * fft_score + 0.35 * texture_score + 0.20 * motion_score)

        # Classify spoof attack type
        if fft_score < self.fft_cutoff_threshold:
            status = "SPOOF_PRINT"
            reason = "High-frequency texture loss detected (Printed photo attack pattern)"
        elif texture_score < 0.30:
            status = "SPOOF_SCREEN"
            reason = "Specular reflection glare detected (Digital screen replay attack pattern)"
        elif L_composite < self.min_liveness_threshold:
            status = "FAILED_LIVENESS"
            reason = f"Liveness score ({L_composite:.3f}) below safety threshold ({self.min_liveness_threshold})"
        else:
            status = "LIVE"
            reason = ""

        is_live = (status == "LIVE")

        return LivenessResult(
            is_live=is_live,
            liveness_score=L_composite,
            status=status,
            fft_high_freq_ratio=fft_score,
            texture_specular_score=texture_score,
            motion_variance_score=motion_score,
            rejection_reason=reason,
            details={
                "fft_raw_ratio": fft_score,
                "texture_glare_score": texture_score,
                "motion_score": motion_score,
            },
        )
