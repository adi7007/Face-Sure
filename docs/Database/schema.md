# Relational Database Schema Specification

**Document Identifier:** `docs/Database/schema.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Entity-Relationship Overview

The database is built on PostgreSQL 16 using the `pgvector` extension for storing and indexing 512-dimensional facial feature embeddings. The schema consists of 10 justified tables designed to manage users, students, courses, attendance sessions, attendance records, biometric vectors, research recognition logs, security audit logs, and system configuration.

```
┌─────────────┐       1:N       ┌──────────────┐       1:N       ┌─────────────────┐
│    users    ├────────────────►│   students   ├────────────────►│ face_embeddings │
└──────┬──────┘                 └──────┬───────┘                 └─────────────────┘
       │ 1:N                           │ 1:N
       ▼                               ▼
┌─────────────┐       1:N       ┌──────────────┐       N:1       ┌─────────────────┐
│   courses   ├────────────────►│ enrollments  │◄────────────────┤   students      │
└──────┬──────┘                 └──────────────┘                 └─────────────────┘
       │ 1:N
       ▼
┌─────────────────────┐ 1:N     ┌────────────────────┐
│ attendance_sessions ├────────►│ attendance_records │
└─────────────────────┘         └─────────┬──────────┘
                                          │ 1:N
                                          ▼
                                ┌────────────────────┐
                                │ recognition_events │
                                └────────────────────┘
```

---

## 2. Table Specifications

### 2.1 `users` Table
Stores authentication credentials, contact information, and role permissions for system users.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'INSTRUCTOR', 'STUDENT')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
```

### 2.2 `students` Table
Stores academic profile information for enrolled students, optionally linked to a user account.

```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(50) UNIQUE NOT NULL, -- Institutional Student ID/Roll Number
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_department ON students(department);
```

### 2.3 `courses` Table
Stores academic course definitions managed by instructors.

```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., "CS-401"
    course_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    instructor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_courses_code ON courses(course_code);
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
```

### 2.4 `enrollments` Table
Junction table mapping students to enrolled courses (Many-to-Many).

```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id)
);

CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
```

### 2.5 `face_embeddings` Table
Stores 512-dimensional ArcFace biometric feature vectors for registered students.

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE face_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    embedding vector(512) NOT NULL,
    sample_angle VARCHAR(20) NOT NULL CHECK (sample_angle IN ('FRONTAL', 'LEFT_YAW', 'RIGHT_YAW', 'UP_PITCH')),
    quality_score FLOAT NOT NULL CHECK (quality_score BETWEEN 0.0 AND 1.0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embeddings_student ON face_embeddings(student_id);

-- HNSW Index for fast vector similarity search using Cosine Distance
CREATE INDEX idx_embeddings_hnsw ON face_embeddings 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);
```

### 2.6 `attendance_sessions` Table
Tracks active and historical attendance recording sessions created by instructors.

```sql
CREATE TABLE attendance_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(150) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED')),
    start_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    late_threshold_minutes INT NOT NULL DEFAULT 15,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_course ON attendance_sessions(course_id);
CREATE INDEX idx_sessions_status ON attendance_sessions(status);
```

### 2.7 `attendance_records` Table
Stores student attendance entries logged during sessions.

```sql
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PRESENT', 'LATE', 'ABSENT', 'EXCUSED')),
    method VARCHAR(30) NOT NULL CHECK (method IN ('FACE_RECOGNITION', 'MANUAL_OVERRIDE')),
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    marked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    marked_by UUID REFERENCES users(id) ON DELETE SET NULL, -- Null if auto-marked by AI
    remarks TEXT,
    CONSTRAINT uq_session_student UNIQUE (session_id, student_id)
);

CREATE INDEX idx_attendance_session ON attendance_records(session_id);
CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_status ON attendance_records(status);
```

### 2.8 `recognition_events` Table
Research audit table storing frame-by-frame recognition parameters ($S_{match}, Q_{sample}, L_{live}, C(x), \tau(Q)$) for paper benchmarks.

```sql
CREATE TABLE recognition_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES attendance_sessions(id) ON DELETE SET NULL,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    match_similarity FLOAT NOT NULL,
    quality_score FLOAT NOT NULL,
    liveness_score FLOAT NOT NULL,
    composite_confidence FLOAT NOT NULL,
    dynamic_threshold FLOAT NOT NULL,
    decision VARCHAR(30) NOT NULL CHECK (decision IN ('AUTHENTICATED', 'REJECTED_QUALITY', 'REJECTED_LIVENESS', 'REJECTED_MATCH')),
    latency_ms FLOAT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_session ON recognition_events(session_id);
CREATE INDEX idx_events_decision ON recognition_events(decision);
```

### 2.9 `audit_logs` Table
System security audit log recording administrative, authentication, and manual override events.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    details JSONB
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
```

### 2.10 `system_configurations` Table
Stores runtime configuration parameters for the QMF-Score engine and application thresholds.

```sql
CREATE TABLE system_configurations (
    key VARCHAR(100) PRIMARY KEY,
    value VARCHAR(255) NOT NULL,
    description TEXT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
