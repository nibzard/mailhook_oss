"""API error handlers."""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from mailhookoss.domain.common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainException,
    EntityNotFoundError,
    ValidationError,
)
from mailhookoss.utils.id_generator import generate_id

logger = structlog.get_logger()


class ErrorResponse:
    """Standard error response format."""

    def __init__(self, code: int, detail: str, correlation_id: str) -> None:
        self.error = {
            "code": code,
            "detail": detail,
            "correlation_id": correlation_id,
        }


def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request state."""
    return getattr(request.state, "correlation_id", generate_id("req"))


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
) -> ORJSONResponse:
    """Handle domain exceptions."""
    correlation_id = get_correlation_id(request)

    logger.warning(
        "domain_exception",
        exception=exc.__class__.__name__,
        detail=str(exc),
        correlation_id=correlation_id,
    )

    # Map domain exceptions to HTTP status codes
    status_code = status.HTTP_400_BAD_REQUEST

    if isinstance(exc, EntityNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN

    error = ErrorResponse(
        code=status_code,
        detail=str(exc),
        correlation_id=correlation_id,
    )

    return ORJSONResponse(
        status_code=status_code,
        content=error.error,
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> ORJSONResponse:
    """Handle unexpected exceptions."""
    correlation_id = get_correlation_id(request)

    logger.error(
        "unexpected_exception",
        exception=exc.__class__.__name__,
        detail=str(exc),
        correlation_id=correlation_id,
        exc_info=exc,
    )

    error = ErrorResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
        correlation_id=correlation_id,
    )

    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.error,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers with the FastAPI app."""
    app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]
