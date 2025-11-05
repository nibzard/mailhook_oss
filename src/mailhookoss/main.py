"""Main FastAPI application."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import make_asgi_app

from mailhookoss.api.errors import register_error_handlers
from mailhookoss.api.middleware import (
    CorrelationIdMiddleware,
    IdempotencyMiddleware,
    LoggingMiddleware,
)
from mailhookoss.api.v1.router import api_router
from mailhookoss.config import settings
from mailhookoss.infrastructure.database.session import (
    close_database,
    init_database,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if not settings.debug else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelName(settings.log_level)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Initialize database
    await init_database()
    logger.info("database_initialized")

    # TODO: Initialize other services (Redis, S3, etc.)

    yield

    # Shutdown
    logger.info("shutting_down_application")
    await close_database()
    logger.info("application_shutdown_complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Open-source multi-tenant email management API service",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(IdempotencyMiddleware)

    # Register error handlers
    register_error_handlers(app)

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    # Prometheus metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    logger.info(
        "application_created",
        api_prefix=settings.api_prefix,
        cors_origins=settings.cors_origins,
    )

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mailhookoss.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
