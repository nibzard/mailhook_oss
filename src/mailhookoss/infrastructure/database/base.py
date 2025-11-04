"""SQLAlchemy base models and mixins."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Import all models to ensure they're registered with Base.metadata
# This is needed for Alembic autogenerate to work
def import_all_models() -> None:
    """Import all models to register them with SQLAlchemy."""
    from mailhookoss.infrastructure.database.models import (  # noqa: F401
        APIKeyModel,
        DomainModel,
        MailboxModel,
        TenantModel,
    )


import_all_models()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the entity is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark the entity as deleted."""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft deleted entity."""
        self.deleted_at = None


class TenantMixin:
    """Mixin for tenant-scoped entities."""

    tenant_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
