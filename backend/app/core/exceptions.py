"""
Custom application exception classes and global exception handlers.
"""

import logging
from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Any = None):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class PermissionDeniedError(AppException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Permission denied", details: Any = None):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class DuplicateResourceError(AppException):
    """Raised when creating a resource that already exists."""

    def __init__(self, message: str = "Resource already exists", details: Any = None):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, details=details)


class BiometricQualityError(AppException):
    """Raised when a facial image fails quality assessment criteria."""

    def __init__(self, message: str = "Facial sample quality insufficient", details: Any = None):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class LivenessSpoofError(AppException):
    """Raised when presentation attack (spoof) is detected."""

    def __init__(self, message: str = "Presentation attack detected", details: Any = None):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global handler for AppException subclasses."""
    logger.warning(
        "AppException caught [%s]: %s (Path: %s)",
        exc.status_code,
        exc.message,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled server exceptions."""
    logger.error("Unhandled Exception on %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected server error occurred. Please contact the administrator.",
        },
    )
