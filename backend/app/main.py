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
from app.core.logging import setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.api.v1.router import api_v1_router


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
    setup_logging(debug=settings.debug)
    print(f"[*] Starting {settings.app_name} v{settings.app_version}")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")

    from app.core.database import init_engine

    init_engine()

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    from app.core.database import close_engine
    await close_engine()
    print("[*] Shutting down...")


def create_app() -> FastAPI:
    """
    Application factory.

    Creates and configures the FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise Facial Recognition Attendance System with Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────
    # NOTE: In FastAPI, middleware is LIFO — the LAST added wraps outermost.
    # CORS must wrap outermost to handle preflight OPTIONS before anything else.
    if settings.debug:
        # Dev mode: allow all origins for frictionless development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ── Exception Handlers ───────────────────────────────────────
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── API Routers ──────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api")

    # ── Health Check ─────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }


    # TODO Phase 2: Include WebSocket endpoint
    # app.include_router(recognition_ws_router)

    return app


# Create the application instance
app = create_app()
