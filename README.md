# Facial Recognition Attendance System

An enterprise-grade, privacy-preserving automated attendance management platform incorporating a novel **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** decision engine.

---

## 🌟 Core Features

- **Multi-Stage AI Computer Vision Pipeline:** RetinaFace face detection & alignment (5 landmarks), composite Face Quality Assessment (FQA), MiniFASNetV2 passive presentation attack liveness detection (FAS), and ArcFace 512D hyperspherical vector embedding.
- **QMF-Score Decision Engine:** Dynamic quality-adaptive thresholding ($\tau(Q)$) and multi-factor confidence scoring ($C(x) = \alpha S_{match} + \beta Q_{sample} + \gamma L_{live}$) minimizing false rejections under non-ideal streaming video conditions.
- **High-Performance Vector Storage:** PostgreSQL 16 database utilizing the `pgvector` HNSW index for sub-10ms $L_2$-normalized vector similarity search.
- **GDPR Article 9 Privacy-by-Design:** Zero raw facial image retention on backend servers; AES-256-GCM encrypted vector payload storage.
- **Modern Full-Stack Architecture:** FastAPI asynchronous REST API & WebSockets backend paired with a React 18, TypeScript, and Vite single-page web application.

---

## 📁 Repository Structure

```
.
├── backend/                  # FastAPI Backend Service
│   ├── app/
│   │   ├── api/v1/          # REST Endpoint Routers (auth, students, courses, sessions, attendance, reports)
│   │   ├── core/            # Config, Security (JWT/bcrypt), Database, Logging, Exceptions
│   │   ├── cv/              # CV Pipeline & QMF-Score Engine Modules
│   │   ├── models/          # SQLAlchemy 2.0 ORM Models (User, Student, Course, Session, Attendance, Vector)
│   │   ├── schemas/         # Pydantic Validation Schemas
│   │   ├── services/        # Business Logic Services
│   │   └── utils/           # Helper Utilities
│   ├── tests/               # Pytest Test Suite
│   ├── alembic/             # Database Migration Scripts
│   ├── pyproject.toml       # Backend Python Dependencies
│   └── pytest.ini           # Pytest Configuration
├── frontend/                 # React + TypeScript + Vite Web Application
│   ├── src/
│   │   ├── components/      # Sidebar, Navbar, Layout, StatCard
│   │   ├── pages/           # Dashboard, Live Kiosk, Students, Courses, Sessions, Reports
│   │   ├── App.tsx          # React Router Setup
│   │   └── index.css        # Glassmorphic Design System
│   ├── package.json
│   └── vite.config.ts
├── data/                    # Local Models, Face Templates & Export Scratch Space
├── docs/                    # Project Documentation
│   ├── Architecture/        # System, AI Pipeline & Security Specifications
│   ├── Database/            # Relational Schema & Index Specifications
│   ├── Research_Paper/      # Literature Review, Research Gap, Methodology, Bibliography
│   ├── SRS/                 # IEEE 830 Software Requirements Specification
│   └── UML/                 # UML Diagrams (Use Case, Class, Sequence, Component) & DFDs
├── scripts/                 # Setup Verification & Database Initialization Scripts
└── docker-compose.yml       # PostgreSQL (pgvector) & Redis Infrastructure Setup
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** 3.14+ (64-bit)
- **Node.js:** 22.x LTS & npm 10+
- **Database:** PostgreSQL 16 with `pgvector` extension (or Docker Desktop)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .

# Run Pytest Test Suite
pytest

# Start FastAPI Dev Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
API Documentation available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build   # Verify TypeScript build
npm run dev     # Start Vite Dev Server (port 5173)
```
Web Kiosk App available at: `http://127.0.0.1:5173`

---

## 🧪 Verification & Health Check

- **API Root Health:** `GET http://127.0.0.1:8000/health`
- **API v1 Health:** `GET http://127.0.0.1:8000/api/v1/health`
- **Database Diagnostics:** `GET http://127.0.0.1:8000/api/v1/health/db`

---

## 📜 License & Citation

Academic Research Component of Capstone Project. See [`docs/Research_Paper/references.md`](docs/Research_Paper/references.md) for full bibliography.
