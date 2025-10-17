"""Custom exceptions and error handling."""
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class BlueTraceError(Exception):
    """Base exception for BlueTrace application."""

    def __init__(
        self,
        code: str,
        message: str,
        hint: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ): 
        self.code = code
        self.message = message
        self.hint = hint
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(BlueTraceError):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid or missing API key", hint: Optional[str] = None):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            hint=hint,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class RateLimitError(BlueTraceError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", hint: Optional[str] = None):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            hint=hint or "Upgrade your plan for higher limits",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ValidationError(BlueTraceError):
    """Input validation failed."""

    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            hint=hint,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class NotFoundError(BlueTraceError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", hint: Optional[str] = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            hint=hint,
            status_code=status.HTTP_404_NOT_FOUND,
        )


def create_error_response(code: str, message: str, hint: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response."""
    error_body: Dict[str, Any] = {"code": code, "message": message}
    if hint:
        error_body["hint"] = hint
    return {"error": error_body}


async def bluetrace_exception_handler(request: Request, exc: BlueTraceError) -> JSONResponse:
    """Handle BlueTrace exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.code, exc.message, exc.hint),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code="HTTP_ERROR",
            message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        ),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            hint="Please contact support if this persists",
        ),
    )

