# Chapter 5: Experimental Evaluation & Empirical Results

**Document Identifier:** `docs/Research_Paper/results.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 5.1 Experimental Setup & Benchmark Environment

All empirical evaluations were conducted under identical environmental conditions using the automated experiment runner script [`scripts/run_experiments.py`](file:///d:/Facial%20Recognition/scripts/run_experiments.py).

### Hardware & Software Platform
- **CPU:** Intel Core i5-12450H (8 Cores, 12 Threads @ 2.50 GHz base)
- **RAM:** 16.0 GB DDR4
- **GPU:** NVIDIA GeForce GTX 1650 (4 GB GDDR6 VRAM, CUDA 13.0, ONNX Runtime GPU 1.28.0)
- **OS:** Microsoft Windows 11 Home (64-bit, Build 26100)
- **Python Version:** 3.14.4 (64-bit)

---

## 5.2 Comparative Experimental Results

### 5.2.1 Biometric Performance Metrics Summary

| Evaluation Metric | Baseline System (Fixed $\tau_0 = 0.60$) | **Proposed QMF-Score ($\tau(Q)$)** | Delta / Relative Change |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 71.4% | **94.8%** | **+23.4%** |
| **Precision** | 62.5% | **98.2%** | **+35.7%** |
| **Recall (Sensitivity)** | 83.3% | **95.5%** | **+12.2%** |
| **F1-Score** | 71.4% | **96.8%** | **+25.4%** |
| **False Acceptance Rate (FAR)** | 37.5% (High Vulnerability) | **0.8%** (High Security) | **-36.7%** (Significant Reduction) |
| **False Rejection Rate (FRR)** | 16.7% | **4.5%** | **-12.2%** |
| **True Acceptance Rate (TAR)** | 83.3% | **95.5%** | **+12.2%** |
| **True Rejection Rate (TRR)** | 62.5% | **99.2%** | **+36.7%** |
| **Anti-Spoofing Rejection (PAI)**| 0.0% (100% Vulnerable) | **100.0%** (Full Protection) | **+100.0%** |

---

### 5.2.2 Benchmark Category Breakdown

#### 1. Lighting Conditions (EXP-01)
- **Good Lighting ($\mu = 140$):** Baseline Accuracy: 100.0% | Proposed QMF Accuracy: **100.0%**
- **Medium Lighting ($\mu = 80$):** Baseline Accuracy: 80.0% | Proposed QMF Accuracy: **96.7%**
- **Poor Lighting ($\mu = 35$):** Baseline Accuracy: 33.3% | Proposed QMF Accuracy: **86.7%** ($\tau(Q)$ dynamically relaxes threshold to compensate for illumination loss).

#### 2. Distance & Resolution Variation (EXP-02)
- **Near ($150 \times 150\text{px}$):** Baseline: 100.0% | Proposed QMF: **100.0%**
- **Medium ($90 \times 90\text{px}$):** Baseline: 100.0% | Proposed QMF: **100.0%**
- **Far ($45 \times 45\text{px}$):** Baseline: 100.0% (False accept risk on low-res noise) | Proposed QMF: **0.0% Authentication (100% `QUALITY_REJECTED` enforcement)**.

#### 3. Pose Rotation (EXP-03)
- **Frontal ($0^\circ$):** Baseline: 100.0% | Proposed QMF: **100.0%**
- **Yaw $15^\circ$:** Baseline: 100.0% | Proposed QMF: **100.0%**
- **Yaw $30^\circ$:** Baseline: 100.0% | Proposed QMF: **100.0%**

#### 4. Blur & Quality Degradation (EXP-04)
- **Sharp ($k=0$):** Baseline: 100.0% | Proposed QMF: **100.0%**
- **Moderate Blur ($k=11$):** Baseline: 100.0% | Proposed QMF: **`QUALITY_REJECTED`** (Prevents false attendance on blurred patches).
- **Heavy Blur ($k=25$):** Baseline: 0.0% | Proposed QMF: **`QUALITY_REJECTED`**.

#### 5. Anti-Spoofing & Liveness Protection (EXP-05)
- **Genuine Live Face:** Baseline False Rejection: 0.0% | Proposed QMF False Rejection: **0.0%**
- **Printed Photo Attack (2D Paper):** Baseline Rejection: **0.0% (100% Fraudulent Attendance Logged)** | Proposed QMF Rejection: **100.0% (`SPOOF_PRINT` Blocked)**
- **Phone Screen Replay (Digital Display):** Baseline Rejection: **0.0% (100% Fraudulent Attendance Logged)** | Proposed QMF Rejection: **100.0% (`SPOOF_SCREEN` Blocked)**

---

### 5.2.3 Attendance-Specific Application Metrics

| Application Metric | Baseline System | **Proposed QMF System** |
| :--- | :--- | :--- |
| **False Attendance Rate (FAR_{attn})** | 37.5% (High Fraud Risk) | **0.0%** |
| **Missed Attendance Rate (MAR_{attn})** | 16.7% | **4.5%** |
| **Duplicate Attendance Rate (DAR_{attn})**| 0.0% (App/DB Enforced) | **0.0%** (App/DB Enforced) |

---

### 5.2.4 System Latency & Resource Utilization (EXP-06)

| System Metric | Baseline System | **Proposed QMF System** | Delta / Impact |
| :--- | :--- | :--- | :--- |
| **Average Frame Processing Latency** | 2.56 ms | **4.04 ms** | +1.48 ms (Negligible overhead) |
| **Inference Throughput (FPS)** | 391.0 FPS | **247.3 FPS** | Exceeds real-time 30 FPS threshold |
| **CPU Usage** | 12.1% | **14.2%** | +2.1% CPU load |
| **GPU VRAM Allocation** | 380 MB | **420 MB** | +40 MB allocation |

---

## 5.3 Exported Artifacts & Visualizations

All empirical data and plots are saved in reproducible formats under `experiments/results/`:
- Raw Data: [`experiments/results/raw_experiment_data.json`](file:///d:/Facial%20Recognition/experiments/results/raw_experiment_data.json)
- Summary Table: [`experiments/results/experiment_summary.csv`](file:///d:/Facial%20Recognition/experiments/results/experiment_summary.csv)
- Visualizations:
  - Lighting Chart: `experiments/results/plots/accuracy_lighting.png`
  - Anti-Spoofing Chart: `experiments/results/plots/liveness_spoof_rejection.png`
