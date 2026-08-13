# Development Roadmap — Facial Recognition Attendance System

> **Total Estimated Duration:** 10–14 weeks  
> **Date Created:** 2026-08-13  
> **Status:** Proposed — Awaiting Approval

---

## Phase Overview

```
Phase 0 ──▶ Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6 ──▶ Phase 7
 Setup      Backend     CV/ML       Frontend    Integration  Research    Docs &       Polish
 (3 days)   Core        Pipeline    (1.5 wk)    (1 wk)       Experiments Reports      & Demo
            (1.5 wk)    (2–3 wk)                             (2 wk)      (2 wk)       (1 wk)
```

---

## Phase 0: Environment Setup & Foundation (3 days)

> **Goal:** Establish a fully working development environment and project scaffolding.

### Tasks

- [ ] **P0.1** Validate Python compatibility with ML libraries
  - Test if PyTorch / ONNX Runtime / OpenCV install on Python 3.14
  - If not: install Python 3.11 or 3.12 alongside; configure virtual environment
- [ ] **P0.2** Install Node.js LTS (v22.x)
  - Install via official Windows installer
  - Verify `node`, `npm`, `npx` work
- [ ] **P0.3** Install and configure PostgreSQL 16
  - Install PostgreSQL
  - Create project database
  - Install `pgvector` extension
- [ ] **P0.4** Install Redis
  - Install Redis for Windows (via WSL2 or Memurai/Redis Windows port)
- [ ] **P0.5** Initialize Git repository
  - `git init`
  - Create `.gitignore` (Python, Node.js, data, models, .env)
  - Initial commit
- [ ] **P0.6** Create project directory structure
  - Set up `backend/`, `frontend/`, `data/`, `research/`, `docs/`, `scripts/`
- [ ] **P0.7** Set up Python virtual environment
  - Create venv for backend
  - Install initial dependencies (FastAPI, uvicorn, SQLAlchemy, alembic, pydantic)
  - Create `pyproject.toml`
- [ ] **P0.8** Scaffold Next.js frontend
  - `npx create-next-app@latest` with TypeScript, Tailwind, App Router
  - Install shadcn/ui
- [ ] **P0.9** Create `docker-compose.yml`
  - PostgreSQL + Redis containers (for consistent dev environment)
- [ ] **P0.10** Download pre-trained ML models
  - ArcFace ONNX model
  - MiniFASNet ONNX model
  - MediaPipe face detection model
  - Store in `data/models/`

### Deliverables
- ✅ Working Python environment with ML library compatibility confirmed
- ✅ Working Node.js environment
- ✅ PostgreSQL + Redis running
- ✅ Git repo initialized with clean structure
- ✅ Both backend and frontend servers start without errors
- ✅ Pre-trained models downloaded

---

## Phase 1: Backend Core (1.5 weeks)

> **Goal:** Build the complete REST API with authentication, database models, and CRUD operations — no ML yet.

### Tasks

- [ ] **P1.1** Database models (SQLAlchemy 2.0)
  - User, Student, Course, Enrollment, AttendanceSession, AttendanceRecord, FaceEmbedding, AuditLog
  - Alembic initial migration
- [ ] **P1.2** Authentication system
  - JWT access + refresh token generation
  - Login, logout, token refresh endpoints
  - Password hashing with bcrypt
  - Role-based middleware (Admin, Instructor, Student)
- [ ] **P1.3** Student management API
  - CRUD endpoints for students
  - Batch import from CSV
  - Input validation with Pydantic
- [ ] **P1.4** Course management API
  - CRUD endpoints for courses
  - Student enrollment/unenrollment
- [ ] **P1.5** Attendance management API
  - Session creation (instructor creates a session for a class)
  - Manual attendance marking
  - Attendance record retrieval with filters
  - Duplicate prevention (cooldown logic)
- [ ] **P1.6** Reporting API
  - Per-course attendance report
  - Per-student attendance summary
  - Date range filtering
  - CSV export endpoint
- [ ] **P1.7** Audit logging
  - Middleware to log all mutating API calls
  - Audit log retrieval endpoint (admin only)
- [ ] **P1.8** Configuration & environment management
  - `.env` file support with pydantic-settings
  - Settings for DB, Redis, JWT secret, model paths, thresholds
- [ ] **P1.9** API tests
  - Write pytest tests for all endpoints
  - Test authentication flows
  - Test RBAC enforcement

