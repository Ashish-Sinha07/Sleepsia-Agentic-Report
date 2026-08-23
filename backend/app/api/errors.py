from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any


class SleepsiaException(Exception):
    """Base exception for Sleepsia API."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(SleepsiaException):
    """Validation error (400)."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_400_BAD_REQUEST)


class ResourceNotFound(SleepsiaException):
    """Resource not found (404)."""

    def __init__(self, resource: str):
        super().__init__(
            f"{resource} not found",
            "NOT_FOUND",
            status.HTTP_404_NOT_FOUND,
        )


class DatabaseError(SleepsiaException):
    """Database error (500)."""

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)


def error_response(
    error: str,
    code: str = "INTERNAL_ERROR",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create consistent error response."""
    return {
        "success": False,
        "error": error,
        "error_code": code,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }
