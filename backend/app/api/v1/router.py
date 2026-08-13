"""
API v1 main router aggregator.
"""

from fastapi import APIRouter
from app.api.v1 import health, auth, students, courses, sessions, attendance, reports

api_v1_router = APIRouter(prefix="/v1")

# Include sub-routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(students.router)
api_v1_router.include_router(courses.router)
api_v1_router.include_router(sessions.router)
api_v1_router.include_router(attendance.router)
api_v1_router.include_router(reports.router)
