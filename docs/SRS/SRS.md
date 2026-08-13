# Software Requirements Specification (SRS)
## Facial Recognition Attendance System with Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)

**Document Identifier:** `docs/SRS/SRS.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Status:** Approved Specification  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the complete functional, non-functional, technical, security, and privacy requirements for the **Facial Recognition Attendance System**. The system integrates advanced computer vision algorithms—specifically RetinaFace face detection, ArcFace deep feature embedding, MiniFASNet presentation attack detection (liveness), and a novel **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** decision engine—with an enterprise backend (FastAPI, PostgreSQL with `pgvector`, Redis) and a modern web application (Next.js, Tailwind CSS).

### 1.2 Scope
The software system provides an automated, non-contact, highly secure biometric attendance management platform for academic institutions and organizations. The scope includes:
* Multi-role user authentication and access control (Admin, Instructor, Student).
* Student enrollment with multi-angle biometric facial feature registration.
* Real-time webcam video stream processing for automated attendance verification.
* Multi-stage computer vision pipeline: Face Detection, Alignment, Quality Assessment, Liveness Verification, 512D Vector Embedding Extraction, and Vector Search.
* **QMF-Score Engine:** Dynamic quality-adaptive thresholding ($\tau(Q)$) and multi-factor confidence scoring to minimize false rejections under non-ideal video conditions.
* Course, session, and roster management.
* Anti-duplication controls, manual override capabilities, and real-time attendance dashboards.
* Data export (CSV, Excel, PDF), compliance reporting, and security audit logging.
* GDPR Article 9 privacy design: zero raw image retention on backend servers, AES-256 encrypted embedding storage.

### 1.3 Intended Audience
This document is intended for:
* **Software Engineering Team:** Developers, CV/ML engineers, and database administrators implementing the software.
* **Academic Review Board & Examiners:** Evaluators reviewing the capstone project and research paper.
* **System Administrators:** IT staff deploying, maintaining, and auditing the application environment.

### 1.4 Definitions
* **Biometric Embedding:** A 512-dimensional $L_2$-normalized floating-point vector extracted from a facial image, representing discriminative facial features in a hyperspherical vector space.
* **QMF-Score:** Quality-Aware Multi-Factor Confidence Score, a unified inference metric combining Cosine Match Similarity ($S_{match}$), Sample Quality ($Q_{sample}$), and Liveness Confidence ($L_{live}$).
* **Dynamic Threshold ($\tau(Q)$):** An adaptively scaled matching decision threshold that varies inversely with facial sample quality.
* **Presentation Attack Detection (PAD):** Mechanisms designed to detect biometric spoofing attempts (e.g., printed photographs, digital video replays on smartphones/tablets).

### 1.5 Acronyms
* **API:** Application Programming Interface
* **ACER:** Average Classification Error Rate
* **FAR:** False Acceptance Rate
* **FRR:** False Rejection Rate
* **FQA:** Face Image Quality Assessment
* **GDPR:** General Data Protection Regulation
* **HNSW:** Hierarchical Navigable Small World (Vector Indexing Algorithm)
* **JWT:** JSON Web Token
* **ORM:** Object-Relational Mapping
* **RBAC:** Role-Based Access Control
* **SRS:** Software Requirements Specification

### 1.6 References
1. IEEE Std 830-1998: *IEEE Recommended Practice for Software Requirements Specifications*.
2. ISO/IEC 29794-5:2024: *Information technology — Biometric sample quality — Part 5: Face image data*.
3. J. Deng et al., "ArcFace: Additive Angular Margin Loss for Deep Face Recognition," CVPR 2019.
4. Project Documentation: `docs/architecture.md`, `docs/Research_Paper/research_gap.md`, `docs/Research_Paper/research_methodology.md`.

---

## 2. Overall Description

### 2.1 Product Perspective
The Facial Recognition Attendance System is a self-contained, enterprise web application. It operates in a client-server web architecture where the frontend (Next.js SPA) communicates with the backend (FastAPI REST & WebSockets) over TLS-encrypted connections. The backend interfaces with a PostgreSQL relational database utilizing the `pgvector` extension for high-performance vector indexing.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [Next.js Web Client] ◄──(HTTP/WS REST+JSON)──► [FastAPI Backend Server]          │
│       │                                                │                        │
│ (Webcam Video Stream)                                  ├──► [Redis Cache/Queue]  │
│                                                        └──► [PostgreSQL+pgvector]│
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Product Functions
1. **Authentication & User Management:** Secure sign-in, JWT token lifecycle management, role-based authorization (Admin, Instructor, Student).
2. **Student & Roster Enrollment:** Student profile creation, course enrollment, multi-image biometric registration.
3. **Real-Time Attendance Kiosk:** Interactive webcam stream capture, real-time bounding box visualization, liveness feedback, and automated attendance logging.
4. **Biometric CV Processing:** RetinaFace detection/alignment, composite quality scoring, MiniFASNet liveness checking, ArcFace embedding extraction, and `pgvector` HNSW vector matching.
5. **QMF-Score Decision Logic:** Dynamic quality-adaptive thresholding to handle low-resolution, tilted, or dimly lit faces without sacrificing security.
6. **Attendance Management:** Manual session control, manual attendance overrides, duplicate attempt suppression, and student attendance logs.
7. **Analytics & Reporting:** Visual attendance dashboards, statistical summaries (attendance rate, punctuality), export to CSV/Excel/PDF.
8. **Security & Audit:** AES-256 biometric vector encryption, password hashing via bcrypt, zero raw-image backend persistence, audit trail logging.

### 2.3 User Classes and Characteristics
* **System Administrator:** High technical expertise. Responsible for user management, system configuration, database backups, and security audit log reviews.
* **Instructor / Teacher:** Moderate technical expertise. Responsible for creating attendance sessions, monitoring live student check-ins, reviewing reports, and applying manual overrides.
* **Student:** Basic technical expertise. Uses the kiosk interface to register biometric samples during enrollment and log attendance via facial verification.

### 2.4 Operating Environment
* **Server Environment:** Windows 10/11 or Linux (Ubuntu 22.04 LTS), Python 3.14+, Node.js 22 LTS, PostgreSQL 16+ with `pgvector`, Redis 7+.
* **Client Environment:** Modern web browsers (Google Chrome 120+, Microsoft Edge 120+, Firefox 120+, Safari 17+) supporting HTML5 WebRTC webcam APIs and WebSockets.
* **Hardware Environment:** Standard PC/Laptop with x86_64 CPU (4+ cores), 8GB+ RAM, integrated HD webcam (720p/1080p). Optional NVIDIA GPU (GTX 1650+) for accelerated CUDA inference.

### 2.5 Design Constraints
* **Language & Frameworks:** Backend strictly in Python (FastAPI, SQLAlchemy 2.0); Frontend strictly in JavaScript/TypeScript (Next.js, Tailwind CSS).
* **Database Engine:** PostgreSQL with `pgvector` extension; no proprietary database systems.
* **Privacy Compliance:** Must conform to GDPR Article 9 design guidelines; no persistent raw face images stored on backend servers.
* **Real-Time Constraint:** Real-time video processing latency must remain under 50ms per frame to maintain $\ge 20$ FPS visual feedback.

### 2.6 Assumptions and Dependencies
* **Assumptions:**
  * Kiosk devices have a functional webcam with adequate surrounding ambient lighting ($\ge 100$ lux).
  * Students register biometric samples during an initial supervised onboarding session.
* **Dependencies:**
  * ONNX Runtime GPU / CPU execution providers.
  * InsightFace and MediaPipe computer vision packages.
  * PostgreSQL database availability.

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization
* **FR-001 (User Login):** The system shall authenticate users (Admins, Instructors, Students) using email/username and password, returning JWT access and refresh tokens upon successful authentication.
* **FR-002 (Role-Based Access Control):** The system shall enforce strict RBAC, restricting access to administrative endpoints (user creation, system settings) exclusively to users with the `ADMIN` role.
* **FR-003 (Token Refresh & Logout):** The system shall provide secure JWT token refresh endpoints and immediate token revocation upon user logout.

### 3.2 Student Management & Enrollment
* **FR-004 (Student Profile CRUD):** The system shall allow Admins and Instructors to create, read, update, and soft-delete student records (Student ID, Full Name, Email, Department, Enrollment Status).
* **FR-005 (Course & Roster Management):** The system shall support creating courses and assigning students to course rosters.
* **FR-006 (Biometric Registration Capture):** The system shall guide the student through capturing 3 to 5 distinct facial sample angles (frontal, $15^\circ$ left yaw, $15^\circ$ right yaw, slight upward pitch) during initial enrollment.
* **FR-007 (Biometric Quality Validation on Registration):** The system shall reject registration frames that fail quality criteria (blur variance $< 80.0$, face size $< 100 \times 100$ pixels, extreme pose $> 30^\circ$).
* **FR-008 (Biometric Embedding Persistence):** The system shall convert approved registration frames into 512-dimensional ArcFace feature vectors, encrypt the vectors via AES-256, store them in PostgreSQL `pgvector`, and discard the source image files.

### 3.3 Computer Vision Pipeline & QMF-Score Engine
* **FR-009 (Face Detection & Landmark Alignment):** The system shall detect human faces in video frames using RetinaFace, extract 5 facial landmarks, and perform affine transformation to crop 112x112 aligned face patches.
* **FR-010 (Composite Quality Assessment):** The system shall calculate a Composite Quality Score $Q_{sample} \in [0, 1]$ evaluating pose angles ($\theta_{yaw, pitch, roll}$), Laplacian variance sharpness ($S_{sharp}$), and brightness uniformity ($I_{lum}$).
* **FR-011 (Liveness Verification / Anti-Spoofing):** The system shall analyze aligned face patches using MiniFASNetV2 to produce a continuous liveness probability $L_{live} \in [0, 1]$, rejecting presentation attack attempts ($L_{live} < 0.40$).
* **FR-012 (Deep Feature Embedding Extraction):** The system shall extract a 512-dimensional $L_2$-normalized feature vector from valid face patches using ArcFace ResNet-50.
* **FR-013 (QMF-Score Decision Engine):** The system shall compute the unified multi-factor confidence metric:
  $$C(x) = \alpha \cdot S_{match} + \beta \cdot Q_{sample} + \gamma \cdot L_{live}$$
  and compare it against the dynamic quality-adaptive threshold $\tau(Q) = \tau_{base} - \lambda(Q_{sample} - \bar{Q})$.

### 3.4 Attendance Session & Record Management
* **FR-014 (Session Lifecycle Management):** Instructors shall be able to open, pause, resume, and close attendance sessions for specific courses with configurable time windows.
* **FR-015 (Automated Attendance Marking):** When the QMF-Score engine authenticates a student, the system shall automatically record their attendance status (`PRESENT` or `LATE`) based on session timestamps.
* **FR-016 (Duplicate Attempt Suppression):** The system shall ignore duplicate successful recognitions for the same student within a configurable cooldown period (default: 5 minutes) during an active session.
* **FR-017 (Manual Attendance Override):** Instructors shall have authority to manually override student attendance status (`PRESENT`, `ABSENT`, `EXCUSED`, `LATE`) with mandatory justification logging.
* **FR-018 (Attendance History & Dashboard):** Students shall be able to view their personal attendance records; Instructors and Admins shall view aggregated course attendance dashboards.

### 3.5 Reporting, Export & Audit Logging
* **FR-019 (Report Generation & Export):** The system shall generate course attendance summaries and export data in CSV, Excel (.xlsx), and PDF formats.
* **FR-020 (Security Audit Logging):** The system shall log all sensitive system events (login attempts, biometric enrollments, manual overrides, data exports) with timestamp, user ID, IP address, and event details in an immutable audit log.

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
* **NFR-001 (Frame Latency):** Computer vision pipeline frame processing (detection to decision) shall execute within **< 45ms** per frame on GPU hardware and **< 80ms** on CPU hardware.
* **NFR-002 (Vector Search Latency):** PostgreSQL `pgvector` HNSW vector similarity queries shall return top-1 matches in **< 10ms** for database scales up to 10,000 enrolled identities.
* **NFR-003 (Kiosk Throughput):** The live webcam verification stream shall maintain a smooth feedback frame rate of $\ge 20$ frames per second (FPS).

### 4.2 Accuracy & Reliability Requirements
* **NFR-004 (Biometric Accuracy):** Under standard operating conditions ($Q_{sample} \ge 0.50$), the system shall achieve a True Acceptance Rate $\ge 99.2\%$ at False Acceptance Rate $\text{FAR} \le 10^{-4}$.
* **NFR-005 (Anti-Spoofing ACER):** The liveness detection subsystem shall achieve an Average Classification Error Rate $\text{ACER} \le 1.5\%$ against 2D print and digital display replay attacks.
* **NFR-006 (System Reliability):** The backend API service shall maintain an operational availability of $\ge 99.5\%$ during scheduled academic hours.

### 4.3 Security & Privacy Requirements
* **NFR-007 (Password Security):** All user passwords shall be hashed using bcrypt with a minimum work factor of 12 before database storage.
* **NFR-008 (Biometric Vector Protection):** Biometric feature embeddings stored in PostgreSQL shall be encrypted at rest using AES-256-GCM symmetric encryption.
* **NFR-009 (Zero Image Persistence):** The system backend shall never persist raw facial images to disk or database storage during attendance verification; video frames shall exist purely in volatile RAM during frame execution.
* **NFR-010 (Transport Security):** All HTTP and WebSocket communications between client and server shall use TLS 1.3 encryption (HTTPS / WSS).

### 4.4 Usability & Accessibility Requirements
* **NFR-011 (Kiosk Feedback):** The webcam kiosk UI shall provide real-time visual bounding box overlays (Green = Authenticated, Yellow = Quality/Liveness Warning, Red = Spoof/Unrecognized) with clear status text within 100ms of state changes.
* **NFR-012 (Responsive Interface):** The web dashboard shall be fully responsive across desktop, tablet, and mobile viewport sizes ($\ge 320\text{px}$ width).

---

## 5. Security Requirements

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             SECURITY ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Client (HTTPS/WSS) ──► TLS 1.3 Termination ──► FastAPI Cors + Security Headers │
│                                                        │                        │
│  JWT Authentication (Bearer Token) ◄───────────────────┼──► Bcrypt Password Hash│
│                                                        │                        │
│  AES-256 Encrypted Biometric Embeddings ◄──────────────┴──► Audit Log Storage   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

* **SEC-001 (Authentication Security):** Standard JSON Web Tokens (JWT) signed with HMAC-SHA256 (256-bit secret key). Short-lived access tokens (15 minutes) paired with secure, HTTP-only refresh tokens (7 days).
* **SEC-002 (Authorization & Scoping):** Endpoint access governed by dependency-injected RBAC permissions (`admin_required`, `instructor_required`).
* **SEC-003 (API Security):** Rate-limiting enforced via Redis (maximum 60 requests per minute per IP for standard endpoints; 5 requests per minute for login endpoints).
* **SEC-004 (Database Security):** Database access isolated via non-superuser PostgreSQL credentials; parametrized SQLAlchemy queries preventing SQL injection.
* **SEC-005 (Biometric Data Protection):** Facial embeddings encrypted at application layer via AES-256-GCM using hardware-managed environment keys.

---

## 6. Privacy Requirements (GDPR Article 9 Alignment)

* **PRV-001 (Data Minimization):** The system collects and processes only numerical biometric embeddings (512 float values per template) and minimal demographic identifiers required for academic attendance.
* **PRV-002 (Template Storage & Isolation):** Facial embeddings are stored separately from personal identification tables, linked strictly via encrypted internal foreign keys.
* **PRV-003 (Right to Erasure / Deletion):** Upon student registration withdrawal or graduation, selecting "Delete Profile" immediately cascades hard-deletion of all associated biometric embedding vectors from PostgreSQL tables.
* **PRV-004 (Consent Tracking):** The student registration portal requires explicit checkbox acknowledgment of biometric data collection policies before enabling webcam capture.

---

## 7. Hardware Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **CPU** | Intel Core i5 (8th Gen) / AMD Ryzen 5 (4 cores, 2.5 GHz) | Intel Core i5-12450H / AMD Ryzen 7 (8 cores, 3.3 GHz+) |
| **RAM** | 8 GB DDR4 | 16 GB DDR4 / DDR5 |
| **GPU** | Integrated Intel UHD / AMD Radeon Graphics | NVIDIA GeForce GTX 1650 (4GB VRAM) or RTX 3050+ |
| **Storage** | 20 GB free SSD storage | 50 GB free NVMe M.2 SSD |
| **Webcam** | USB / Integrated Webcam 720p @ 30 FPS | HD Webcam 1080p @ 30/60 FPS |
| **Network** | Fast Ethernet (100 Mbps) / Wi-Fi 5 | Gigabit Ethernet (1 Gbps) / Wi-Fi 6 |

---

## 8. Software Requirements

| Component | Specification / Version | Purpose |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11 (64-bit) or Ubuntu 22.04 LTS | Deployment Host OS |
| **Python Runtime** | Python 3.14.4 (64-bit) | Backend Core & ML Inference |
| **Node.js Runtime** | Node.js 22.x LTS & npm 10.x | Frontend Build & Execution |
| **Database Engine** | PostgreSQL 16+ with `pgvector` 0.5.0+ | Relational Data & Vector Storage |
| **Cache Server** | Redis 7.x | Session Store & Rate Limiting |
| **Web Browser** | Google Chrome 120+, Edge 120+, Firefox 120+ | Client UI & Webcam Stream Capture |
| **ML Frameworks** | ONNX Runtime GPU 1.28, OpenCV 5.0, InsightFace 1.0, MediaPipe 1.0 | Computer Vision Pipeline |
| **Web Stack** | FastAPI 0.141, Next.js 14, React 18, Tailwind CSS 3.4 | Full-Stack Web Application |

---

## 9. External Interface Requirements

### 9.1 User Interface
* Clean, responsive web dashboard with dark/light theme support.
* Live webcam feed container with HTML5 `<video>` and `<canvas>` overlay rendering real-time bounding boxes and liveness status text.

### 9.2 Camera Interface
* Standards-compliant HTML5 `navigator.mediaDevices.getUserMedia()` API interface capturing 1280x720 RGB video stream at 30 FPS.

### 9.3 Backend REST & WebSocket API Interface
* **REST Endpoints:** JSON payloads over HTTP/HTTPS for authentication, profile management, session management, and reporting.
* **WebSocket Endpoint:** Binary/Base64 frame transmission over `wss://` for real-time streaming recognition feedback.

---

## 10. Acceptance Criteria

| ID | Feature Area | Measurable Acceptance Criteria | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-001** | System Startup | Backend API starts cleanly, connects to PostgreSQL and Redis, and responds to `GET /health` with `200 OK` in < 2 seconds. | Automated Integration Test |
| **AC-002** | Student Registration | Successfully captures 3 face angles, converts to 512D vectors, encrypts, and saves to database in < 3 seconds total. | System Test |
| **AC-003** | Biometric Recognition | Recognizes registered student from webcam feed and logs attendance in < 1.0 second from entering camera view. | End-to-End Test |
| **AC-004** | Spoof Defense | Rejects printed photo and smartphone video replay spoof attempts with ACER < 1.5% (zero false attendance logged). | Security / PAD Test |
| **AC-005** | QMF-Score Performance | Demonstrates $\ge 12\%$ lower false rejection rate on $20^\circ$ tilted or blurry frames compared to static threshold baseline. | Benchmark Experiment |
| **AC-006** | Data Privacy | Verifies zero image files written to disk during live attendance kiosk operation; database holds encrypted vectors only. | File System / DB Audit |
| **AC-007** | Report Export | Successfully exports course attendance summary to downloadable CSV, Excel, and PDF files matching database records. | User Acceptance Test |
