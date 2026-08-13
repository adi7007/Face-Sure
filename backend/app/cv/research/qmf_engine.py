"""
Quality-Aware Multi-Factor Confidence Scoring (QMF-Score) Research Engine.

Implements the novel research contribution specified in docs/Research_Paper/research_methodology.md:
1. Dynamic Quality-Adaptive Thresholding: tau(Q) = tau_base + lambda * (1.0 - Q_sample)
2. Multi-Factor Composite Scoring: C(x) = alpha * S_match + beta * Q_sample + gamma * L_live
3. Multi-Stage Decision Gate Protocol
"""

import uuid
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
import numpy as np

from app.cv.research.config import QMFConfig, TelemetryRecord


@dataclass
class QMFDecisionResult:
    """Output of QMF-Score decision evaluation."""

    decision: str  # "AUTHENTICATED" | "SPOOF_REJECTED" | "QUALITY_REJECTED" | "UNKNOWN_REJECTED"
    matched_student_id: Optional[str]
    similarity_score: float
    quality_score: float
    liveness_score: float
    composite_score: float
    dynamic_threshold: float
    telemetry: TelemetryRecord


class QMFScoreEngine:
    """
    Proposed Research Engine executing Quality-Aware Multi-Factor Decision Fusion.
    """

    def __init__(self, config: Optional[QMFConfig] = None):
        self.config = config if config is not None else QMFConfig()

    def compute_dynamic_threshold(self, quality_score: float) -> float:
        """
        Calculate dynamic adaptive similarity threshold tau(Q).

        tau(Q) = tau_base + lambda * (1.0 - Q_sample)

        Args:
            quality_score: Sample face quality Q in [0.0, 1.0].

        Returns:
            Adaptive threshold tau(Q). High quality -> lower threshold, Low quality -> stricter threshold.
        """
        Q_clamped = float(np.clip(quality_score, 0.0, 1.0))
        tau_Q = self.config.tau_base + self.config.lambda_param * (1.0 - Q_clamped)
        return float(tau_Q)

    def compute_composite_score(self, similarity_score: float, quality_score: float, liveness_score: float) -> float:
        """
        Calculate Multi-Factor Composite Score C(x).

        C(x) = alpha * S_match + beta * Q_sample + gamma * L_live

        Args:
            similarity_score: ArcFace cosine similarity S in [0.0, 1.0].
            quality_score: Face quality Q in [0.0, 1.0].
            liveness_score: FAS liveness L in [0.0, 1.0].

        Returns:
            Composite score C(x) in [0.0, 1.0].
        """
        S = float(np.clip(similarity_score, 0.0, 1.0))
        Q = float(np.clip(quality_score, 0.0, 1.0))
        L = float(np.clip(liveness_score, 0.0, 1.0))

        C = (
            self.config.alpha_weight * S
            + self.config.beta_weight * Q
            + self.config.gamma_weight * L
        )
        return float(np.clip(C, 0.0, 1.0))

    def evaluate_decision(
        self,
        similarity_score: float,
        quality_score: float,
        liveness_score: float,
        candidate_student_id: Optional[str],
    ) -> QMFDecisionResult:
        """
        Execute multi-factor decision gate logic and generate complete telemetry record.

        Args:
            similarity_score: Top cosine similarity score.
            quality_score: Sample face quality score.
            liveness_score: FAS liveness score.
            candidate_student_id: Matched candidate student ID.

        Returns:
            QMFDecisionResult with decision classification and full telemetry record.
        """
        pred_id = f"QMF-PRED-{uuid.uuid4().hex[:10].upper()}"
        tau_Q = self.compute_dynamic_threshold(quality_score)
        composite_score = self.compute_composite_score(similarity_score, quality_score, liveness_score)

        # Gate 1: Hard Liveness Gate
        if liveness_score < self.config.tau_liveness_min:
            decision = "SPOOF_REJECTED"
            matched_id = None

        # Gate 2: Hard Quality Gate
        elif quality_score < self.config.tau_quality_min:
            decision = "QUALITY_REJECTED"
            matched_id = None

        # Gate 3: Dynamic Adaptive Similarity & Composite Fusion Gate
        elif similarity_score >= tau_Q and composite_score >= self.config.tau_composite_min and candidate_student_id:
            decision = "AUTHENTICATED"
            matched_id = candidate_student_id

        # Fallback: Unknown / Insufficient Similarity
        else:
            decision = "UNKNOWN_REJECTED"
            matched_id = None

        telemetry = TelemetryRecord(
            prediction_id=pred_id,
            pipeline_type="PROPOSED_QMF",
            similarity_score=similarity_score,
            quality_score=quality_score,
            liveness_score=liveness_score,
            composite_score=composite_score,
            dynamic_threshold=tau_Q,
            final_decision=decision,
            matched_student_id=matched_id,
            threshold_parameters={
                "tau_base": self.config.tau_base,
                "lambda_param": self.config.lambda_param,
                "tau_quality_min": self.config.tau_quality_min,
                "tau_liveness_min": self.config.tau_liveness_min,
                "tau_composite_min": self.config.tau_composite_min,
            },
            model_version=self.config.model_version,
            experimental_config={
                "alpha_weight": self.config.alpha_weight,
                "beta_weight": self.config.beta_weight,
                "gamma_weight": self.config.gamma_weight,
            },
        )

        return QMFDecisionResult(
            decision=decision,
            matched_student_id=matched_id,
            similarity_score=similarity_score,
            quality_score=quality_score,
            liveness_score=liveness_score,
            composite_score=composite_score,
            dynamic_threshold=tau_Q,
            telemetry=telemetry,
        )
