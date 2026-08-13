# Security & Privacy Architecture Specification

**Document Identifier:** `docs/Architecture/security_architecture.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Security Architecture Overview

The Facial Recognition Attendance System implements a defense-in-depth security model protecting user authentication, system APIs, database storage, and sensitive biometric data. The architecture complies with ISO/IEC 27001 principles and GDPR Article 9 regulations governing biometric data handling.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              DEFENSE-IN-DEPTH SECURITY MODEL                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Transport Security (TLS 1.3 Encryption for HTTP & WebSockets)                 │
│ Layer 2: API Protection & Rate Limiting (Redis Rate Limiter, CORS, Helmet Headers)     │
│ Layer 3: Authentication & AuthZ (JWT Access/Refresh Tokens, Bcrypt, RBAC Middleware)   │
│ Layer 4: Application Logic (Input Sanitization, Pydantic Schema Validation)           │
│ Layer 5: Data Storage Protection (AES-256-GCM Vector Encryption, Parameterized SQL)     │
│ Layer 6: Audit & Monitoring (Immutable Security Event Audit Logging)                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Authorization Framework

### 2.1 JSON Web Token (JWT) Authentication
* **Algorithm:** HMAC-SHA256 (`HS256`) utilizing a 256-bit environment secret key (`SECRET_KEY`).
* **Access Tokens:** Short-lived (15 minutes expiry) carrying claims: `sub` (User ID), `role` (Admin/Instructor/Student), `email`, `exp`, `iat`.
* **Refresh Tokens:** Long-lived (7 days expiry) stored in HttpOnly, Secure, SameSite=Strict cookies to mitigate Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) vulnerabilities.
* **Token Revocation:** Logout and session invalidation blacklists active refresh tokens in Redis until natural expiration.

### 2.2 Password Security & Hashing
* **Algorithm:** `bcrypt` password hashing with a cost factor of 12 rounds.
* **Policy Enforcement:** Minimum 8 characters, requiring at least one uppercase letter, one lowercase letter, one numeric digit, and one special character.
* **Storage:** Plaintext passwords are never logged, cached, or persisted.

### 2.3 Role-Based Access Control (RBAC)
FastAPI dependency injection enforces role restrictions at the route handler level:
* `ADMIN`: Full access to user management, course creation, system settings, database management, and complete security audit logs.
* `INSTRUCTOR`: Access to assigned course rosters, opening/closing attendance sessions, live kiosk monitoring, manual attendance overrides, and report exports.
* `STUDENT`: Read-only access to personal attendance history, enrolled course schedules, and registration profile settings.

---

## 3. Biometric Protection & Data Privacy Architecture (GDPR Article 9)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           BIOMETRIC PRIVACY & LIFECYCLE FLOW                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Webcam Capture] ──► (In-Memory RAM Frame) ──► [ArcFace Embedder] ──► 512D Float Vector │
│                            │                                                 │         │
│                            ▼                                                 ▼         │
│                    (RAM Immediately)                                 [AES-256 Encrypter]│
│                       (Destroyed)                                            │         │
│                                                                              ▼         │
│                                                                      [PostgreSQL DB]   │
│                                                                      (vector(512))     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Zero Image Persistence Principle
* Live video streams from the webcam kiosk exist **purely in volatile server RAM** during the ~40ms computer vision frame execution cycle.
* Raw facial video frames, cropped JPEG patches, and intermediate images are **never saved to server disk, temporary directories, or database blobs** during live attendance kiosk operation.
* Once feature extraction completes, image array memory is immediately garbage-collected.

### 3.2 Biometric Vector Encryption at Rest
* 512-dimensional floating-point embeddings are converted to binary byte representations and encrypted using **AES-256-GCM (Galois/Counter Mode)** symmetric encryption before storage in PostgreSQL.
* Decryption keys are loaded exclusively from secure environment variables (`BIOMETRIC_ENCRYPTION_KEY`) injected at runtime and never committed to version control.

### 3.3 Template Protection & Irreversibility
* The 512-dimensional ArcFace vector is a non-invertible, non-linear deep representation. Reconstructing the original human facial image from an embedding vector is computationally infeasible.
* Vector representations cannot be used across external identity domains without knowledge of our specific model alignment and embedding weights.

### 3.4 Data Minimization & Deletion Rights
* **Data Minimization:** Only 512 float values per biometric template are retained alongside the student database reference ID.
* **Right to Erasure (GDPR Art. 17):** Deleting a student profile triggers a hard-cascade SQL delete operation that permanently purges all associated biometric vector rows from the `face_embeddings` table.

---

## 4. API & Network Protection Architecture

### 4.1 Rate Limiting (Redis Token Bucket)
To protect against brute-force password guessing and Denial of Service (DoS) attacks, Redis rate-limiting middleware throttles requests by IP address:
* Authentication endpoints (`/api/v1/auth/login`): Maximum 5 requests per minute per IP.
* General REST endpoints (`/api/v1/*`): Maximum 60 requests per minute per IP.
* WebSocket connections (`/ws/recognize`): Maximum 1 concurrent connection per client IP.

### 4.2 Cross-Origin Resource Sharing (CORS)
Strict CORS configuration in FastAPI restricts API access to explicitly whitelisted origins (`ALLOWED_ORIGINS` in `.env`), preventing unauthorized third-party web domains from invoking endpoints.

### 4.3 Input Validation & Injection Prevention
* All incoming JSON payloads are validated against strict Pydantic schemas, stripping unexpected fields and enforcing type safety.
* Database queries utilize SQLAlchemy 2.0 ORM parameterization, completely eliminating SQL injection vectors.

---

## 5. Security Event Audit Logging

System audit logging records security-critical events in the immutable `audit_logs` table:

| Field | Data Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (PK) | Unique log entry identifier |
| `timestamp` | TIMESTAMPTZ | UTC timestamp of the security event |
| `user_id` | UUID (FK) | ID of the user performing the action (or NULL for unauthenticated attempts) |
| `event_type` | VARCHAR(50) | Event type (e.g., `USER_LOGIN`, `LOGIN_FAILED`, `BIOMETRIC_ENROLLED`, `ATTENDANCE_OVERRIDE`, `DATA_EXPORT`) |
| `ip_address` | VARCHAR(45) | Client IPv4 or IPv6 address |
| `user_agent` | TEXT | HTTP User-Agent header string |
| `details` | JSONB | Structured JSON metadata (e.g., target student ID, override rationale, export format) |
