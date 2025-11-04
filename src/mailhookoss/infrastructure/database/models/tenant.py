"""Tenant database model."""

from datetime import datetime

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mailhookoss.infrastructure.database.base import Base, TimestampMixin


class TenantModel(Base, TimestampMixin):
    """Tenant database model."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Relationships (will be added as we implement other models)
    # domains = relationship("DomainModel", back_populates="tenant")
    # api_keys = relationship("APIKeyModel", back_populates="tenant")

    __table_args__ = (
        Index("ix_tenants_name", "name"),
    )

    def to_entity(self) -> "Tenant":
        """Convert database model to domain entity.

        Returns:
            Tenant domain entity
        """
        from mailhookoss.domain.tenants.entities import Tenant

        return Tenant(
            id=self.id,
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(tenant: "Tenant") -> "TenantModel":
        """Create database model from domain entity.

        Args:
            tenant: Tenant domain entity

        Returns:
            Tenant database model
        """
        return TenantModel(
            id=tenant.id,
            name=tenant.name,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )

    def update_from_entity(self, tenant: "Tenant") -> None:
        """Update model fields from domain entity.

        Args:
            tenant: Tenant domain entity
        """
        self.name = tenant.name
        self.updated_at = tenant.updated_at
