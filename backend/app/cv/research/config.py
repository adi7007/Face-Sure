"""
Experiment Configuration & Prediction Telemetry System.

Provides configurable parameters for both Baseline and Proposed QMF-Score pipelines
and defines the complete TelemetryRecord schema for empirical analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass
class BaselineConfig:
    """Configuration for Baseline Recognition Pipeline."""

    pipeline_name: str = "Baseline_Fixed_Threshold"
    model_version: str = "v1.0.0-Baseline"
    fixed_similarity_threshold: float = 0.60
    min_face_size: int = 40


@dataclass
class QMFConfig:
    """Configuration for Proposed Quality-Aware Multi-Factor (QMF-Score) Pipeline."""

    pipeline_name: str = "Proposed_QMF_Score"
    model_version: str = "v2.0.0-QMF"
    
    # Dynamic Adaptive Threshold Parameters: tau(Q) = tau_base + lambda * (1.0 - Q_sample)
    tau_base: float = 0.55
    lambda_param: float = 0.15
    
    # Hard Cutoff Thresholds
    tau_quality_min: float = 0.30
    tau_liveness_min: float = 0.50
    tau_composite_min: float = 0.55

    # Multi-Factor Composite Weights (alpha + beta + gamma = 1.0)
    alpha_weight: float = 0.50  # Match Similarity weight
    beta_weight: float = 0.30   # Quality Score weight
    gamma_weight: float = 0.20  # Liveness Score weight


@dataclass
class TelemetryRecord:
    """Comprehensive telemetry recorded for every prediction."""

    prediction_id: str
    pipeline_type: str  # "BASELINE" | "PROPOSED_QMF"
    
    # Biometric Telemetry
    similarity_score: float
    quality_score: float
    liveness_score: float
    composite_score: float
    dynamic_threshold: float
    
    # Final Decision
    final_decision: str  # "AUTHENTICATED" | "SPOOF_REJECTED" | "QUALITY_REJECTED" | "UNKNOWN_REJECTED"
    matched_student_id: Optional[str]
    
    # Parameters & Model Metadata
    threshold_parameters: Dict[str, Any] = field(default_factory=dict)
    model_version: str = ""
    experimental_config: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
