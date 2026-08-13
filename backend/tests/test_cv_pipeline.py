"""
Comprehensive tests for the Facial Recognition Pipeline:
- Face Detection & Alignment
- Quality Assessment
- Embedding Extraction & L2 Normalization
- Known Face Recognition
- Unknown Face Rejection
- Multi-Student Gallery Matching
- Poor Quality Image Filtering
"""

import pytest
import numpy as np
import cv2

from app.cv import (
    FaceDetector,
    FaceAligner,
    QualityAssessor,
    FaceEmbedder,
    FaceMatcher,
    RecognitionPipeline,
)


def create_synthetic_face_image(seed: int = 1, width: int = 300, height: int = 300, blur_ksize: int = 0) -> np.ndarray:
    """Helper to generate a deterministic synthetic face image with seed-dependent structural variance."""
    np.random.seed(seed)
    bg_color = int(180 + (seed * 13) % 70)
    img = np.ones((height, width, 3), dtype=np.uint8) * bg_color
    
    # Head ellipse with seed-dependent geometry
    center = (width // 2, height // 2)
    axes = (int(width // 4 + (seed % 15)), int(height // 3 + (seed % 20)))
    skin_color = (int(140 + (seed * 7) % 80), int(120 + (seed * 11) % 60), int(100 + (seed * 17) % 50))
    cv2.ellipse(img, center, axes, 0, 0, 360, skin_color, -1)
    
    # Eyes with seed-dependent offset
    eye_offset_x = int(width // 8 + (seed % 10))
    eye_y = int(height // 2 - height // 10 + (seed % 8))
    eye_size = int(12 + (seed % 8))
    cv2.circle(img, (center[0] - eye_offset_x, eye_y), eye_size, (20, 20, 20), -1)
    cv2.circle(img, (center[0] + eye_offset_x, eye_y), eye_size, (20, 20, 20), -1)
    
    # Nose
    nose_w = int(8 + (seed % 10))
    nose_pts = np.array([
        [center[0], eye_y + 10],
        [center[0] - nose_w, eye_y + 35 + (seed % 10)],
        [center[0] + nose_w, eye_y + 35 + (seed % 10)]
    ], dtype=np.int32)
    cv2.fillPoly(img, [nose_pts], (80, 60, 40))
    
    # Mouth
    mouth_y = eye_y + 65 + (seed % 12)
    cv2.ellipse(img, (center[0], mouth_y), (int(25 + seed % 15), 10), 0, 0, 180, (40, 20, 80), 4)
    
    if blur_ksize > 1:
        img = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
        
    return img


def test_face_detector():
    """Test face detector locates bounding boxes and 5 landmarks."""
    detector = FaceDetector(min_detection_confidence=0.5)
    image = create_synthetic_face_image(seed=10)
    
    faces = detector.detect_faces(image)
    assert len(faces) >= 1
    face = faces[0]
    
    assert len(face.bbox) == 4
    assert face.bbox[2] > face.bbox[0]
    assert face.bbox[3] > face.bbox[1]
    assert face.landmarks.shape == (5, 2)


def test_face_aligner():
    """Test face aligner outputs standardized 112x112 crop patch."""
    aligner = FaceAligner()
    image = create_synthetic_face_image(seed=12)
    landmarks = np.array([[100, 100], [180, 100], [140, 140], [110, 180], [170, 180]], dtype=np.float32)
    
    crop = aligner.align(image, landmarks, crop_size=112)
    assert crop.shape == (112, 112, 3)


def test_quality_assessor_acceptable():
    """Test quality assessor accepts high-quality sharp face images."""
    assessor = QualityAssessor(min_face_size=50, min_laplacian_variance=30.0)
    sharp_image = create_synthetic_face_image(seed=14, blur_ksize=0)
    
    res = assessor.assess_quality(sharp_image)
    assert res.is_acceptable is True
    assert res.quality_score > 0.3
    assert res.rejection_reason == ""


def test_quality_assessor_rejection_blur():
    """Test quality assessor rejects heavily blurred face images."""
    assessor = QualityAssessor(min_face_size=50, min_laplacian_variance=500.0)
    blurry_image = create_synthetic_face_image(seed=14, blur_ksize=31)
    
    res = assessor.assess_quality(blurry_image)
    assert res.is_acceptable is False
    assert "blurry" in res.rejection_reason.lower()


def test_face_embedder_normalization():
    """Test face embedder returns L2-normalized 512D feature vectors."""
    embedder = FaceEmbedder(embedding_dim=512)
    crop = create_synthetic_face_image(seed=20, width=112, height=112)
    
    embedding = embedder.extract_embedding(crop)
    assert embedding.shape == (512,)
    assert embedding.dtype == np.float32
    
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 1e-4  # L2 unit length test


def test_face_matcher_known_vs_unknown():
    """Test matcher correctly identifies known identity vs unknown imposter."""
    embedder = FaceEmbedder(embedding_dim=512)
    matcher = FaceMatcher(default_threshold=0.60)
    
    # Generate distinct facial crops for 2 students
    student1_crop = create_synthetic_face_image(seed=10, width=112, height=112)
    student2_crop = create_synthetic_face_image(seed=88, width=112, height=112)
    
    vec_student1 = embedder.extract_embedding(student1_crop)
    vec_student2 = embedder.extract_embedding(student2_crop)
    
    enrolled_gallery = [
        ("STU-001", "TMPL-1", vec_student1),
        ("STU-002", "TMPL-2", vec_student2),
    ]
    
    # 1. Test Known Identity Match (STU-001)
    match_result1 = matcher.match(vec_student1, enrolled_gallery)
    assert match_result1.is_known is True
    assert match_result1.matched_student_id == "STU-001"
    assert match_result1.confidence_score >= 0.95
    
    # 2. Test Known Identity Match (STU-002)
    match_result2 = matcher.match(vec_student2, enrolled_gallery)
    assert match_result2.is_known is True
    assert match_result2.matched_student_id == "STU-002"
    assert match_result2.confidence_score >= 0.95
    
    # 3. Test Unknown Imposter Rejection
    imposter_crop = create_synthetic_face_image(seed=555, width=112, height=112)
    vec_imposter = embedder.extract_embedding(imposter_crop)
    
    match_result_imposter = matcher.match(vec_imposter, enrolled_gallery, threshold=0.98)
    assert match_result_imposter.is_known is False
    assert match_result_imposter.matched_student_id is None


def test_recognition_pipeline_end_to_end():
    """Test full Recognition Pipeline end-to-end processing."""
    pipeline = RecognitionPipeline(matching_threshold=0.50)
    embedder = FaceEmbedder(embedding_dim=512)
    
    # Student A registration sample
    student_a_image = create_synthetic_face_image(seed=50)
    vec_a = embedder.extract_embedding(student_a_image)
    gallery = [("STU-ALICE", "T1", vec_a)]
    
    # Pipeline execution on Student A test image
    results = pipeline.process_frame(student_a_image, gallery)
    assert len(results) >= 1
    
    frame_res = results[0]
    assert frame_res.face_found is True
    assert frame_res.quality_result.is_acceptable is True
    assert frame_res.match_result.is_known is True
    assert frame_res.match_result.matched_student_id == "STU-ALICE"
    assert frame_res.match_result.confidence_score >= 0.50
