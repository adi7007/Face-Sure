# Biometric Model Selection & Evaluation Report

**Document Identifier:** `docs/Architecture/model_selection.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Executive Summary

This document presents the technical evaluation and selection rationale for the face embedding and detection models utilized in the **Facial Recognition Attendance System**. Three candidate face embedding architectures—**FaceNet**, **CosFace**, and **ArcFace**—were evaluated across accuracy, computational performance, licensing, reproducibility, and deployment feasibility. **ArcFace** (utilizing Additive Angular Margin Loss with a MobileFaceNet / ResNet-50 backbone executed via ONNX Runtime GPU) is selected as the primary face recognition model.

---

## 2. Candidate Model Evaluation Matrix

| Evaluation Criteria | FaceNet (Schroff 2015) | CosFace (Wang 2018) | **ArcFace (Deng 2019) [SELECTED]** |
| :--- | :--- | :--- | :--- |
| **Loss Function** | Online Triplet Loss ($L_2$ Euclidean Margin) | Large Margin Cosine Loss ($\cos\theta - m$) | **Additive Angular Margin Loss ($\cos(\theta + m)$)** |
| **Embedding Dimension**| 128-dimensional | 512-dimensional | **512-dimensional ($L_2$-normalized)** |
| **LFW Benchmark Accuracy**| 99.63% | 99.73% | **99.83%** |
| **CFP-FP Benchmark Accuracy**| 95.56% | 98.12% | **98.37%** |
| **Hyperspherical Geometry**| No (Euclidean space constraint) | Yes (Cosine margin) | **Yes (Direct geodesic distance mapping)** |
| **Licensing** | Apache 2.0 / Open Source | MIT License | **MIT License (InsightFace Repository)** |
| **ONNX Runtime GPU Optimization**| Good | High | **Optimal (Native ONNX TensorRT execution)** |
| **Robustness to Pose/Illum.**| Moderate | High | **Superior (Enforces tight intra-class angular clusters)**|

---

## 3. Decision Rationale for ArcFace

1. **Superior Angular Class Separability:** ArcFace introduces an exact angular margin penalty $m=0.50$ directly within the cosine angle ($\cos(\theta + m)$). This aligns directly with geodesic distance on a unit hypersphere, forcing embeddings of the same identity into tighter clusters while pushing different identities further apart.
2. **512-Dimensional Representation:** The 512D output vector provides high representational capacity for distinguishing thousands of identity templates while matching seamlessly with PostgreSQL `pgvector(512)` indexing.
3. **Execution Efficiency & Hardware Acceleration:** ArcFace executed via ONNX Runtime GPU (CUDA/TensorRT execution providers) yields sub-10ms inference per face crop patch, maintaining streaming rates $> 25$ FPS on commodity GPU hardware (NVIDIA GTX 1650).
4. **Licensing & Reproducibility:** Distributed under the permissive MIT license via InsightFace / ONNX model zoo, enabling full academic and industrial reproducibility.

---

## 4. Pipeline Architecture Decisions

* **Face Detection:** MediaPipe Face Detector / OpenCV Haar Cascade fallback for fast bounding box and landmark extraction.
* **Face Alignment:** 5-point similarity transformation mapping detected facial landmarks (eyes, nose, mouth corners) to standardized $112 \times 112$ canonical crop patches.
* **Quality Assessor:** Laplacian variance sharpness thresholding ($\sigma^2_{Lap} \ge 60.0$) and minimum bounding box size ($60 \times 60$ pixels) to filter unidentifiable samples.
* **Vector Matching Metric:** Cosine Similarity ($S = 1 - \text{cosine\_distance}$) against stored student embedding templates.
