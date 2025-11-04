"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="MailhookOSS", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    testing: bool = Field(default=False, description="Testing mode")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API path prefix")
    cors_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins",
    )

    # Database
    database_url: PostgresDsn = Field(
        description="PostgreSQL database URL",
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(
        default=10,
        description="Max overflow for database pool",
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL statements (debug)",
    )

    # Redis
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis URL",
    )
    redis_max_connections: int = Field(
        default=50,
        description="Max Redis connections",
    )

    # S3 Storage
    s3_endpoint: str | None = Field(
        default=None,
        description="S3 endpoint URL (for MinIO/LocalStack)",
    )
    s3_bucket: str = Field(description="S3 bucket name")
    s3_access_key: str = Field(description="S3 access key")
    s3_secret_key: str = Field(description="S3 secret key")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    s3_use_ssl: bool = Field(default=True, description="Use SSL for S3")

    # AWS SES
    ses_region: str = Field(default="us-east-1", description="SES region")
    ses_access_key: str = Field(description="SES access key")
    ses_secret_key: str = Field(description="SES secret key")
    ses_configuration_set: str | None = Field(
        default=None,
        description="SES configuration set",
    )
    ses_endpoint: str | None = Field(
        default=None,
        description="SES endpoint (for LocalStack)",
    )

    # Security
    api_key_secret: str = Field(
        description="Secret key for API key HMAC signing",
    )
    signed_url_secret: str = Field(
        description="Secret key for signed URL generation",
    )
    signed_url_expiration: int = Field(
        default=3600,
        description="Signed URL expiration in seconds",
    )

    # Pagination
    default_page_size: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Default pagination size",
    )
    max_page_size: int = Field(
        default=100,
        ge=1,
        le=200,
        description="Maximum pagination size",
    )

    # Webhooks
    webhook_timeout: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Webhook HTTP timeout in seconds",
    )
    webhook_max_retries: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum webhook retry attempts",
    )
    webhook_retry_delays: list[int] = Field(
        default=[1, 5, 25, 125, 625],
        description="Retry delays in seconds (exponential backoff)",
    )

    # Workers
    worker_concurrency: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Worker concurrency",
    )

    # Email Processing
    max_attachment_size: int = Field(
        default=25 * 1024 * 1024,  # 25 MB
        description="Maximum attachment size in bytes",
    )
    max_email_size: int = Field(
        default=40 * 1024 * 1024,  # 40 MB (SES limit)
        description="Maximum email size in bytes",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON array string or comma-separated
            if v.startswith("["):
                import json

                return json.loads(v)
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic)."""
        url = str(self.database_url)
        return url.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