### Deliverables
- ✅ All REST API endpoints functional and tested
- ✅ Database schema created with migrations
- ✅ JWT auth working
- ✅ Swagger/OpenAPI docs auto-generated at `/docs`
- ✅ 80%+ test coverage on API layer

---

## Phase 2: Computer Vision & ML Pipeline (2–3 weeks)

> **Goal:** Build the complete face recognition pipeline — detection → alignment → quality → liveness → embedding → matching → decision.

### Week 1: Detection, Alignment, Quality

- [ ] **P2.1** Face detector module
  - Implement `FaceDetector` class wrapping MediaPipe
  - Input: RGB image → Output: list of bounding boxes + confidence
  - Support configurable confidence threshold
  - Unit tests with sample images
- [ ] **P2.2** Face aligner module
  - Implement `FaceAligner` class
  - 5-point landmark detection
  - Affine transform to 112×112 aligned face
  - Unit tests
- [ ] **P2.3** Face quality assessor module
  - Implement `QualityAssessor` class
  - Blur detection (Laplacian variance)
  - Exposure analysis (histogram-based)
  - Pose estimation (yaw/pitch/roll from landmarks)
  - Occlusion detection
  - Composite quality score (0.0–1.0)
  - Configurable thresholds
  - Unit tests with good/bad quality sample images

### Week 2: Liveness, Embeddings, Matching

- [ ] **P2.4** Liveness detector module
  - Implement `LivenessDetector` class
  - Load MiniFASNet ONNX model
  - Texture analysis pipeline (LBP features)
  - Binary classification: real vs. spoof
  - Confidence score output
  - Unit tests with real and spoofed images
- [ ] **P2.5** Face embedder module
  - Implement `FaceEmbedder` class
  - Load ArcFace ONNX model via ONNX Runtime (GPU)
  - Input: aligned 112×112 face → Output: 512-d embedding vector
  - Batch inference support
  - Unit tests
- [ ] **P2.6** Face matcher module
  - Implement `FaceMatcher` class
  - Cosine similarity computation
  - Load enrolled embeddings from Redis cache (fallback to PostgreSQL)
  - Top-K retrieval
  - Configurable similarity threshold
  - Unit tests

### Week 3: Pipeline Integration & Face Registration

- [ ] **P2.7** Decision engine
  - Implement `DecisionEngine` class
  - Fuse quality, liveness, and similarity scores
  - Apply business rules (cooldown, session validity)
  - Return structured decision with reason codes
- [ ] **P2.8** Pipeline orchestrator
  - Implement `RecognitionPipeline` class
  - Chain: Detect → Align → Quality → Liveness → Embed → Match → Decide
  - Error handling at each stage
  - Performance timing and logging
  - Pipeline benchmarking script
- [ ] **P2.9** Face registration endpoint
  - POST `/api/v1/students/{id}/enroll-face`
  - Capture multiple face samples
  - Run through quality gate
  - Extract and store embeddings
  - Update Redis cache
- [ ] **P2.10** WebSocket recognition endpoint
  - `/ws/recognition` WebSocket handler
  - Frame decoding (base64 → numpy array)
  - Pipeline execution per frame
  - Backpressure / frame skipping
  - Real-time result streaming
- [ ] **P2.11** Pipeline integration tests
  - End-to-end test: image → attendance record
  - Latency benchmarks
  - Accuracy benchmarks on test set

### Deliverables
- ✅ All CV modules working independently with unit tests
- ✅ Complete pipeline processes a frame in < 100ms
- ✅ Face registration stores embeddings correctly
- ✅ WebSocket recognition endpoint streams results
- ✅ Pipeline performance benchmarks documented

---

## Phase 3: Frontend Development (1.5 weeks)

> **Goal:** Build a polished, responsive web UI with all pages and real-time webcam integration.

### Tasks

- [ ] **P3.1** Design system & layout
  - Configure Tailwind theme (colors, fonts)
  - Create layout components (sidebar, header, main content)
  - Set up shadcn/ui components
  - Dark mode support
- [ ] **P3.2** Authentication pages
  - Login page with form validation
  - Protected route middleware
  - Logout functionality
  - Token refresh logic
- [ ] **P3.3** Dashboard page
  - Admin dashboard: system stats, recent activity
  - Instructor dashboard: course stats, today's attendance
  - Student dashboard: personal attendance summary
  - Charts (Recharts)
- [ ] **P3.4** Student management pages
  - Student list with search, filter, pagination
  - Student detail page
  - Add/edit student form
  - CSV import interface
