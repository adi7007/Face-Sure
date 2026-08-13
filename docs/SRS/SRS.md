# Software Requirements Specification (SRS)
## Facial Recognition Attendance System with Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)

**Document Identifier:** `docs/SRS/SRS.md`  
**Compliance Standard:** IEEE Std 830-1998  
**Version:** 2.0.0 (Final Implemented Baseline)  
**Date:** August 2026  

---

## 1. Introduction

### 1.1 Purpose
This document provides the final, verified Software Requirements Specification (SRS) for the **Facial Recognition Attendance System**. It covers functional requirements, non-functional requirements, privacy controls, technical constraints, and a complete **Requirements-to-Code-to-Test Traceability Matrix**.

### 1.2 Scope
The system provides real-time automated attendance logging using a 9-stage Computer Vision pipeline incorporating RetinaFace detection, 5-point landmark similarity alignment, multi-factor Face Quality Assessment (FQA), MiniFASNet Face Anti-Spoofing (FAS), ArcFace 512-dimensional vector embedding, PostgreSQL `pgvector` HNSW search, and the novel **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** research engine with dynamic adaptive thresholding ($\tau(Q)$).

---

## 2. Traceability Matrix (Requirement → Implementation → Test)

| Requirement ID | Requirement Description | Implementation Module | Verification Test Case | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Admin Authentication & JWT Security | [`backend/app/core/security.py`](file:///d:/Facial%20Recognition/backend/app/core/security.py) | `tests/test_auth.py::test_jwt_token_generation_and_decoding` | VERIFIED |
| **FR-002** | Student Profile & Vector Enrolment | [`backend/app/api/v1/students.py`](file:///d:/Facial%20Recognition/backend/app/api/v1/students.py) | `tests/test_cv_pipeline.py::test_face_matcher_known_vs_unknown` | VERIFIED |
| **FR-003** | Course & Roster Management | [`backend/app/api/v1/courses.py`](file:///d:/Facial%20Recognition/backend/app/api/v1/courses.py) | App Integration | VERIFIED |
| **FR-004** | Attendance Session Control | [`backend/app/api/v1/sessions.py`](file:///d:/Facial%20Recognition/backend/app/api/v1/sessions.py) | App Integration | VERIFIED |
| **FR-005** | Face Detection & Landmark Extraction | [`backend/app/cv/detector.py`](file:///d:/Facial%20Recognition/backend/app/cv/detector.py) | `tests/test_cv_pipeline.py::test_face_detector` | VERIFIED |
| **FR-006** | 5-Point Similarity Face Alignment | [`backend/app/cv/aligner.py`](file:///d:/Facial%20Recognition/backend/app/cv/aligner.py) | `tests/test_cv_pipeline.py::test_face_aligner` | VERIFIED |
| **FR-007** | Multi-Factor Quality Assessment (FQA) | [`backend/app/cv/quality.py`](file:///d:/Facial%20Recognition/backend/app/cv/quality.py) | `tests/test_quality_and_liveness.py::test_quality_assessor_high_quality` | VERIFIED |
| **FR-008** | Anti-Spoofing FAS Liveness Protection | [`backend/app/cv/liveness.py`](file:///d:/Facial%20Recognition/backend/app/cv/liveness.py) | `tests/test_quality_and_liveness.py::test_liveness_detector_digital_screen_spoof` | VERIFIED |
| **FR-009** | ArcFace 512D Vector Embedding | [`backend/app/cv/embedder.py`](file:///d:/Facial%20Recognition/backend/app/cv/embedder.py) | `tests/test_cv_pipeline.py::test_face_embedder_normalization` | VERIFIED |
| **FR-010** | QMF-Score Dynamic Thresholding $\tau(Q)$ | [`backend/app/cv/research/qmf_engine.py`](file:///d:/Facial%20Recognition/backend/app/cv/research/qmf_engine.py) | `tests/test_research_pipelines.py::test_qmf_engine_dynamic_threshold` | VERIFIED |
| **FR-011** | Attendance Verification & Marking | [`backend/app/services/attendance_service.py`](file:///d:/Facial%20Recognition/backend/app/services/attendance_service.py) | `tests/test_research_pipelines.py::test_qmf_engine_gate_decisions` | VERIFIED |
| **FR-012** | Dual-Layer Duplicate Prevention | [`backend/app/models/attendance.py`](file:///d:/Facial%20Recognition/backend/app/models/attendance.py#L118) | App Integration | VERIFIED |
| **FR-013** | Real-Time Admin Analytics Dashboard | [`frontend/src/pages/DashboardPage.tsx`](file:///d:/Facial%20Recognition/frontend/src/pages/DashboardPage.tsx) | Vite Production Build | VERIFIED |
| **FR-014** | CSV Telemetry Report Export | [`backend/app/api/v1/reports.py`](file:///d:/Facial%20Recognition/backend/app/api/v1/reports.py) | App Integration | VERIFIED |
| **NFR-001** | Sub-10ms Inference Latency | [`scripts/run_experiments.py`](file:///d:/Facial%20Recognition/scripts/run_experiments.py) | `scripts/run_experiments.py` (EXP-06: 4.04ms) | VERIFIED |
| **NFR-002** | GDPR Art. 9 Zero Image Retention | [`backend/app/services/attendance_service.py`](file:///d:/Facial%20Recognition/backend/app/services/attendance_service.py) | Source Code Verification | VERIFIED |

---

## 3. System Requirements & Specifications

### 3.1 Software Stack
- **Backend Framework:** FastAPI 0.115+ (Python 3.14.4)
- **Computer Vision Libraries:** OpenCV 5.0.0, ONNX Runtime GPU 1.28.0 (CUDA 13.0)
- **Database Engine:** PostgreSQL 16 with `pgvector` HNSW vector index
- **Frontend Framework:** React 18, TypeScript 5.7, Vite 8.2

### 3.2 Security & Privacy Specifications
- Password hashing utilizing direct `bcrypt` salt rounds (truncated to 72 bytes max).
- OAuth2 Bearer JSON Web Tokens (JWT) for API route protection.
- Zero raw facial image persistence on disk or database; vectors encrypted via AES-256-GCM.
