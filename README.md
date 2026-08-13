# Facial Recognition Attendance System

A comprehensive facial recognition-based attendance management system with liveness detection, face quality assessment, and real-time recognition capabilities.

## 🏗️ Architecture

- **Frontend:** Next.js 15 (React 19) + shadcn/ui + Tailwind CSS
- **Backend:** FastAPI (Python) + SQLAlchemy 2.0
- **Database:** PostgreSQL 16 with pgvector extension
- **Cache:** Redis
- **CV/ML:** InsightFace (ArcFace) + MediaPipe + MiniFASNet via ONNX Runtime GPU

## 📁 Project Structure

```
├── backend/          # FastAPI application
│   ├── app/          # Application source code
│   │   ├── api/      # REST API endpoints
│   │   ├── cv/       # Computer vision pipeline
│   │   ├── models/   # Database ORM models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── core/     # Cross-cutting concerns
│   └── tests/        # Backend tests
├── frontend/         # Next.js application
├── data/             # Runtime data (models, faces, exports)
├── research/         # Experiments, notebooks, paper
├── docs/             # Documentation (SRS, architecture, etc.)
└── scripts/          # Utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ with virtual environment
- Node.js 22 LTS
- PostgreSQL 16 with pgvector
- Redis
- NVIDIA GPU with CUDA support (recommended)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

- [Project Plan](docs/project_plan.md)
- [Architecture](docs/architecture.md)
- [Development Roadmap](docs/development_roadmap.md)

## 📄 License

This project is developed as an academic project. All rights reserved.
