"""
Independent Unit Tests for Face Quality Assessment and Liveness Detection:
- Multi-factor Quality Assessor (blur, size, contrast, brightness, pose, symmetry)
- Configurable quality thresholds
- Liveness Detector (genuine face, printed photo spoof, screen replay glare, static motion)
"""

import pytest
import numpy as np
import cv2

from app.cv import QualityAssessor, QualityThresholds, LivenessDetector


def create_test_face(seed: int = 42, width: int = 112, height: int = 112, blur: int = 0, glare: bool = False) -> np.ndarray:
    """Helper to generate synthetic test face crops."""
    np.random.seed(seed)
    img = np.ones((height, width, 3), dtype=np.uint8) * 160
    
    # Head & features
    center = (width // 2, height // 2)
    cv2.ellipse(img, center, (width // 3, height // 2 - 5), 0, 0, 360, (200, 170, 140), -1)
    
    # Eyes
    cv2.circle(img, (width // 3, height // 3), 8, (20, 20, 20), -1)
    cv2.circle(img, (2 * width // 3, height // 3), 8, (20, 20, 20), -1)
    
    # Nose & Mouth
    cv2.line(img, (width // 2, height // 3 + 5), (width // 2, height // 2 + 5), (100, 70, 50), 3)
    cv2.ellipse(img, (width // 2, height // 2 + 25), (18, 6), 0, 0, 180, (50, 20, 80), 3)
    
    if blur > 1:
        img = cv2.GaussianBlur(img, (blur, blur), 0)
        
    if glare:
        # Add saturated glare spot (digital screen specular reflection)
        cv2.rectangle(img, (width // 4, height // 4), (3 * width // 4, 3 * height // 4), (255, 255, 255), -1)
        
    return img


# ── Quality Assessor Tests ───────────────────────────────────────────────────

def test_quality_assessor_high_quality():
    """Test quality assessor approves high-quality sharp face image."""
    assessor = QualityAssessor()
    face = create_test_face(seed=10)
    
    res = assessor.assess_quality(face)
    assert res.is_acceptable is True
    assert res.quality_score > 0.40
    assert res.rejection_reason == ""


def test_quality_assessor_configurable_thresholds():
    """Test quality assessor respects custom QualityThresholds configuration."""
    custom_thresholds = QualityThresholds(
        min_sharpness=2000.0,  # High threshold exceeding test face sharpness
        min_face_width=60,
    )
    assessor = QualityAssessor(thresholds=custom_thresholds)
    face = create_test_face(seed=10)
    
    res = assessor.assess_quality(face)
    assert res.is_acceptable is False
    assert "blur" in res.rejection_reason.lower()


def test_quality_assessor_pose_estimation():
    """Test facial pose yaw & pitch angle estimation."""
    assessor = QualityAssessor()
    
    # Landmarks rotated to extreme left yaw
    rotated_landmarks = np.array([
        [20.0, 40.0],  # Right Eye shifted far left
        [40.0, 40.0],  # Left Eye
        [25.0, 60.0],  # Nose
        [20.0, 80.0],  # Right Mouth
        [40.0, 80.0],  # Left Mouth
    ], dtype=np.float32)
    
    yaw, pitch = assessor.estimate_pose(rotated_landmarks)
    assert abs(yaw) > 15.0  # Detects yaw rotation


# ── Liveness Detector Tests ──────────────────────────────────────────────────

def test_liveness_detector_genuine_face():
    """Test liveness detector classifies genuine face image as LIVE."""
    detector = LivenessDetector(min_liveness_threshold=0.35)
    genuine_face = create_test_face(seed=77)
    
    res = detector.assess_liveness(genuine_face)
    assert res.is_live is True
    assert res.status == "LIVE"
    assert res.liveness_score >= 0.35


def test_liveness_detector_digital_screen_spoof():
    """Test liveness detector flags screen glare as SPOOF_SCREEN."""
    detector = LivenessDetector()
    glare_face = create_test_face(seed=77, glare=True)
    
    res = detector.assess_liveness(glare_face)
    assert res.is_live is False
    assert res.status == "SPOOF_SCREEN"
    assert "specular" in res.rejection_reason.lower() or "glare" in res.rejection_reason.lower()


def test_liveness_detector_printed_photo_spoof():
    """Test liveness detector flags low high-frequency FFT photo as SPOOF_PRINT."""
    detector = LivenessDetector(fft_cutoff_threshold=0.50)  # Strict cutoff
    blurry_photo = create_test_face(seed=77, blur=25)
    
    res = detector.assess_liveness(blurry_photo)
    assert res.is_live is False
    assert res.status in ["SPOOF_PRINT", "FAILED_LIVENESS"]
    assert len(res.rejection_reason) > 0


def test_liveness_detector_static_motion():
    """Test landmark motion analyzer detects static photo presentation."""
    detector = LivenessDetector()
    
    # 5 identical frames (zero motion variance)
    static_landmarks = [np.array([[30, 40], [70, 40], [50, 60], [35, 80], [65, 80]])] * 5
    motion_score = detector.analyze_landmark_motion(static_landmarks)
    
    assert motion_score < 0.50  # Low score due to lack of natural micro-movements
