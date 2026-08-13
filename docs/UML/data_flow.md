# Data Flow Specifications & DFD Specifications

**Document Identifier:** `docs/UML/data_flow.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Context Diagram (DFD Level 0)

The Data Flow Diagram Level 0 defines the global data boundary between external entities (Admin, Instructor, Student, Webcam Sensor) and the Facial Recognition Attendance System process.

```
                  ┌────────────────────────┐
                  │      Administrator     │
                  └───────────┬────────────┘
                              │ Admin Commands / User Config
                              ▼
┌──────────────┐  Student Reg │ ┌──────────────────────────────────────┐  Attendance Reports  ┌────────────┐
│   Student    ├──────────────┼►│  0.0                                 ├─────────────────────►│ Instructor │
└──────────────┘  Credentials │ │  Facial Recognition Attendance System│  Manual Overrides   └────────────┘
                              │ └──────────────────▲───────────────────┘
┌──────────────┐  Video Stream│                    │ Video Frames
│ Webcam Kiosk ├──────────────┘                    │
└──────────────┘                                   └─────────────────────────────────
```

---

## 2. Detailed System Data Flows

### 2.1 Student Biometric Registration Flow
```
[Student/Instructor] ──► (Webcam Capture) ──► 1. Quality Filter ($Q \ge 0.50$)
                                                      │
                                                      ▼
                                           2. ArcFace Embedder (512D Vector)
                                                      │
                                                      ▼
                                           3. AES-256 Encrypter
                                                      │
                                                      ▼
                                           4. PostgreSQL (`face_embeddings`)
                                                      │
                                                      ▼
                                           5. RAM Image Purge (Zero Disk Save)
```

1. Instructor triggers student registration mode via web frontend (`/students/enroll`).
2. Webcam captures 3 to 5 multi-angle facial sample frames.
3. Frames are passed to `QualityAssessor`. If sample quality $Q_{sample} < 0.50$ (e.g., severe blur), the client is prompted to adjust position.
4. Approved patches are processed by ArcFace ResNet-50 to extract 512D feature embeddings.
5. Embeddings are encrypted using AES-256-GCM and stored in the `face_embeddings` table linked to the `student_id`.
6. Raw image arrays in server RAM are immediately purged.

### 2.2 Streaming Recognition & QMF-Score Engine Flow
```
[Webcam Kiosk] ──► (WSS WebSocket Frame) ──► 1. RetinaFace (Detect & Align 112x112)
                                                    │
                                                    ├──► 2. QualityAssessor ($Q_{sample}$)
                                                    ├──► 3. MiniFASNetV2 ($L_{live}$)
                                                    └──► 4. ArcFace ($e \in \mathbb{R}^{512}$)
                                                                │
                                                                ▼
                                                     5. `pgvector` HNSW Search ($S_{match}$)
                                                                │
                                                                ▼
                                                     6. QMF-Score Engine ($C(x) \ge \tau(Q)$)
                                                                │
                                                                ▼
                                                     7. Emit WS Event & Bounding Box
```

1. Kiosk client captures HTML5 video frame ($1280 \times 720$) every $100\text{ms}$ and emits over WebSocket `/ws/recognize`.
2. Backend pipeline detects face bounding box and 5 landmarks using RetinaFace.
3. Affine transform crops aligned $112 \times 112$ patch.
4. Parallel/sequential evaluation computes:
   - $Q_{sample} = 0.40 Q_{pose} + 0.35 Q_{sharp} + 0.25 Q_{illum}$
   - $L_{live} \in [0, 1]$ via MiniFASNetV2
   - $e \in \mathbb{R}^{512}$ via ArcFace
5. Query embedding $e$ searches PostgreSQL `face_embeddings` using HNSW index cosine distance to yield nearest `student_id` and raw similarity $S_{match}$.
6. `QMFScoreEngine` computes composite confidence $C(x) = 0.60 S_{match} + 0.25 Q_{sample} + 0.15 L_{live}$ and dynamic threshold $\tau(Q) = \tau_{base} - \lambda(Q_{sample} - 0.50)$.
7. If $C(x) \ge \tau(Q)$ and $L_{live} \ge 0.50$, emit `AUTHENTICATED` event JSON over WebSocket to update kiosk canvas.

### 2.3 Automated Attendance Marking Flow
```
[QMF-Score: AUTHENTICATED] ──► 1. Check Cooldown (5 min in Redis)
                                          │
                                          ├─► (Active Cooldown) ──► Ignore Duplicate
                                          │
                                          └─► (Not Cooling Down) ──► 2. Insert DB Record (`PRESENT`/`LATE`)
                                                                     3. Log Research Audit Event
                                                                     4. Emit Visual/Audio Feedback
```

1. QMF-Score Engine resolves authenticated `student_id` and active `session_id`.
2. System queries Redis key `cooldown:{session_id}:{student_id}`. If key exists, attempt is ignored as a duplicate within 5 minutes.
3. If not cooling down, system checks session `start_time` vs current timestamp. If current time $> \text{start\_time} + \text{late\_threshold}$, status set to `LATE`; otherwise `PRESENT`.
4. Attendance record inserted into `attendance_records` table; research log inserted into `recognition_events` table.
5. Redis cooldown key set with 300-second TTL.
6. WebSocket event notifies kiosk UI to trigger green visual indicator and audio chime.

### 2.4 User Authentication & JWT Flow
```
[User Client] ──► (POST /v1/auth/login) ──► 1. Verify Email & Bcrypt Password Hash
                                                    │
                                                    ▼
                                           2. Generate JWT Access (15m) & Refresh (7d)
                                                    │
                                                    ▼
                                           3. Set HttpOnly Secure Cookie & Return JSON
```

1. Client posts credentials (`email`, `password`) to `/api/v1/auth/login`.
2. System queries `users` table, verifies `is_active == True`, and checks bcrypt password hash.
3. Upon validation, generates 15-minute JWT access token and 7-day refresh token.
4. Refresh token set in `HttpOnly`, `Secure`, `SameSite=Strict` HTTP cookie; access token returned in JSON response payload.
5. Subsequent API requests pass access token in `Authorization: Bearer <token>` HTTP header.

### 2.5 Reporting & Export Data Flow
```
[Instructor/Admin] ──► (GET /v1/reports/export?course_id=X&format=xlsx) 
                                 │
                                 ▼
                     1. Authorize Role & Course Ownership
                                 │
                                 ▼
                     2. Execute Aggregated SQL Join Query
                        (students JOIN attendance_records JOIN sessions)
                                 │
                                 ▼
                     3. Stream Export File (OpenPyXL / ReportLab PDF)
                                 │
                                 ▼
                     4. Write Audit Log Event (`DATA_EXPORT`)
```

1. Instructor selects course, date range, and export format (CSV/Excel/PDF) on frontend dashboard.
2. Request sent to `/api/v1/reports/export`.
3. Backend validates instructor authorization for target course.
4. Executes optimized SQL query aggregating student total sessions, present count, late count, absent count, and attendance percentage.
5. Formats output using Pandas / OpenPyXL (Excel) or ReportLab (PDF) and streams file response to client.
6. Security audit event logged in `audit_logs`.
