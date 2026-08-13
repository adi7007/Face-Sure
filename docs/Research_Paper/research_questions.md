# Research Questions, Objectives, and Formal Hypotheses

**Project:** Facial Recognition Attendance System  
**Title:** Quality-Aware Multi-Factor Confidence Scoring (QMF-Score) for Unconstrained Biometric Attendance Streams  
**Author:** Software Architect & Research Engineer  
**Date:** August 2026  
**Document:** `docs/Research_Paper/research_questions.md`  

---

## 1. Formal Research Problem Statement

In operational automated facial recognition attendance environments (e.g., classroom kiosks, entrance turnstiles), video frames are captured under unconstrained environmental conditions characterized by variable subject-to-camera distance, head pose variations, localized motion blur, and ambient illumination fluctuations. 

Existing facial recognition attendance architectures evaluate identity matching using **static similarity thresholds** ($\tau_{static}$) operating on isolated pipeline stages. Specifically, face quality assessment (FQA), face liveness detection (FAS), and deep feature matching (FR) are treated as decoupled binary decision gates. 

This architectural decoupling introduces two key systemic failure modes:
1. **Excessive False Rejections (FRR):** High-similarity genuine face images that suffer from slight non-ideal conditions (e.g., $20^\circ$ yaw angle or minor motion blur) fail strict static quality or similarity gates, forcing manual attendance overrides.
2. **Security Vulnerability to Boundary Spoofs (FAR):** Low-quality or degraded imposter faces near static matching thresholds can cause false acceptance errors if similarity margins are naively relaxed to accommodate unconstrained streams.

There is a lack of a unified inference framework that mathematically integrates biometric sample quality ($Q_{sample}$), presentation attack liveness confidence ($L_{live}$), and hyperspherical embedding similarity ($S_{match}$) into a **dynamic, quality-adaptive verification threshold ($\tau(Q)$)** for real-time video attendance streams.

---

## 2. Research Questions

### Primary Research Question (PRQ)
> **How can biometric sample quality, presentation attack liveness confidence, and deep angular feature similarity be mathematically unified into a dynamic inference framework to optimize verification accuracy and operational throughput in unconstrained streaming facial recognition attendance systems?**

### Secondary Research Questions (SRQs)
* **RQ1 (Quality-Utility Modeling):** How can physical facial sample quality metrics (head pose $\theta_{yaw, pitch, roll}$, Laplacian sharpness $S_{lap}$, and illumination uniformity $I_{lum}$) be weighted into a composite quality score $Q_{sample} \in [0, 1]$ that reliably predicts matcher utility?
* **RQ2 (Dynamic Thresholding):** What mathematical decay function $\tau(Q)$ optimal maps composite quality $Q_{sample}$ to a dynamic cosine match threshold such that False Acceptance Rate (FAR) remains constrained ($\le 10^{-4}$) while False Rejection Rate (FRR) is minimized on degraded video frames?
* **RQ3 (Multi-Factor Integration):** Does a unified composite confidence metric $C(x) = \alpha S_{match} + \beta Q_{sample} + \gamma L_{live}$ demonstrate superior classification performance (measured by TAR@FAR=$10^{-4}$, EER, and F1-Score) compared to conventional decoupled sequential gating?
* **RQ4 (Operational Efficiency & Fairness):** Can the proposed QMF-Score framework maintain real-time streaming execution ($\ge 20$ FPS on commodity hardware) while reducing demographic differentials across varying skin tones and lighting conditions?

---

## 3. Research Objectives (ROs)

To address the research questions, the following concrete research objectives are established:

* **RO1 (Formulation):** Formulate a real-time Composite Quality Metric ($Q_{sample}$) and a Dynamic Quality-Adaptive Threshold function ($\tau(Q)$) grounded in hyperspherical embedding geometry.
* **RO2 (System Architecture Integration):** Design and implement the unified **Decision Engine** pipeline integrating RetinaFace (detection/alignment), MiniFASNetV2 (passive liveness), ArcFace ResNet-50 (512D feature extraction), and `pgvector` HNSW index matching within a production-grade FastAPI backend.
* **RO3 (Benchmark Evaluation):** Benchmark the proposed QMF-Score model against static-threshold baseline architectures across public benchmark datasets (IJB-S, synthetic LFW-degraded splits) and an empirically collected classroom attendance video dataset.
* **RO4 (Ablation & Statistical Validation):** Conduct detailed ablation studies to analyze the individual contributions of $S_{match}$, $Q_{sample}$, and $L_{live}$, verifying statistical significance using paired $t$-tests and Wilcoxon signed-rank tests ($p < 0.05$).

---

## 4. Formal Hypotheses

* **Hypothesis 1 ($H_1$ - Accuracy Improvement):**  
  *Null Hypothesis ($H_{1,0}$):* Incorporating dynamic quality-adaptive thresholding ($\tau(Q)$) yields no statistically significant reduction in False Rejection Rate (FRR) compared to static thresholding ($\tau_{static} = 0.60$) at FAR = $10^{-4}$.  
  *Alternative Hypothesis ($H_{1,1}$):* The QMF-Score dynamic thresholding function $\tau(Q)$ reduces FRR by at least **10%** on unconstrained low-quality video frame streams compared to static thresholding at FAR = $10^{-4}$ with statistical significance ($p < 0.05$).

* **Hypothesis 2 ($H_2$ - Security & Spoof Resistance):**  
  *Null Hypothesis ($H_{2,0}$):* Multi-factor confidence scoring $C(x)$ offers no improvement in Average Classification Error Rate (ACER) against 2D print and screen presentation attacks compared to isolated passive liveness filtering.  
  *Alternative Hypothesis ($H_{2,1}$):* Integrating liveness confidence $L_{live}$ directly into the multi-factor decision metric $C(x)$ achieves an ACER $\le 1.0\%$ across presentation attack benchmarks, outperforming decoupled single-stage liveness gates.

* **Hypothesis 3 ($H_3$ - Operational Throughput):**  
  *Null Hypothesis ($H_{3,0}$):* Executing the composite quality assessment and multi-factor decision logic introduces unacceptable computational latency, reducing stream throughput below 15 FPS on a standard quad-core CPU.  
  *Alternative Hypothesis ($H_{3,1}$):* The QMF-Score decision engine executes within **< 15ms per frame** overhead, maintaining real-time video processing speeds $\ge 25$ FPS on standard CPU hardware.

---

## 5. Summary of Expected Academic & Practical Contributions

1. **Theoretical Contribution:** A novel mathematical formulation for dynamic threshold calibration ($\tau(Q)$) based on hyperspherical sample utility estimation.
2. **Architectural Contribution:** An open-source, enterprise-ready reference architecture integrating real-time quality scoring, liveness verification, ArcFace embeddings, and PostgreSQL `pgvector` HNSW search under strict GDPR Article 9 privacy design principles.
3. **Empirical Contribution:** Comprehensive benchmark evaluation demonstrating quantitative accuracy, robustness, and latency improvements over static-threshold biometrics in unconstrained video attendance streams.
