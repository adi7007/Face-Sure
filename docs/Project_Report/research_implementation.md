# Chapter 4: Research Contribution Implementation Report

**Document Identifier:** `docs/Project_Report/research_implementation.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 4.1 Overview of Research Implementation

This chapter presents the concrete software implementation of our research contribution: **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score) with Dynamic Thresholding ($\tau(Q)$)**.

To establish defensible academic evaluation, the software repository contains two independently executable pipeline architectures:
1. **Baseline Fixed-Threshold Pipeline:** Represents conventional automated attendance systems utilizing a fixed cosine similarity matching threshold ($\tau_0 = 0.60$) without quality adaptation or liveness verification.
2. **Proposed QMF-Score Pipeline:** Incorporates multi-factor biometric telemetry (ArcFace similarity $S$, quality score $Q$, liveness score $L$) fused through a multi-stage decision gate protocol and dynamic adaptive thresholding ($\tau(Q)$).

---

## 4.2 Mathematical Formulas & Code Equivalence

### 4.2.1 Dynamic Quality-Adaptive Thresholding $\tau(Q)$
Standard fixed-threshold systems suffer from false rejections when streaming video quality fluctuates due to lighting or distance. We implement a dynamic threshold $\tau(Q)$ that relaxes the matching barrier for high-quality crops while tightening it for degraded crops:

$$\tau(Q_{sample}) = \tau_{base} + \lambda \cdot (1.0 - Q_{sample})$$

**Implementation:** [`backend/app/cv/research/qmf_engine.py`](file:///d:/Facial%20Recognition/backend/app/cv/research/qmf_engine.py#L42-L56)
```python
def compute_dynamic_threshold(self, quality_score: float) -> float:
    Q_clamped = float(np.clip(quality_score, 0.0, 1.0))
    tau_Q = self.config.tau_base + self.config.lambda_param * (1.0 - Q_clamped)
    return float(tau_Q)
```

### 4.2.2 Multi-Factor Composite Score $C(x)$
To prevent single-factor spoofing or poor-quality false accepts, predictions are evaluated against a multi-factor composite score $C(x)$:

$$C(x) = \alpha \cdot S_{match} + \beta \cdot Q_{sample} + \gamma \cdot L_{live}$$

**Implementation:** [`backend/app/cv/research/qmf_engine.py`](file:///d:/Facial%20Recognition/backend/app/cv/research/qmf_engine.py#L58-L76)
```python
def compute_composite_score(self, similarity_score: float, quality_score: float, liveness_score: float) -> float:
    S = float(np.clip(similarity_score, 0.0, 1.0))
    Q = float(np.clip(quality_score, 0.0, 1.0))
    L = float(np.clip(liveness_score, 0.0, 1.0))

    C = (
        self.config.alpha_weight * S
        + self.config.beta_weight * Q
        + self.config.gamma_weight * L
    )
    return float(np.clip(C, 0.0, 1.0))
```

---

## 4.3 Empirical Telemetry & Audit Logging

Every inference request generates a structured `TelemetryRecord` containing:
- `similarity_score`, `quality_score`, `liveness_score`, `composite_score`, `dynamic_threshold`
- `final_decision` classification (`AUTHENTICATED`, `SPOOF_REJECTED`, `QUALITY_REJECTED`, `UNKNOWN_REJECTED`)
- Immutable model version metadata (`v2.0.0-QMF`), configuration parameters ($\tau_{base}=0.55$, $\lambda=0.15$), and ISO-8601 UTC timestamps.

---

## 4.4 Automated Verification & Test Results

The implementation was validated using Pytest across 23 unit & integration tests:
- **Baseline Pipeline:** Executed and benchmarked in `test_baseline_vs_proposed_side_by_side`.
- **Proposed QMF Pipeline:** Verified across dynamic threshold calculation, gate decisions, and telemetry recording.
- **Pass Rate:** 23/23 tests passed (100% success rate).
