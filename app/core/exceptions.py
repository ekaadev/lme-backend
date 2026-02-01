"""
Custom exceptions untuk aplikasi.
Setiap exception memiliki status code dan detail yang konsisten.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """
    Base exception untuk semua custom exceptions di aplikasi.
    Menyediakan struktur yang konsisten untuk error handling.
    """

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.detail)


class NotFoundError(AppException):
    """Exception untuk resource yang tidak ditemukan (404)."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(AppException):
    """Exception untuk request tanpa autentikasi yang valid (401)."""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppException):
    """Exception untuk akses yang tidak diizinkan (403)."""

    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=403, detail=detail)


class ValidationError(AppException):
    """Exception untuk data yang tidak valid (422)."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail)


class BadRequestError(AppException):
    """Exception untuk request yang tidak valid (400)."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class ConflictError(AppException):
    """Exception untuk konflik data, misalnya duplicate entry (409)."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)


class ExternalAPIError(AppException):
    """Exception untuk error dari external API seperti Genius API."""

    def __init__(self, detail: str = "External API error", service: str = "unknown"):
        self.service = service
        super().__init__(status_code=502, detail=f"{service}: {detail}")


class DatabaseError(AppException):
    """Exception untuk error database."""

    def __init__(self, detail: str = "Database error"):
        super().__init__(status_code=500, detail=detail)