- [ ] **P3.5** Face registration page
  - Webcam capture interface (`react-webcam`)
  - Guided capture flow (front, left, right angles)
  - Quality feedback in real-time
  - Enrollment confirmation
- [ ] **P3.6** Live attendance page
  - Real-time webcam feed
  - WebSocket connection to backend
  - Live recognition results overlay on video
  - Recognized students list (live-updating)
  - Session start/stop controls
  - Visual indicators (green = recognized, red = unknown, yellow = low quality)
- [ ] **P3.7** Attendance history & reports
  - Session list with date filtering
  - Session detail (who was present)
  - Per-student attendance history
  - Per-course attendance analytics
  - Export buttons (CSV)
- [ ] **P3.8** Admin pages
  - User management
  - System configuration
  - Audit log viewer
- [ ] **P3.9** Frontend tests
  - Component tests with Vitest + React Testing Library
  - Key user flow tests

### Deliverables
- ✅ All pages built and navigable
- ✅ Webcam integration working in browser
- ✅ Real-time recognition results displayed
- ✅ Responsive design (desktop + tablet)
- ✅ Dark mode functional
- ✅ Frontend component tests passing

---

## Phase 4: Full Integration & End-to-End Testing (1 week)

> **Goal:** Connect everything, fix integration bugs, optimize performance.

### Tasks

- [ ] **P4.1** End-to-end integration testing
  - Full flow: login → start session → face recognition → attendance recorded → view report
  - Multi-user concurrent testing
- [ ] **P4.2** Performance optimization
  - Profile the recognition pipeline (identify bottlenecks)
  - Optimize ONNX model inference settings
  - Tune frame skip rate for smooth UX
  - Database query optimization
- [ ] **P4.3** Error handling & edge cases
  - No face detected
  - Multiple faces detected
  - Low quality images
  - Spoof detected
  - Unknown person
  - Network interruption during WebSocket
  - Concurrent sessions
- [ ] **P4.4** Security hardening
  - Rate limiting on API endpoints
  - Input sanitization
  - CORS configuration
  - Secure cookie settings
- [ ] **P4.5** Data seeding
  - Create scripts to populate test data
  - Seed demo users, students, courses
  - Generate synthetic attendance history

### Deliverables
- ✅ Full system working end-to-end
- ✅ All edge cases handled gracefully
- ✅ Performance within acceptable targets
- ✅ Security review complete

---

## Phase 5: Research & Experimentation (2 weeks)

> **Goal:** Conduct experiments, gather metrics, and prepare material for the research paper.

### Tasks

- [ ] **P5.1** Define research contribution
  - Finalize the novel contribution topic
  - Write experiment hypotheses
- [ ] **P5.2** Set up experiment framework
  - Reproducible experiment configs (YAML)
  - Automated metric collection
  - Results logging to CSV/JSON
- [ ] **P5.3** Baseline experiments
  - Benchmark ArcFace-R50, ArcFace-R100, AdaFace on standard datasets
  - Measure: accuracy, FAR, FRR, latency
  - Document baseline results
- [ ] **P5.4** Novel contribution experiments
  - Implement the proposed improvement
  - Ablation studies
  - Comparison against baselines
  - Statistical significance testing
- [ ] **P5.5** Liveness detection evaluation
  - Test against: printed photos, screen replay, video replay
  - Measure: APCER, BPCER, ACER
  - Compare liveness methods
- [ ] **P5.6** Quality assessment impact study
  - Measure recognition accuracy vs. quality thresholds
  - Plot quality-accuracy curves
  - Determine optimal quality gate settings
- [ ] **P5.7** Bias & fairness analysis
  - Test on diverse demographic groups
  - Report per-group accuracy metrics
  - Discuss ethical considerations
- [ ] **P5.8** Visualization of results
  - Create publication-quality charts and tables
  - ROC curves, DET curves, confusion matrices
  - Latency distribution plots

### Deliverables
- ✅ Complete experiment results with statistical rigor
- ✅ Publication-quality visualizations
- ✅ Clear novel contribution demonstrated
- ✅ Reproducible experiment code

---

## Phase 6: Documentation (2 weeks)

> **Goal:** Complete all academic and technical documentation.

### Tasks

- [ ] **P6.1** Software Requirements Specification (SRS)
  - IEEE 830 format
  - Functional requirements
  - Non-functional requirements (performance, security, usability)
  - Use case diagrams
  - System requirements
  - Data flow diagrams
