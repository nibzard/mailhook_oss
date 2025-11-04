"""Custom middleware for the API."""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mailhookoss.utils.id_generator import generate_id

logger = structlog.get_logger()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to each request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        """Process request and add correlation ID."""
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", generate_id("req"))
        request.state.correlation_id = correlation_id

        # Bind to logger context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        """Process request with logging."""
        start_time = time.time()

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Add timing header
        response.headers["X-Process-Time-Ms"] = str(round(duration_ms, 2))

        return response


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Handle idempotency for POST/PATCH requests."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        """Process request with idempotency checking."""
        # Only apply to POST and PATCH requests
        if request.method not in ("POST", "PATCH"):
            return await call_next(request)

        # Check for idempotency key
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        # Store idempotency key in request state
        request.state.idempotency_key = idempotency_key

        # TODO: Implement actual idempotency logic with Redis
        # 1. Check if request with this key exists in Redis
        # 2. If yes, return cached response
        # 3. If no, process request and cache response

        logger.debug(
            "idempotency_key_received",
            idempotency_key=idempotency_key,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        return response
