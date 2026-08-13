"""
FastAPI application entry point.

Creates and configures the FastAPI application instance with:
- CORS middleware
- API routers
- WebSocket endpoints
- Lifespan management (startup/shutdown)
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan manager.

    Handles startup and shutdown tasks:
    - Startup: Initialize database, Redis, load ML models
    - Shutdown: Close database connections, release GPU resources
    """
    settings = get_settings()

    # ── Startup ──────────────────────────────────────────────────
    print(f"[*] Starting {settings.app_name} v{settings.app_version}")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")

    # TODO Phase 1: Initialize database connection pool
    # TODO Phase 1: Initialize Redis connection
    # TODO Phase 2: Load ML models into GPU memory

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    print("[*] Shutting down...")

    # TODO Phase 1: Close database connections
    # TODO Phase 1: Close Redis connection
    # TODO Phase 2: Release ML model GPU resources


def create_app() -> FastAPI:
    """
    Application factory.

    Creates and configures the FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A facial recognition-based attendance management system with "
            "liveness detection, face quality assessment, and real-time recognition."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health Check ─────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    # TODO Phase 1: Include API routers
    # app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    # app.include_router(students_router, prefix="/api/v1/students", tags=["Students"])
    # app.include_router(courses_router, prefix="/api/v1/courses", tags=["Courses"])
    # app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["Attendance"])
    # app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
    # app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

    # TODO Phase 2: Include WebSocket endpoint
    # app.include_router(recognition_ws_router)

    return app


# Create the application instance
app = create_app()
