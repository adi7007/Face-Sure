"""
Comprehensive Unit & Integration Test Suite for Research Pipelines:
- Dynamic Threshold Computation tau(Q)
- Multi-Factor Composite Scoring C(x)
- Side-by-Side Evaluation (Baseline vs Proposed QMF Pipeline)
- Spoof Rejection vs Fraudulent Baseline Authentication
- Telemetry Record Validation
"""

import pytest
import numpy as np
import cv2

from app.cv import FaceEmbedder
from app.cv.research import (
    BaselineConfig,
    QMFConfig,
    TelemetryRecord,
    QMFScoreEngine,
    BaselinePipeline,
    ProposedQMFPipeline,
)


def create_test_image(seed: int = 10, blur: int = 0, glare: bool = False) -> np.ndarray:
    """Generate synthetic image for pipeline evaluation."""
    np.random.seed(seed)
    img = np.ones((300, 300, 3), dtype=np.uint8) * 200
    center = (150, 150)
    
    # Face
    cv2.ellipse(img, center, (75, 100), 0, 0, 360, (180, 150, 120), -1)
    # Eyes
    cv2.circle(img, (110, 120), 12, (20, 20, 20), -1)
    cv2.circle(img, (190, 120), 12, (20, 20, 20), -1)
    # Nose & Mouth
    cv2.line(img, (150, 130), (150, 160), (100, 70, 50), 4)
    cv2.ellipse(img, (150, 190), (25, 8), 0, 0, 180, (40, 20, 80), 4)
    
    if blur > 1:
        img = cv2.GaussianBlur(img, (blur, blur), 0)
    if glare:
        cv2.rectangle(img, (80, 80), (220, 220), (255, 255, 255), -1)
        
    return img


def test_qmf_engine_dynamic_threshold():
    """Verify tau(Q) = tau_base + lambda * (1 - Q)."""
    engine = QMFScoreEngine(config=QMFConfig(tau_base=0.55, lambda_param=0.15))
    
    # High quality (Q = 1.0) -> tau(Q) = 0.55
    tau_high = engine.compute_dynamic_threshold(1.0)
    assert abs(tau_high - 0.55) < 1e-5
    
    # Moderate quality (Q = 0.50) -> tau(Q) = 0.55 + 0.15 * 0.5 = 0.625
    tau_mid = engine.compute_dynamic_threshold(0.50)
    assert abs(tau_mid - 0.625) < 1e-5
    
    # Low quality (Q = 0.0) -> tau(Q) = 0.55 + 0.15 * 1.0 = 0.70
    tau_low = engine.compute_dynamic_threshold(0.0)
    assert abs(tau_low - 0.70) < 1e-5


def test_qmf_engine_composite_score():
    """Verify C(x) = alpha * S + beta * Q + gamma * L."""
    engine = QMFScoreEngine(config=QMFConfig(alpha_weight=0.50, beta_weight=0.30, gamma_weight=0.20))
    
    composite = engine.compute_composite_score(similarity_score=0.80, quality_score=0.90, liveness_score=0.95)
    # Expected: 0.5*0.8 + 0.3*0.9 + 0.2*0.95 = 0.40 + 0.27 + 0.19 = 0.86
    assert abs(composite - 0.86) < 1e-4


def test_qmf_engine_gate_decisions():
    """Test multi-stage decision gate classifications."""
    engine = QMFScoreEngine()
    
    # 1. Spoof attack -> SPOOF_REJECTED
    res_spoof = engine.evaluate_decision(
        similarity_score=0.90, quality_score=0.85, liveness_score=0.20, candidate_student_id="STU-001"
    )
    assert res_spoof.decision == "SPOOF_REJECTED"
    assert res_spoof.matched_student_id is None
    
    # 2. Extremely low quality -> QUALITY_REJECTED
    res_qual = engine.evaluate_decision(
        similarity_score=0.90, quality_score=0.10, liveness_score=0.90, candidate_student_id="STU-001"
    )
    assert res_qual.decision == "QUALITY_REJECTED"
    assert res_qual.matched_student_id is None
    
    # 3. Genuine Match -> AUTHENTICATED
    res_match = engine.evaluate_decision(
        similarity_score=0.85, quality_score=0.88, liveness_score=0.95, candidate_student_id="STU-001"
    )
    assert res_match.decision == "AUTHENTICATED"
    assert res_match.matched_student_id == "STU-001"


def test_baseline_vs_proposed_side_by_side():
    """Side-by-side comparison of Baseline vs Proposed QMF Pipeline."""
    embedder = FaceEmbedder(embedding_dim=512)
    sample_img = create_test_image(seed=50)
    sample_crop = cv2.resize(sample_img, (112, 112))
    vec = embedder.extract_embedding(sample_crop)
    
    gallery = [("STU-100", "TMPL-1", vec)]
    
    # Run Baseline
    baseline = BaselinePipeline()
    base_telemetry = baseline.process_frame(sample_img, gallery)
    assert len(base_telemetry) >= 1
    base_rec = base_telemetry[0]
    assert base_rec.pipeline_type == "BASELINE"
    assert base_rec.final_decision == "AUTHENTICATED"
    
    # Run Proposed QMF
    proposed = ProposedQMFPipeline()
    proposed_results = proposed.process_frame(sample_img, gallery)
    assert len(proposed_results) >= 1
    prop_res = proposed_results[0]
    assert prop_res.telemetry.pipeline_type == "PROPOSED_QMF"
    assert prop_res.decision == "AUTHENTICATED"
    assert prop_res.matched_student_id == "STU-100"


def test_telemetry_recording_completeness():
    """Verify all mandatory telemetry attributes are populated."""
    proposed = ProposedQMFPipeline()
    embedder = FaceEmbedder(embedding_dim=512)
    
    sample_img = create_test_image(seed=30)
    vec = embedder.extract_embedding(cv2.resize(sample_img, (112, 112)))
    gallery = [("STU-TEST", "TMPL-1", vec)]
    
    results = proposed.process_frame(sample_img, gallery)
    assert len(results) >= 1
    t = results[0].telemetry
    
    # Mandatory field verification
    assert t.prediction_id.startswith("QMF-PRED-")
    assert t.pipeline_type == "PROPOSED_QMF"
    assert len(t.timestamp) > 0
    assert 0.0 <= t.similarity_score <= 1.0
    assert 0.0 <= t.quality_score <= 1.0
    assert 0.0 <= t.liveness_score <= 1.0
    assert 0.0 <= t.composite_score <= 1.0
    assert 0.0 <= t.dynamic_threshold <= 1.0
    assert t.final_decision in ["AUTHENTICATED", "SPOOF_REJECTED", "QUALITY_REJECTED", "UNKNOWN_REJECTED"]
    assert "tau_base" in t.threshold_parameters
    assert "alpha_weight" in t.experimental_config
