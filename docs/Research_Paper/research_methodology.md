# Research Methodology and Experimental Framework

**Project:** Facial Recognition Attendance System  
**Title:** Experimental Design for Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)  
**Author:** Software Architect & Research Engineer  
**Date:** August 2026  
**Document:** `docs/Research_Paper/research_methodology.md`  

---

## 1. System Architecture Comparison

To scientifically evaluate the proposed **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** framework, we establish a formal architectural comparison between the standard industry baseline system and our proposed system.

```
========================================================================================
BASELINE ARCHITECTURE (Decoupled Sequential Gating with Static Threshold)
========================================================================================
[Video Frame] ──► [Face Detection] ──► [Quality Filter] ──► [Liveness Filter] ──► [ArcFace Match] ──► Threshold (\tau_0) ──► Decision
                                           │ (Fail: Drop)       │ (Fail: Drop)                              (Static 0.60)
                                           ▼                    ▼
                                        (Discard)            (Discard)

========================================================================================
PROPOSED ARCHITECTURE (Unified QMF-Score Engine with Dynamic Adaptive Threshold)
========================================================================================
[Video Frame] ──► [RetinaFace] ──► Extract Features Simultaneously:
                                   ├── Pose, Sharpness, Illumination ──► Compute Q_sample
                                   ├── MiniFASNet Texture Classifier  ──► Compute L_live
                                   └── ArcFace ResNet-50 512D Vector ──► Compute S_match
                                                                              │
                                                                              ▼
                                                       ┌──────────────────────────────────────────────┐
                                                       │ Unified QMF-Score Engine                     │
                                                       │ C(x) = \alpha S + \beta Q + \gamma L         │
                                                       │ Dynamic Threshold: \tau(Q) = \tau_0 + f(1-Q) │
                                                       └──────────────────────┬───────────────────────┘
                                                                              │
                                                                              ▼
                                                                     Automated Attendance Log
```

### 1.1 Baseline System Architecture (System A)
* **Detection & Alignment:** RetinaFace (ResNet-50 backbone) extracting 5 2D landmarks.
* **Quality Filter:** Hard threshold $Q_{sharpness} \ge 100.0$ (Laplacian variance). Discards frame if quality check fails.
* **Liveness Filter:** Hard threshold $L_{live} \ge 0.85$ (MiniFASNetV2). Discards frame if liveness check fails.
* **Recognition Matcher:** ArcFace ResNet-50 512D embeddings using standard Cosine Similarity.
* **Decision Logic:** Static global threshold $\tau_{static} = 0.60$ ($S_{match} \ge 0.60 \implies \text{Match}$).

### 1.2 Proposed System Architecture (System B - QMF-Score)
* **Detection & Alignment:** RetinaFace (ResNet-50 backbone) extracting 5 2D landmarks.
* **Quality Assessor:** Multi-component score $Q_{sample} = w_p Q_{pose} + w_s Q_{sharpness} + w_i Q_{illumination} \in [0, 1]$.
* **Liveness Detector:** MiniFASNetV2 producing continuous probability $L_{live} \in [0, 1]$.
* **Recognition Matcher:** ArcFace ResNet-50 512D vector cosine similarity $S_{match} \in [0, 1]$.
* **Unified Decision Engine:**
  $$C(x) = \alpha \cdot S_{match}(x) + \beta \cdot Q_{sample}(x) + \gamma \cdot L_{live}(x)$$
  $$\tau(Q) = \tau_{base} - \lambda \cdot (Q_{sample} - \bar{Q})$$
  $$\text{Decision} = \begin{cases} \text{AUTHENTICATED}, & \text{if } C(x) \ge \tau(Q) \text{ AND } L_{live} \ge L_{min} \\ \text{REJECTED}, & \text{otherwise} \end{cases}$$

---

## 2. Dataset Formulations & Benchmark Splits

The methodology utilizes three distinct dataset splits to evaluate intra-dataset performance, cross-domain generalization, and real-world operational attendance streams:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                EVALUATION DATASETS                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Split 1: Public Benchmark Dataset (IJB-S Surveillance & LFW)                           │
│ Split 2: Synthetic Environmental Degradation Suite (Gaussian Blur, Pose, Illumination) │
│ Split 3: Empirically Captured Operational Classroom Attendance Video Dataset           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Split 1: Public Benchmark Datasets
* **IJB-S (IARPA Janus Benchmark Surveillance):** 565 video tracks of 137 subjects captured in unconstrained operational environments (surveillance cameras, walk-by kiosks). Evaluates 1:N identification in low-resolution video.
* **LFW (Labeled Faces in the Wild):** 13,233 images of 5,749 identities. Used for standard baseline verification calibration.

