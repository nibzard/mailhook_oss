"""API Key database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from mailhookoss.domain.api_keys.value_objects import APIKeyType
from mailhookoss.infrastructure.database.base import Base, TimestampMixin


class APIKeyModel(Base, TimestampMixin):
    """API Key database model."""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    key_type: Mapped[str] = mapped_column(String(20), nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    truncated_secret: Mapped[str] = mapped_column(String(12), nullable=False)
    tenant_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_api_keys_tenant_id", "tenant_id"),
        Index("ix_api_keys_secret_hash", "secret_hash"),
    )

    def to_entity(self) -> "APIKey":
        """Convert database model to domain entity.

        Returns:
            APIKey domain entity
        """
        from mailhookoss.domain.api_keys.entities import APIKey

        return APIKey(
            id=self.id,
            key_type=APIKeyType(self.key_type),
            secret_hash=self.secret_hash,
            truncated_secret=self.truncated_secret,
            tenant_id=self.tenant_id,
            note=self.note,
            expires_at=self.expires_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(api_key: "APIKey") -> "APIKeyModel":
        """Create database model from domain entity.

        Args:
            api_key: APIKey domain entity

        Returns:
            APIKey database model
        """
        return APIKeyModel(
            id=api_key.id,
            key_type=api_key.key_type.value,
            secret_hash=api_key.secret_hash,
            truncated_secret=api_key.truncated_secret,
            tenant_id=api_key.tenant_id,
            note=api_key.note,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
        )
