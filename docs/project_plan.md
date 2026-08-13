# Facial Recognition Attendance System — Project Plan

> **Project Type:** College Major Project + Research Paper  
> **Date Created:** 2026-08-13  
> **Status:** Planning Phase — No Implementation Yet

---

## 1. Development Environment Analysis

### Hardware

| Component | Details |
|-----------|---------|
| **CPU** | 12th Gen Intel Core i5-12450H — 8 cores / 12 threads |
| **RAM** | 16 GB |
| **GPU** | NVIDIA GeForce GTX 1650 — 4 GB VRAM |
| **CUDA** | CUDA 13.0 supported (Driver 581.83) |
| **Disk (D:)** | ~133 GB free of ~276 GB total |
| **OS** | Windows (HP Victus laptop) |

### Software

| Tool | Version / Status |
|------|-----------------|
| **Python** | 3.14.4 (system-wide install) |
| **pip** | 26.0.1 |
| **Git** | 2.55.0 |
| **Java** | 21.0.11 LTS |
| **VS Code** | 1.132.1 |
| **Node.js** | ❌ Not installed |
| **npm / npx / yarn / pnpm** | ❌ Not installed |
| **nvm** | ❌ Not installed |
| **Docker** | ❌ Not installed |
| **CMake** | ❌ Not installed |

### Python Environment