### 2.2 Split 2: Synthetic Environmental Degradation Suite
To systematically evaluate robustness, standard high-quality test pairs from LFW are subjected to controlled synthetic degradation:
1. **Motion Blur:** Gaussian kernel smoothing ($\sigma \in [1.0, 5.0]$ pixels).
2. **Pose Distortion:** Synthetic affine rotation ($\theta_{yaw} \in [0^\circ, 45^\circ]$).
3. **Low Illumination:** Gamma scaling ($I_{gamma} \in [0.2, 1.0]$ simulating 10 lux to 300 lux).

### 2.3 Split 3: Operational Classroom Video Dataset
* **Cohort Size:** 50 enrolled student subjects (demographically diverse: varying age, gender, skin tone).
* **Enrollment:** 5 high-quality reference enrollment images per subject under controlled studio lighting.
* **Test Video Sequences:** 100 video sequences (1080p, 30 FPS, 10–30 seconds per subject) recorded at classroom entry doors under morning, afternoon, and artificial evening light. Includes genuine attempts and 50 presentation attack attempts (2D print photos, 4K iPad video replays).

---

## 3. Experimental Protocols & Metrics

### 3.1 Biometric Verification Metrics
* **False Acceptance Rate (FAR):** Proportion of imposter pairs incorrectly accepted as genuine matches:
  $$\text{FAR} = \frac{\text{False Positives}}{\text{False Positives} + \text{True Negatives}}$$
* **False Rejection Rate (FRR):** Proportion of genuine pairs incorrectly rejected:
  $$\text{FRR} = \frac{\text{False Negatives}}{\text{False Negatives} + \text{True Positives}}$$
* **True Acceptance Rate at Fixed FAR (TAR@FAR):** Primary metric for high-security biometrics (evaluated at $\text{FAR} = 10^{-4}$ and $10^{-5}$).
* **Equal Error Rate (EER):** The point on the ROC curve where $\text{FAR} = \text{FRR}$.

### 3.2 Presentation Attack Detection (PAD / Liveness) Metrics
* **APCER (Attack Presentation Classification Error Rate):** Proportion of spoof attacks incorrectly classified as live.
* **BPCER (Bonafide Presentation Classification Error Rate):** Proportion of live faces incorrectly classified as spoofs.
* **ACER (Average Classification Error Rate):**
  $$\text{ACER} = \frac{\text{APCER} + \text{BPCER}}{2}$$

### 3.3 System Operational Metrics
* **System Precision, Recall, F1-Score:** Overall attendance session accuracy across video streams.
* **Inference Latency (ms):** Per-frame wall-clock processing time broken down by stage (Detection, Alignment, Quality, Liveness, Feature Extraction, Vector Search).
* **Throughput (FPS):** Frames processed per second on standard CPU hardware (Intel Core i5-12450H).

---

## 4. Ablation Study Plan

To isolate the specific impact of each component in the proposed QMF-Score framework, four ablation configurations will be experimentally compared:

| Config ID | Description | Match Score ($S_{match}$) | Quality ($Q_{sample}$) | Liveness ($L_{live}$) | Threshold Type |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Ablation 0** | Baseline ArcFace | Yes | No | No | Static ($\tau_0$) |
| **Ablation 1** | ArcFace + Quality Filter | Yes | Hard Filter | No | Static ($\tau_0$) |
| **Ablation 2** | ArcFace + Liveness Filter | Yes | No | Hard Filter | Static ($\tau_0$) |
| **Ablation 3** | ArcFace + Adaptive Threshold $\tau(Q)$ | Yes | Continuous | No | **Dynamic $\tau(Q)$** |
| **Full Model** | **Full QMF-Score Engine** | **Yes** | **Continuous** | **Continuous** | **Dynamic $\tau(Q)$** |

---

## 5. Statistical Verification & Reproducibility Guidelines

1. **Statistical Significance Testing:** All comparative results across test splits will be evaluated using 5-fold cross-validation. Statistical significance of accuracy improvements will be verified using paired two-tailed $t$-tests and non-parametric Wilcoxon signed-rank tests with significance threshold $\alpha = 0.05$ ($p < 0.05$).
2. **Deterministic Execution Seeds:** Random seeds for synthetic degradation and data splits will be fixed (`seed=42`).
3. **Open-Source Reproducibility Artifacts:** All experimental benchmark scripts, evaluation datasets (anonymized embeddings), and model configuration files will be stored in `research/experiments/` and `research/benchmarks/`.
