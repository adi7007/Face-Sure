# System Architecture Specification

**Document Identifier:** `docs/Architecture/system_architecture.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. High-Level System Architecture

The Facial Recognition Attendance System is designed as a decoupled, multi-tier web application combining an asynchronous FastAPI backend service, a Next.js single-page frontend application, a PostgreSQL relational database with vector search (`pgvector`), a Redis cache/queue, and an embedded computer vision ML pipeline.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                         Next.js 14 Web Application                             │   │
│   │   ┌──────────────────────┐  ┌───────────────────────┐  ┌───────────────────┐   │   │
│   │   │  Webcam Stream (W3C) │  │ Real-time Kiosk UI    │  │ Admin/Teacher UI  │   │   │
│   │   └──────────┬───────────┘  └───────────┬───────────┘  └─────────┬─────────┘   │   │
│   └──────────────┼──────────────────────────┼────────────────────────┼─────────────┘   │
└──────────────────┼──────────────────────────┼────────────────────────┼─────────────────┘
                   │ (MediaStream API)        │ (WebSocket /wss)       │ (REST /HTTPS)
                   ▼                          ▼                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   APPLICATION LAYER                                    │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                           FastAPI Web Server (Python)                          │   │
│   │   ┌──────────────────┐   ┌────────────────────────┐   ┌────────────────────┐   │   │
│   │   │  API Routers     │   │  JWT Auth & Security   │   │  WebSocket Router  │   │   │
│   │   │  (/v1/*)         │   │  Middleware            │   │  (/ws/recognize)   │   │   │
│   │   └────────┬─────────┘   └───────────┬────────────┘   └──────────┬─────────┘   │   │
│   │            │                         │                           │             │   │
│   │            ▼                         ▼                           ▼             │   │
│   │   ┌────────────────────────────────────────────────────────────────────────┐   │   │
│   │   │                     Business Service Layer                             │   │
│   │   │  (StudentService, SessionService, AttendanceService, ReportingService) │   │   │
│   │   └──────────────────────────────────┬─────────────────────────────────────┘   │   │
│   └──────────────────────────────────────┼─────────────────────────────────────────┘   │
└──────────────────────────────────────────┼─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI / ML COMPUTER VISION PIPELINE                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                      Pipeline Orchestrator (Async Engine)                      │   │
│   │  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │
│   │  │  RetinaFace   │─►│ Quality      │─►│ MiniFASNet   │─►│ ArcFace 512D     │   │   │
│   │  │  (Detect/Align│  │  Assessor    │  │  (Liveness)  │  │ (Embedder)       │   │   │
│   │  └───────────────┘  └──────────────┘  └──────────────┘  └─────────┬────────┘   │   │
│   │                                                                   │            │   │
│   │                                                                   ▼            │   │
│   │                                                         ┌──────────────────┐   │   │
│   │                                                         │ QMF-Score Engine │   │   │
│   │                                                         │ (Dynamic Tau)    │   │   │
│   │                                                         └──────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA STORAGE LAYER                                   │
│   ┌──────────────────────────────────────┐    ┌──────────────────────────────────┐   │
│   │  PostgreSQL 16 + pgvector            │    │  Redis Cache Server              │   │
│   │  - Relational Schema (Users, Sessions│    │  - JWT Revocation Blacklist      │   │
│   │  - Encrypted Vectors (HNSW Index)    │    │  - Rate Limiting Counters        │   │
│   │  - Recognition & Audit Logs          │    │  - Real-time Active Kiosk State  │   │
│   └──────────────────────────────────────┘    └──────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Subsystem Specifications

### 2.1 Web Client Subsystem (Frontend)
* **Framework:** Next.js 14 (App Router) with React 18, TypeScript, and Tailwind CSS.
* **Camera Integration:** HTML5 `getUserMedia()` WebRTC camera capture capturing 1280x720 RGB frames.
* **Kiosk Video Canvas:** HTML5 `<canvas>` rendering 30 FPS video with real-time visual feedback bounding boxes (Green = Authenticated, Yellow = Quality/Liveness Warning, Red = Spoof/Unknown).
* **Communication:** Axios HTTP client for REST API endpoints (`/v1/*`); Native WebSockets (`/ws/recognize`) for streaming frame transfer.
* **State Management:** React Context API + Zustand lightweight state container.

### 2.2 API & Server Subsystem (Backend Core)
* **Framework:** FastAPI running on Uvicorn / Gunicorn ASGI server.
* **Router Structure:**
  * `/api/v1/auth`: Registration, login, token refresh, logout.
  * `/api/v1/students`: Student CRUD, course enrollment, biometric sample upload.
  * `/api/v1/courses`: Course creation, instructor assignment, roster management.
  * `/api/v1/sessions`: Attendance session open/pause/close/status.
  * `/api/v1/attendance`: Attendance records, manual overrides, student history.
  * `/api/v1/reports`: Statistics, CSV/Excel/PDF export triggers.
  * `/api/v1/system`: System health check, configuration parameters, audit logs.
  * `/ws/recognize`: Full-duplex WebSocket stream for kiosk frame verification.
* **Dependency Injection:** Database sessions via SQLAlchemy async session maker; current authenticated user resolved via `get_current_user` FastAPI dependency.

### 2.3 Computer Vision Subsystem (AI Layer)
* **Detection & Alignment:** RetinaFace (ResNet-50 backbone, ONNX Runtime execution). Generates 5 2D facial landmarks; applies similarity transform to yield 112x112 normalized face crops.
* **Quality Assessor:** Multi-component metric assessing head pose ($\theta_{yaw, pitch, roll}$), Laplacian variance sharpness ($S_{sharp}$), and brightness uniformity ($I_{illum}$).
* **Liveness Detector:** MiniFASNetV2 (Squeeze-and-Excitation MobileNet backbone) yielding continuous liveness confidence $L_{live} \in [0, 1]$.
* **Embedding Model:** ArcFace ResNet-50 producing 512-dimensional $L_2$-normalized feature vectors.
* **Decision Engine (QMF-Score):** Unifies Cosine Similarity ($S_{match}$), Sample Quality ($Q_{sample}$), and Liveness ($L_{live}$) into composite score $C(x)$ evaluated against dynamic threshold $\tau(Q)$.

### 2.4 Data Storage Subsystem
* **PostgreSQL 16:** Primary relational store. Stores application tables (`users`, `students`, `courses`, `enrollments`, `attendance_sessions`, `attendance_records`, `recognition_events`, `audit_logs`).
* **pgvector Extension:** Vector column type `vector(512)` indexed with Hierarchical Navigable Small World (HNSW) cosine index (`m=16`, `ef_construction=64`).
* **Redis 7:** In-memory store for rate limiting counters, WebSocket kiosk session state, and JWT token revocation blacklists.

### 2.5 Security & Audit Subsystem
* **Authentication:** JWT tokens (HMAC-SHA256). Password hashing via bcrypt (cost factor 12).
* **Encryption at Rest:** Biometric vector payload encryption using AES-256-GCM.
* **Zero Image Storage:** Video frames processed purely in volatile RAM; destroyed immediately after feature extraction.
* **Audit Logging:** System-wide immutable security log recording user actions, IP addresses, timestamps, and payload hashes.