- **Location:** `C:\Users\VICTUS\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- **Installed packages:** Only `pip 26.0.1` — completely clean environment
- **No virtual environment** currently active
- **No ML/CV libraries** installed (PyTorch, OpenCV, dlib, etc.)

### Workspace State

- **Path:** `d:\Facial Recognition`
- **Status:** Empty directory — fresh start
- **Git:** Not initialized

### Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| CPU | ✅ Good | 8-core i5-12450H is adequate for development |
| RAM | ⚠️ Adequate | 16 GB is workable but tight for training; sufficient for inference |
| GPU | ⚠️ Adequate | GTX 1650 (4 GB) supports CUDA acceleration for inference; limited for training |
| Disk | ✅ Good | 133 GB free is sufficient for datasets and models |
| Python | ⚠️ Caution | Python 3.14 is bleeding edge — some ML libraries may not have wheels yet |
| Node.js | ❌ Missing | Must be installed for the frontend |

> [!WARNING]
> **Python 3.14 Compatibility Risk:** Python 3.14.4 is very new. Major ML libraries (PyTorch, ONNX Runtime, dlib) may not yet publish pre-built wheels for 3.14. We may need to install Python 3.11 or 3.12 alongside 3.14 specifically for the ML backend. This will be validated before implementation begins.

---

## 2. Project Understanding

### Objective

Build a **Facial Recognition Attendance System** that is simultaneously:

1. **A functional software product** — a deployable web application that captures faces via webcam, recognizes registered students, detects spoofing attempts, and records attendance automatically.
2. **An academic deliverable** — accompanied by a complete SRS document, a comprehensive project report, and a research paper suitable for publication in a conference or journal.

### Core Problem Statement

Manual attendance systems in educational institutions are:
- Time-consuming (5–10 minutes per session)
- Prone to proxy attendance
- Difficult to audit at scale
- Lacking biometric verification

### What This System Must Do

1. **Register** students by capturing and encoding their facial features
2. **Detect** faces in real-time from webcam streams
3. **Assess quality** of detected faces (blur, exposure, pose, occlusion)
4. **Verify liveness** to prevent spoofing (printed photos, screen replay, 3D masks)
5. **Recognize** faces by comparing live embeddings against the enrolled database
6. **Record attendance** with timestamp, confidence score, and session metadata
7. **Provide a dashboard** for instructors and administrators
8. **Generate reports** (daily, weekly, per-student, per-course)
9. **Log an audit trail** for every recognition decision

### Research Dimension

The project must include a **novel or improved contribution** suitable for academic publication. Potential areas:
- A hybrid liveness detection pipeline combining texture analysis + motion cues
- Face quality-aware recognition (adaptive thresholding based on image quality scores)
- Lightweight model distillation for real-time inference on consumer GPUs
- Multi-factor spoofing detection ensemble
- Benchmark comparison of modern face recognition backbones (ArcFace vs CosFace vs AdaFace) on a controlled attendance scenario

---

## 3. Recommended Technology Stack

### 3.1 Frontend — Next.js (React)

| Aspect | Recommendation |
|--------|---------------|
| **Framework** | Next.js 15 (React 19) |
| **UI Library** | shadcn/ui + Tailwind CSS |
| **State** | Zustand or React Context |
| **Charts** | Recharts |
| **Webcam** | `react-webcam` + MediaStream API |

**Why Next.js:**
- Server-side rendering for fast initial page loads
- API routes can proxy calls to the Python backend
- File-based routing simplifies dashboard/page structure
- Excellent TypeScript support
- Huge ecosystem for rapid UI development
- Industry standard — impressive on a college project

### 3.2 Backend — FastAPI (Python)

| Aspect | Recommendation |
|--------|---------------|
| **Framework** | FastAPI |
| **ASGI Server** | Uvicorn |
| **Task Queue** | Celery + Redis (optional, for heavy tasks) |
| **WebSocket** | FastAPI native WebSocket support |

**Why FastAPI:**
- Native `async/await` for high-concurrency webcam stream handling
- Automatic OpenAPI/Swagger docs (excellent for SRS and project report)
- Pydantic models enforce type-safe request/response schemas
- First-class Python ecosystem — seamless integration with OpenCV, PyTorch, ONNX
- WebSocket support for real-time face recognition streaming
- Fastest pure-Python web framework

### 3.3 Database — PostgreSQL + Redis

| Component | Role |
|-----------|------|
| **PostgreSQL** | Primary relational store (students, attendance, courses, users) |
| **Redis** | Caching face embeddings in memory for fast retrieval; session store |
| **SQLAlchemy 2.0** | ORM for database operations |
| **Alembic** | Database migrations |

**Why PostgreSQL:**
- `pgvector` extension enables native vector similarity search for face embeddings
- JSONB columns for flexible metadata storage
- Mature, reliable, widely supported
- Free and open-source

**Why Redis:**
- Sub-millisecond embedding lookups during real-time recognition
- Session management
- Rate limiting

### 3.4 Computer Vision & Face Recognition

| Component | Library | Purpose |
|-----------|---------|---------|
| **Face Detection** | MediaPipe Face Detection or RetinaFace | Fast, accurate face detection |
| **Face Alignment** | MediaPipe Face Mesh (468 landmarks) | Align faces before embedding |
| **Face Quality** | Custom CNN or SER-FIQ (quality scoring) | Reject blurry/occluded/poorly-lit faces |
| **Face Embedding** | InsightFace (ArcFace/CosFace/AdaFace) via ONNX | State-of-the-art face embeddings |
| **Liveness Detection** | MiniFASNet (FAS) + texture analysis | Anti-spoofing |
| **Image Processing** | OpenCV | General image manipulation |
| **Inference Runtime** | ONNX Runtime (GPU) | Hardware-accelerated inference |

**Why this stack:**

- **InsightFace + ONNX Runtime** is the gold standard for face recognition. ArcFace achieves 99.83% accuracy on LFW. ONNX Runtime enables GPU acceleration on your GTX 1650 without requiring a full PyTorch installation at runtime.
- **MediaPipe** provides real-time face detection and 468-point face mesh at 30+ FPS even on CPU, making it ideal for the webcam pipeline.
- **MiniFASNet** is a lightweight anti-spoofing model specifically designed for face authentication scenarios — it detects printed photos, screen replays, and paper masks with high accuracy.
- Using **ONNX** as the inference format means we decouple from any specific training framework and get cross-platform portability.

### 3.5 Authentication — JWT + Role-Based Access Control

| Component | Choice |
|-----------|--------|
| **Auth tokens** | JWT (access + refresh tokens) |
| **Password hashing** | bcrypt via `passlib` |
| **Roles** | Admin, Instructor, Student |
| **Session** | HTTP-only secure cookies |

**Why JWT:**
- Stateless — scales easily
- Standard for REST APIs
- Works seamlessly with Next.js middleware for protected routes

### 3.6 Testing

| Layer | Tool |
|-------|------|
| **Python unit tests** | pytest + pytest-cov |
| **Python API tests** | httpx + FastAPI TestClient |
| **ML model tests** | Custom benchmark scripts (accuracy, latency, FAR/FRR) |
| **Frontend tests** | Vitest + React Testing Library |
| **E2E tests** | Playwright |
| **Load testing** | Locust (optional) |

### 3.7 Deployment

| Component | Recommendation |
|-----------|---------------|
| **Containerization** | Docker + Docker Compose |
| **Reverse proxy** | Nginx |
| **Target** | Local deployment (college demo) |
| **Optional cloud** | Railway / Render / AWS EC2 with GPU |

---

## 4. Major Modules

### Module Map

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  Login   │  │ Student  │  │  Live    │  │   Dashboard   │   │
│  │  Page    │  │ Mgmt     │  │  Camera  │  │   & Reports   │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘   │
└──────────────────────────┬───────────────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼───────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  Auth    │  │ Student  │  │ Attend-  │  │   Reporting   │   │
│  │ Module   │  │ API      │  │ ance API │  │   Engine      │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              CV / ML Pipeline Engine                      │   │
│  │  ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌────────┐  │   │
│  │  │  Detect │→│ Align  │→│Quality │→│ Live │→│Embedder│  │   │
│  │  └─────────┘ └────────┘ └────────┘ └──────┘ └────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────────┐     │
│  │  PostgreSQL  │  │   Redis    │  │  File Storage        │     │
│  │  (pgvector)  │  │  (cache)   │  │  (face images/models)│     │
│  └──────────────┘  └────────────┘  └──────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

### Module Details

#### M1: Authentication & Authorization
- User registration, login, logout
- JWT token management (access + refresh)
- Role-based access control (Admin, Instructor, Student)
- Password reset flow
- Session management

#### M2: Student Management
- CRUD operations for student profiles
- Student-course enrollment
- Batch import (CSV)
- Student photo gallery

#### M3: Face Registration
- Guided face capture (multiple angles recommended)
- Quality gate — reject low-quality images during enrollment
- Face embedding extraction and storage
- Re-enrollment / update capability
- Multiple face samples per student for robustness

#### M4: Face Detection
- Real-time face detection from webcam stream
- Bounding box extraction
- Multi-face detection support
- Configurable confidence thresholds

#### M5: Face Alignment
- Facial landmark detection (5-point or 68-point)
- Affine transformation to canonical face position
- Ensures consistent input to the embedding model

#### M6: Face Quality Assessment
- **Blur detection** — Laplacian variance
- **Exposure assessment** — histogram analysis
- **Pose estimation** — yaw, pitch, roll angle thresholds
- **Occlusion detection** — partial face coverage
- **Composite quality score** — weighted aggregate
- Reject or warn on low-quality detections

#### M7: Liveness Detection (Anti-Spoofing)
- **Texture analysis** — detect flat/printed surfaces via LBP or CNN
- **Depth estimation** — monocular depth cue analysis (optional)
- **Challenge-response** — blink detection or head-turn prompt (optional)
- **Binary classification** — real vs. spoof with confidence score
- **Research component** — novel hybrid pipeline or ensemble method

#### M8: Face Embedding & Recognition
- Extract 512-d face embeddings using ArcFace/AdaFace
- Cosine similarity matching against enrolled embeddings
- Configurable similarity threshold
- Top-K candidate retrieval
- Unknown face handling

#### M9: Decision Engine
- Fuse scores from quality, liveness, and recognition
- Apply configurable business rules
- Minimum quality threshold gate
- Minimum liveness confidence gate
- Recognition confidence threshold
- Final accept/reject decision with reason code

#### M10: Attendance Management
- Record attendance with metadata (timestamp, confidence, session, device)
- Prevent duplicate marking (cooldown period per student per session)
- Manual override capability for instructors
- Attendance session management (create, start, end)
- Late marking support

#### M11: Dashboard & Visualization
- **Admin dashboard** — system-wide statistics, user management
- **Instructor dashboard** — course attendance rates, student trends
- **Student dashboard** — personal attendance history
- Real-time attendance feed during active sessions
- Charts and graphs (attendance rate over time, per-course breakdown)

#### M12: Reporting Engine
- Daily/weekly/monthly attendance reports
- Per-student attendance percentage
- Per-course analytics
- Export to CSV/PDF
- Alerts for low attendance

#### M13: Audit & Logging
- Log every recognition attempt (image hash, scores, decision)
- Track system access and modifications
- Tamper-evident audit trail

#### M14: Research & Experimentation Module
- Benchmark different face recognition backbones
- Compare liveness detection approaches
- Record and export experimental metrics (accuracy, FAR, FRR, latency)
- Reproducible experiment configurations
- Visualization of research results

---

## 5. Risks

### 5.1 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Python 3.14 incompatibility** with ML libraries (PyTorch, ONNX RT, dlib) | 🔴 High | Install Python 3.11/3.12 in parallel; use virtual environments |
| **GTX 1650 VRAM (4 GB)** insufficient for training | 🟡 Medium | Use pre-trained models + ONNX inference; train in Colab if needed |
| **WebSocket frame drops** under load | 🟡 Medium | Implement frame skipping; process every Nth frame |
| **Node.js not installed** — frontend blocked | 🟢 Low | Simple install via official installer |
| **CMake not installed** — `dlib` compilation will fail | 🟡 Medium | Install CMake, or use MediaPipe/InsightFace which don't require dlib |

### 5.2 Machine Learning Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Low accuracy on diverse skin tones** — facial recognition bias | 🔴 High | Test on diverse datasets (RFW); report bias metrics in research paper |
| **Liveness detection bypass** by high-quality screen replay | 🟡 Medium | Hybrid multi-signal pipeline; never rely on single detector |
| **Face quality rejecting legitimate users** (false rejections) | 🟡 Medium | Calibrate thresholds on test population; provide manual fallback |
| **Embedding model too slow** for real-time on GTX 1650 | 🟡 Medium | Benchmark multiple models; use ONNX optimizations |
| **Small enrollment dataset** — few images per person | 🟡 Medium | Augmentation; multi-sample enrollment; test accuracy vs. sample count |

### 5.3 Privacy & Legal Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Biometric data storage** without consent | 🔴 High | Explicit consent flow; encryption at rest; data retention policy |
| **GDPR/data protection compliance** | 🟡 Medium | Allow data deletion; document data flows in SRS |
| **Face images stored insecurely** | 🔴 High | Encrypt stored images; hash-based integrity; access controls |

### 5.4 Dataset Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **No institutional dataset available** | 🟡 Medium | Create controlled dataset with consenting volunteers |
| **Dataset too small for statistical significance** | 🟡 Medium | Supplement with public datasets (LFW, CASIA-WebFace) for benchmarking |
| **Imbalanced demographics** in test data | 🟡 Medium | Stratified sampling; report per-demographic metrics |

### 5.5 Performance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Real-time pipeline latency > 500ms** | 🟡 Medium | Pipeline profiling; ONNX optimization; frame skipping |
| **Database slow for large embedding searches** | 🟢 Low | pgvector ANN index; Redis embedding cache |
| **Memory leaks from continuous webcam processing** | 🟡 Medium | Explicit resource cleanup; memory profiling |

### 5.6 Research Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Contribution deemed incremental** by reviewers | 🟡 Medium | Clearly define the novel contribution early; compare against baselines |
| **Cannot reproduce published results** for comparison | 🟡 Medium | Use standard benchmarks (LFW, CPLFW, CALFW) with published protocols |
| **Insufficient ablation study** | 🟡 Medium | Plan ablation experiments from the start |

### 5.7 Deployment Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Demo machine differs from dev machine** | 🟡 Medium | Docker containerization; tested on clean environment |
| **Webcam quality varies across hardware** | 🟢 Low | Quality assessment module adapts; test on multiple cameras |
| **Network dependency for demo** | 🟢 Low | Local deployment option; no cloud dependency for core features |

---

## 6. Questions & Decisions Required

> [!IMPORTANT]
> The following decisions must be made before implementation begins.

### Must-Decide

| # | Question | Options | Impact |
|---|----------|---------|--------|
| 1 | **Python version for ML backend** | (a) Try 3.14 first, fallback to 3.11 (b) Install 3.11/3.12 now | Blocks all ML library installation |
| 2 | **Face recognition backbone** | (a) ArcFace-R100 (best accuracy) (b) ArcFace-R50 (good balance) (c) AdaFace (SOTA, newer) (d) Compare all three (research angle) | Affects accuracy & latency |
| 3 | **Liveness detection approach** | (a) MiniFASNet only (b) Texture + blink detection hybrid (c) Depth-based (d) Custom ensemble (research angle) | Core research contribution area |
| 4 | **Research paper focus** | (a) Novel liveness detection pipeline (b) Quality-aware adaptive recognition (c) Lightweight model benchmark for attendance scenarios (d) Other | Shapes the experimental module |
| 5 | **Install Node.js?** | (a) Yes, install Node.js LTS now (b) Wait | Blocks frontend development |
| 6 | **Database: PostgreSQL vs SQLite** | (a) PostgreSQL (production-ready, pgvector) (b) SQLite (simpler setup, no vector search) | Affects architecture and demo simplicity |
| 7 | **Authentication scope** | (a) Full JWT + RBAC (b) Simplified session auth (c) College SSO integration | Affects development timeline |

### Should-Decide

| # | Question | Options | Impact |
|---|----------|---------|--------|
| 8 | **Multi-face simultaneous recognition?** | (a) Yes (b) Single-face only | UI/pipeline complexity |
| 9 | **Attendance mode** | (a) Automatic (walk-by) (b) Self-service (student faces camera) (c) Both | UX design |
| 10 | **Report format** | (a) Web only (b) PDF export (c) CSV export (d) All | Reporting module scope |
| 11 | **Docker for deployment?** | (a) Yes (b) No (direct install) | Need to install Docker |
| 12 | **Target conference/journal for research paper?** | User input needed | Shapes paper format and depth |

---

## 7. Deliverables Summary

| Deliverable | Format | Status |
|-------------|--------|--------|
| Working Software Application | Web app (Next.js + FastAPI) | 🔲 Not started |
| Software Requirements Specification (SRS) | `docs/srs.md` | 🔲 Not started |
| Project Report | `docs/project_report.md` or LaTeX | 🔲 Not started |
| Research Paper | LaTeX (IEEE/ACM format) | 🔲 Not started |
| Source Code | Git repository | 🔲 Not started |
| Test Suite | pytest + Vitest + Playwright | 🔲 Not started |
| User Manual | `docs/user_manual.md` | 🔲 Not started |

---

*This document will be updated as decisions are made and implementation progresses.*
