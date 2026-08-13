# Computer Vision & AI Recognition Pipeline Architecture

**Document Identifier:** `docs/Architecture/ai_pipeline.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. End-to-End Pipeline Overview

The computer vision pipeline processes incoming video stream frames from the kiosk camera, detects faces, validates image quality and liveness, extracts biometric embeddings, queries the vector database, and applies the novel **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** decision mechanism to authenticate identities.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI PIPELINE EXECUTION STAGES                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Video Frame Capture ──► 2. Face Detection ──► 3. Alignment (112x112 Crop)           │
│                            (RetinaFace)          (5-Point Affine)                      │
│                                                         │                              │
│ 6. Vector Search       ◄── 5. Embedding       ◄── 4. Quality & Liveness Checks       │
│    (pgvector HNSW)          (ArcFace 512D)       (Pose/Sharpness/MiniFASNet)          │
│         │                                                                              │
│         ▼                                                                              │
│ 7. QMF-Score Engine ──► 8. Identity Resolution ──► 9. Automated Attendance Mark        │
│    (Dynamic Tau)           (Student Match)           (PostgreSQL Event Log)            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Stage-by-Stage Technical Design

### Stage 1: Video Frame Capture & Pre-Processing
* **Input:** Raw RGB Video Frame from HTML5 WebRTC Kiosk Stream ($1280 \times 720 \times 3$, Uint8).
* **Operation:** Format conversion to BGR color space; frame resize to $640 \times 360$ for ultra-fast detection pass while retaining full-resolution ROI for crop extraction.
* **Latency Budget:** $< 2\text{ms}$.

### Stage 2: Face Detection (RetinaFace)
* **Model:** RetinaFace with ResNet-50 / MobileNet-0.25 backbone executed via ONNX Runtime GPU.
* **Operation:** Single-shot Feature Pyramid Network (FPN) detects candidate bounding boxes ($B = [x_1, y_1, x_2, y_2, s_{conf}]$) and predicts 5 2D facial landmarks ($L = [p_{reye}, p_{leye}, p_{nose}, p_{rmouth}, p_{lmouth}]$).
* **Filtering Threshold:** Detection confidence score $s_{conf} \ge 0.80$; minimum face bounding box size $60 \times 60$ pixels.
* **Tensor Shapes:** Input $(1, 3, 360, 640) \to$ Bounding Boxes $(N, 5)$, Landmarks $(N, 5, 2)$.
* **Latency Budget:** $12\text{ms}$ (GPU) / $25\text{ms}$ (CPU).

### Stage 3: Facial Alignment & Standardized Cropping
* **Operation:** Computes 2D affine transformation matrix $M_{2\times3}$ mapping detected 5 landmarks $L$ to standardized canonical template coordinates (InsightFace 112x112 target layout).
* **Output:** Aligned normalized RGB face crop patch ($112 \times 112 \times 3$, Float32 normalized to $[-1, 1]$).
* **Latency Budget:** $< 1.5\text{ms}$.

### Stage 4: Composite Face Quality Assessment (FQA)
* **Operation:** Computes three physical quality factors on the aligned patch:
  1. **Pose Angle Estimation ($Q_{pose}$):** Derived from landmark geometry ($\theta_{yaw, pitch, roll}$).  
     $$Q_{pose} = \max\left(0, 1 - \frac{|\theta_{yaw}| + |\theta_{pitch}| + |\theta_{roll}|}{60^\circ}\right)$$
  2. **Sharpness Score ($Q_{sharpness}$):** Normalized Laplacian variance $\sigma^2_{Lap}$ of the grayscale patch.  
     $$Q_{sharpness} = \frac{1}{1 + e^{-0.05 (\sigma^2_{Lap} - 80)}}$$
  3. **Illumination Score ($Q_{illumination}$):** Measures mean brightness $\mu_I$ and contrast standard deviation $\sigma_I$.  
     $$Q_{illumination} = 1 - \frac{|\mu_I - 128|}{128}$$
* **Composite Quality Score ($Q_{sample}$):**
  $$Q_{sample} = 0.40 \cdot Q_{pose} + 0.35 \cdot Q_{sharpness} + 0.25 \cdot Q_{illumination} \in [0, 1]$$
* **Gating Condition:** If $Q_{sample} < 0.20$, reject frame immediately as unusable blur/extreme pose without running heavy downstream embedder.
* **Latency Budget:** $< 2.0\text{ms}$.

### Stage 5: Liveness Detection / Presentation Attack Defense (FAS)
* **Model:** MiniFASNetV2 (Squeeze-and-Excitation MobileNet) trained with multi-scale patch and depth map supervision.
* **Operation:** Extracts texture gradient differences and high-frequency spectral artifacts to distinguish genuine human skin from print photos or digital screens.
* **Output:** Continuous liveness probability score $L_{live} \in [0, 1]$.
* **Gating Condition:** If $L_{live} < 0.35$, tag frame as `SPOOF_ATTEMPT` and log security alert.
* **Latency Budget:** $6.0\text{ms}$ (GPU) / $15.0\text{ms}$ (CPU).

### Stage 6: Deep Feature Embedding Extraction (ArcFace)
* **Model:** ArcFace ResNet-50 trained on MS1MV2 dataset (Additive Angular Margin $m=0.50$).
* **Operation:** Maps aligned $112 \times 112 \times 3$ crop to a unit-length hyperspherical feature space.
* **Output:** 512-dimensional Float32 vector $e \in \mathbb{R}^{512}$ where $\|e\|_2 = 1.0$.
* **Tensor Shapes:** Input $(1, 3, 112, 112) \to$ Output $(1, 512)$.
* **Latency Budget:** $10.0\text{ms}$ (GPU) / $30.0\text{ms}$ (CPU).

### Stage 7: Vector Similarity Search (PostgreSQL `pgvector`)
* **Operation:** Queries PostgreSQL table `face_embeddings` using HNSW index cosine distance metric ($d_{cosine} = 1 - \cos(\theta)$):
  ```sql
  SELECT student_id, (1 - (embedding <=> :query_embedding)) AS cosine_similarity
  FROM face_embeddings
  ORDER BY embedding <=> :query_embedding LIMIT 1;
  ```
* **Output:** Candidate matched `student_id` and raw match score $S_{match} \in [0, 1]$.
* **Latency Budget:** $< 8.0\text{ms}$.

### Stage 8: Research Decision Engine (QMF-Score & Dynamic Threshold $\tau(Q)$)
* **Unified Multi-Factor Score ($C(x)$):**
  $$C(x) = 0.60 \cdot S_{match} + 0.25 \cdot Q_{sample} + 0.15 \cdot L_{live}$$
* **Dynamic Quality-Adaptive Threshold ($\tau(Q)$):**
  $$\tau(Q) = \tau_{base} - \lambda \cdot (Q_{sample} - 0.50)$$
  where baseline threshold $\tau_{base} = 0.60$ and adaptation factor $\lambda = 0.15$.
* **Decision Rule:**
  $$\text{Result} = \begin{cases} \text{AUTHENTICATED (Student ID)}, & \text{if } C(x) \ge \tau(Q) \text{ AND } L_{live} \ge 0.50 \\ \text{UNKNOWN / REJECTED}, & \text{otherwise} \end{cases}$$
* **Latency Budget:** $< 0.5\text{ms}$.

### Stage 9: Attendance Session & Audit Event Logging
* **Operation:** If `AUTHENTICATED`:
  1. Check for recent recognition within cooldown period ($5$ minutes). If cooling down, return `ALREADY_MARKED`.
  2. Insert attendance record into `attendance_records` table (`status='PRESENT'`, `attendance_method='FACE_RECOGNITION'`).
  3. Insert audit log event into `recognition_events` table (stores $S_{match}, Q_{sample}, L_{live}, C(x), \tau(Q)$ for research evaluation).
  4. Emit WebSocket JSON response to Kiosk client to trigger green bounding box and audio chime.
* **Latency Budget:** $< 5.0\text{ms}$.

---

## 3. Total Pipeline Performance & Latency Budget Summary

| Pipeline Stage | Algorithm / Component | GPU Latency | CPU Latency | Output Artifact |
| :--- | :--- | :---: | :---: | :--- |
| **Stage 1** | Pre-processing & BGR resize | $1.5\text{ ms}$ | $2.0\text{ ms}$ | Resized BGR tensor |
| **Stage 2** | RetinaFace Detection | $12.0\text{ ms}$ | $25.0\text{ ms}$ | Bounding Box & 5 Landmarks |
| **Stage 3** | 5-Point Affine Alignment | $1.0\text{ ms}$ | $1.5\text{ ms}$ | Aligned 112x112 Crop Patch |
| **Stage 4** | Quality Assessor (Pose/Sharpness) | $1.5\text{ ms}$ | $2.0\text{ ms}$ | $Q_{sample} \in [0, 1]$ |
| **Stage 5** | MiniFASNetV2 Liveness | $6.0\text{ ms}$ | $15.0\text{ ms}$ | $L_{live} \in [0, 1]$ |
| **Stage 6** | ArcFace ResNet-50 Embedder | $10.0\text{ ms}$ | $30.0\text{ ms}$ | 512D Vector $e \in \mathbb{R}^{512}$ |
| **Stage 7** | `pgvector` HNSW Search | $5.0\text{ ms}$ | $8.0\text{ ms}$ | Candidate `student_id`, $S_{match}$ |
| **Stage 8** | QMF-Score Decision Engine | $0.2\text{ ms}$ | $0.5\text{ ms}$ | $C(x), \tau(Q)$, Final Decision |
| **Stage 9** | DB Commit & WS Broadcast | $4.0\text{ ms}$ | $6.0\text{ ms}$ | Attendance Record & Audit Log |
| **TOTAL** | **Full Pipeline Execution** | **$41.2\text{ ms}$** | **$90.0\text{ ms}$** | **Stream FPS: ~24.2 FPS (GPU)** |