- [ ] **P6.2** Project report
  - Introduction & problem statement
  - Literature review
  - System design & architecture
  - Implementation details
  - Testing results
  - Conclusion & future work
  - Screenshots and diagrams
- [ ] **P6.3** Research paper
  - Abstract
  - Introduction
  - Related Work
  - Proposed Method
  - Experimental Setup
  - Results & Discussion
  - Conclusion
  - References
  - Format: IEEE or ACM conference template
- [ ] **P6.4** User manual
  - Installation guide
  - Admin guide
  - Instructor guide
  - Student guide
- [ ] **P6.5** API documentation
  - Verify auto-generated OpenAPI docs are complete
  - Add examples and descriptions

### Deliverables
- ✅ Complete SRS document
- ✅ Complete project report
- ✅ Research paper draft (ready for review)
- ✅ User manual
- ✅ API documentation

---

## Phase 7: Polish, Demo & Submission (1 week)

> **Goal:** Final polish, demo preparation, and submission readiness.

### Tasks

- [ ] **P7.1** UI polish
  - Animations and transitions
  - Loading states
  - Error messages UX
  - Accessibility basics
- [ ] **P7.2** Demo preparation
  - Create demo script (step-by-step)
  - Set up demo data
  - Test on clean machine (or Docker)
  - Prepare backup plan for live demo failures
- [ ] **P7.3** Docker deployment
  - Finalize `docker-compose.yml`
  - Test full system in containers
  - Write deployment README
- [ ] **P7.4** Code cleanup
  - Remove debug code
  - Consistent code formatting (Black, ESLint)
  - Docstrings and comments
  - Final git commit and tag
- [ ] **P7.5** Presentation preparation
  - PowerPoint / Google Slides
  - Key architecture diagrams
  - Demo video recording (backup)
  - Research contribution summary slide

### Deliverables
- ✅ Polished, demo-ready application
- ✅ Docker deployment working
- ✅ Presentation prepared
- ✅ All documents finalized
- ✅ Git repository clean and tagged

---

## Timeline Summary

| Phase | Description | Duration | Cumulative |
|-------|-------------|----------|------------|
| **Phase 0** | Environment Setup | 3 days | Week 0.5 |
| **Phase 1** | Backend Core | 1.5 weeks | Week 2 |
| **Phase 2** | CV/ML Pipeline | 2–3 weeks | Week 4–5 |
| **Phase 3** | Frontend | 1.5 weeks | Week 6 |
| **Phase 4** | Integration & Testing | 1 week | Week 7 |
| **Phase 5** | Research & Experiments | 2 weeks | Week 9 |
| **Phase 6** | Documentation | 2 weeks | Week 11 |
| **Phase 7** | Polish & Demo | 1 week | Week 12 |

> [!NOTE]
> Phases 5 and 6 can partially overlap — begin writing the SRS and project report structure during earlier phases, and fill in details as implementation progresses.

> [!TIP]
> **Recommended approach:** Start a lightweight SRS skeleton during Phase 0, update it incrementally during Phases 1–4, then finalize during Phase 6. This prevents a documentation crunch at the end.

---

## Critical Path

The critical path (longest sequential dependency chain) is:

```
P0 (Setup) → P2 (CV Pipeline) → P4 (Integration) → P5 (Research)
```

- The **CV/ML Pipeline (Phase 2)** is the highest-risk, longest-duration phase
- **Phase 1 (Backend)** and **Phase 3 (Frontend)** can partially overlap with Phase 2
- **Phase 5 (Research)** depends on a working pipeline for experiments
- **Phase 6 (Docs)** can start skeleton work as early as Phase 0

---

## Milestone Checkpoints

| Milestone | Target | Criteria |
|-----------|--------|----------|
| **M1: Dev Ready** | End of Phase 0 | Both servers start, DB connected, models downloaded |
| **M2: API Complete** | End of Phase 1 | All REST endpoints tested, auth working |
| **M3: Pipeline Working** | End of Phase 2 | Face recognition pipeline < 100ms, WebSocket streaming |
| **M4: UI Complete** | End of Phase 3 | All pages built, webcam integration working |
| **M5: System Integrated** | End of Phase 4 | Full end-to-end flow working |
| **M6: Research Complete** | End of Phase 5 | Experiments done, novel contribution demonstrated |
| **M7: Docs Complete** | End of Phase 6 | SRS, report, and paper drafts ready |
| **M8: Submission Ready** | End of Phase 7 | Everything polished, demo prepared |

---

*This roadmap will be updated as the project progresses and decisions are made.*
