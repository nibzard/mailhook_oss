"""Domain database model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from mailhookoss.domain.domains.value_objects import (
    DNSRecord,
    VerificationMethod,
    VerificationStatus,
)
from mailhookoss.infrastructure.database.base import Base, TimestampMixin


class DomainModel(Base, TimestampMixin):
    """Domain database model."""

    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain: Mapped[str] = mapped_column(String(253), nullable=False, unique=True)
    unicode_domain: Mapped[str] = mapped_column(String(253), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=VerificationStatus.PENDING.value,
    )
    verification_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    dns_records: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)

    __table_args__ = (
        Index("ix_domains_tenant_id", "tenant_id"),
        Index("ix_domains_domain", "domain", unique=True),
    )

    def to_entity(self) -> "Domain":  # noqa: F821
        """Convert database model to domain entity.

        Returns:
            Domain domain entity
        """
        from mailhookoss.domain.domains.entities import Domain

        # Convert JSON dns_records to DNSRecord objects
        dns_record_objects = [
            DNSRecord.from_dict(record) for record in (self.dns_records or [])
        ]

        return Domain(
            id=self.id,
            tenant_id=self.tenant_id,
            domain=self.domain,
            unicode_domain=self.unicode_domain,
            active=self.active,
            verification_status=VerificationStatus(self.verification_status),
            verification_method=(
                VerificationMethod(self.verification_method)
                if self.verification_method
                else None
            ),
            verified_at=self.verified_at,
            dns_records=dns_record_objects,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(domain: "Domain") -> "DomainModel":  # noqa: F821
        """Create database model from domain entity.

        Args:
            domain: Domain domain entity

        Returns:
            Domain database model
        """
        # Convert DNSRecord objects to JSON-serializable dicts
        dns_records_json = [record.to_dict() for record in domain.dns_records]

        return DomainModel(
            id=domain.id,
            tenant_id=domain.tenant_id,
            domain=domain.domain,
            unicode_domain=domain.unicode_domain,
            active=domain.active,
            verification_status=domain.verification_status.value,
            verification_method=(
                domain.verification_method.value if domain.verification_method else None
            ),
            verified_at=domain.verified_at,
            dns_records=dns_records_json,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def update_from_entity(self, domain: "Domain") -> None:  # noqa: F821
        """Update model fields from domain entity.

        Args:
            domain: Domain domain entity
        """
        dns_records_json = [record.to_dict() for record in domain.dns_records]

        self.active = domain.active
        self.verification_status = domain.verification_status.value
        self.verification_method = (
            domain.verification_method.value if domain.verification_method else None
        )
        self.verified_at = domain.verified_at
        self.dns_records = dns_records_json
        self.updated_at = domain.updated_at
