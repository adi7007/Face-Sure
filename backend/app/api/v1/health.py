"""
Health check and system diagnostic API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.core.database import get_db

router = APIRouter(tags=["Health & System"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint returning system status and version."""
    settings = get_settings()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """Database connectivity health check verifying PostgreSQL response."""
    try:
        result = await db.execute(text("SELECT 1"))
        val = result.scalar()
        return {
            "status": "connected",
            "database": "postgresql",
            "query_test": val == 1,
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "postgresql",
            "details": str(e),
        }
