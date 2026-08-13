# Unified Modeling Language (UML) Diagrams

**Document Identifier:** `docs/UML/uml_diagrams.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Use Case Diagram

```mermaid
graph TD
    subgraph Users
        Admin["Administrator"]
        Teacher["Instructor / Teacher"]
        Student["Student"]
    end

    subgraph "Facial Recognition Attendance System"
        UC1["Login & Authenticate"]
        UC2["Manage Users & Roles"]
        UC3["Manage Student Profiles"]
        UC4["Enroll Facial Biometrics"]
        UC5["Manage Courses & Rosters"]
        UC6["Create & Manage Attendance Sessions"]
        UC7["Run Kiosk Attendance Recognition"]
        UC8["Manual Attendance Override"]
        UC9["View Attendance Reports & Export"]
        UC10["View Personal Attendance History"]
        UC11["View System Security Audit Logs"]
    end

    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC5
    Admin --> UC9
    Admin --> UC11

    Teacher --> UC1
    Teacher --> UC3
    Teacher --> UC4
    Teacher --> UC5
    Teacher --> UC6
    Teacher --> UC7
    Teacher --> UC8
    Teacher --> UC9

    Student --> UC1
    Student --> UC4
    Student --> UC10
```

---

## 2. Class Diagram (ORM Models & Business Services)

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String username
        +String hashedPassword
        +UserRole role
        +Boolean isActive
        +authenticate()
    }

    class Student {
        +UUID id
        +String studentId
        +String fullName
        +String email
        +String department
        +UUID userId
    }

    class Course {
        +UUID id
        +String courseCode
        +String courseName
        +UUID instructorId
    }

    class FaceEmbedding {
        +UUID id
        +UUID studentId
        +Vector512 embedding
        +String sampleAngle
        +Float qualityScore
    }

    class AttendanceSession {
        +UUID id
        +UUID courseId
        +UUID createdBy
        +SessionStatus status
        +DateTime startTime
        +DateTime endTime
        +openSession()
        +closeSession()
    }

    class AttendanceRecord {
        +UUID id
        +UUID sessionId
        +UUID studentId
        +AttendanceStatus status
        +AttendanceMethod method
        +Float confidenceScore
        +DateTime markedAt
    }

    class PipelineOrchestrator {
        +processFrame(Frame) FrameResult
    }

    class QMFScoreEngine {
        +computeConfidence(S, Q, L) Float
        +computeDynamicThreshold(Q) Float
    }

    User "1" -- "0..1" Student : links
    User "1" -- "*" Course : teaches
    Student "1" -- "*" FaceEmbedding : owns
    Course "1" -- "*" AttendanceSession : contains
    AttendanceSession "1" -- "*" AttendanceRecord : records
    Student "1" -- "*" AttendanceRecord : targets
    PipelineOrchestrator --> QMFScoreEngine : evaluates
```

---

## 3. Sequence Diagram (Real-Time Video Recognition & Attendance)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant KioskUI as Web Kiosk (Next.js)
    participant WSRouter as WebSocket Router
    participant Orchestrator as Pipeline Orchestrator
    participant VisionEngine as RetinaFace + MiniFASNet + ArcFace
    participant QMFEngine as QMF-Score Engine
    participant DB as PostgreSQL (pgvector)

    Student->>KioskUI: Position face in front of webcam
    KioskUI->>WSRouter: Send Video Frame (WSS binary/base64)
    WSRouter->>Orchestrator: Process Frame(raw_frame)
    Orchestrator->>VisionEngine: Detect, Align, Quality & Liveness
    VisionEngine-->>Orchestrator: BBox, LandMarks, Q_sample, L_live, Embed_vector
    Orchestrator->>DB: Vector Cosine Search (embedding <=> query)
    DB-->>Orchestrator: Candidate Student ID, S_match
    Orchestrator->>QMFEngine: Calculate C(x) & Dynamic Tau(Q)
    QMFEngine-->>Orchestrator: Result: AUTHENTICATED
    Orchestrator->>DB: Insert Attendance Record & Event Log
    Orchestrator-->>WSRouter: FrameResult (AUTHENTICATED, Student Name, BBox)
    WSRouter-->>KioskUI: Emit Recognition Event JSON
    KioskUI-->>Student: Display Green Bounding Box & Audio Chime
```

---

## 4. Activity Diagram (Student Biometric Registration Flow)

```mermaid
stateDiagram-v2
    [*] --> StartRegistration
    StartRegistration --> CaptureSample1: Frontal Pose
    CaptureSample1 --> AssessQuality1: Evaluate Pose/Sharpness
    
    state QualityCheck1 <<choice>>
    AssessQuality1 --> QualityCheck1
    QualityCheck1 --> CaptureSample1: Quality < 0.50 (Prompt Adjust)
    QualityCheck1 --> CaptureSample2: Quality >= 0.50 (Pass)
    
    CaptureSample2 --> CaptureSample3: Left & Right Yaw Angles
    CaptureSample3 --> ExtractArcFaceEmbeddings: Generate 512D Vectors
    ExtractArcFaceEmbeddings --> EncryptVectors: Apply AES-256 Encryption
    EncryptVectors --> SaveToDatabase: Save to face_embeddings Table
    SaveToDatabase --> PurgeRAMImages: Destroy Raw Images in RAM
    PurgeRAMImages --> [*]: Enrollment Complete
```

---

## 5. Component Diagram (System Module Architecture)

```mermaid
componentDiagram
    package "Client Tier" {
        [Webcam Capture Module]
        [Kiosk Overlay Component]
        [Admin Dashboard UI]
    }

    package "API Server Tier (FastAPI)" {
        [REST Router Controllers]
        [WebSocket Stream Handler]
        [JWT Security & Auth Middleware]
        [Business Services Layer]
    }

    package "AI Computer Vision Core" {
        [RetinaFace Detector]
        [Quality Assessor Module]
        [MiniFASNet Liveness Module]
        [ArcFace Vector Embedder]
        [QMF-Score Decision Engine]
    }

    package "Data Layer" {
        database "PostgreSQL 16\n(pgvector)" as DB
        database "Redis Cache" as Cache
    }

    [Webcam Capture Module] --> [WebSocket Stream Handler]
    [Admin Dashboard UI] --> [REST Router Controllers]
    [WebSocket Stream Handler] --> [AI Computer Vision Core]
    [AI Computer Vision Core] --> [QMF-Score Decision Engine]
    [QMF-Score Decision Engine] --> DB
    [REST Router Controllers] --> [Business Services Layer]
    [Business Services Layer] --> DB
    [JWT Security & Auth Middleware] --> Cache
```

---

## 6. Deployment Diagram

```mermaid
graph TD
    subgraph Client Hardware
        WebCam["HD Webcam (1080p)"]
        Browser["Web Browser (Chrome/Edge/Firefox)"]
        WebCam --> Browser
    end

    subgraph Application Server (Host / Docker Container)
        Uvicorn["FastAPI ASGI Server (Uvicorn)"]
        ONNX["ONNX Runtime GPU / CPU"]
        Uvicorn --> ONNX
    end

    subgraph Database Infrastructure
        Postgres["PostgreSQL 16 + pgvector"]
        Redis["Redis Cache Server"]
    end

    Browser -- HTTPS / REST --> Uvicorn
    Browser -- WSS / WebSockets --> Uvicorn
    Uvicorn -- Async SQLAlchemy --> Postgres
    Uvicorn -- aioredis --> Redis
```
