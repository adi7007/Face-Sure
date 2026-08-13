"""
Facial Alignment and Affine Transformation module.

Aligns detected faces to canonical 112x112 pixel crop patches using
5-point similarity transformation matrices.
"""

import cv2
import numpy as np


class FaceAligner:
    """
    Performs 5-point landmark affine alignment to standard ArcFace 112x112 layout.
    """

    # Standard ArcFace 112x112 target landmark reference points
    REFERENCE_LANDMARKS_112 = np.array(
        [
            [38.2946, 51.6963],  # Right Eye
            [73.5318, 51.5014],  # Left Eye
            [56.0252, 71.7366],  # Nose Tip
            [41.5493, 92.3655],  # Right Mouth Corner
            [70.7299, 92.2041],  # Left Mouth Corner
        ],
        dtype=np.float32,
    )

    def align(self, image: np.ndarray, landmarks: np.ndarray, crop_size: int = 112) -> np.ndarray:
        """
        Align and crop face patch using 5-point similarity transformation.

        Args:
            image: Original BGR image (H, W, 3).
            landmarks: Detected 5 landmark coordinates, shape (5, 2).
            crop_size: Output square dimensions (default 112).

        Returns:
            Aligned BGR face crop array of shape (crop_size, crop_size, 3).
        """
        if landmarks is None or len(landmarks) != 5:
            # Fallback to simple crop if landmarks unavailable
            h, w = image.shape[:2]
            return cv2.resize(image, (crop_size, crop_size))

        # Estimate partial affine similarity matrix
        tfm, _ = cv2.estimateAffinePartial2D(
            landmarks.astype(np.float32),
            self.REFERENCE_LANDMARKS_112,
        )

        if tfm is None:
            return cv2.resize(image, (crop_size, crop_size))

        aligned_crop = cv2.warpAffine(
            image,
            tfm,
            (crop_size, crop_size),
            flags=cv2.INTER_LINEAR,
            borderValue=0,
        )

        return aligned_crop
