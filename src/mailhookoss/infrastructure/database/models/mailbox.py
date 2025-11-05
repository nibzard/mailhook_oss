"""Mailbox database model."""

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from mailhookoss.domain.mailboxes.value_objects import (
    InboundPolicy,
    MailboxFilters,
    SpamPolicy,
)
from mailhookoss.infrastructure.database.base import Base, TimestampMixin


class MailboxModel(Base, TimestampMixin):
    """Mailbox database model."""

    __tablename__ = "mailboxes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    local_part: Mapped[str] = mapped_column(String(64), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sender_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    spam_policy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SpamPolicy.MARK.value,
    )
    inbound_policy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=InboundPolicy.THREAD_TRUST.value,
    )
    filters: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"allow": [], "deny": []},
    )

    __table_args__ = (
        Index("ix_mailboxes_tenant_id", "tenant_id"),
        Index("ix_mailboxes_domain_id", "domain_id"),
        Index(
            "ix_mailboxes_domain_local_part",
            "domain_id",
            "local_part",
            unique=True,
        ),
    )

    def to_entity(self) -> "Mailbox":  # noqa: F821
        """Convert database model to domain entity.

        Returns:
            Mailbox domain entity
        """
        from mailhookoss.domain.mailboxes.entities import Mailbox

        filters = MailboxFilters.from_dict(self.filters or {"allow": [], "deny": []})

        return Mailbox(
            id=self.id,
            tenant_id=self.tenant_id,
            domain_id=self.domain_id,
            local_part=self.local_part,
            active=self.active,
            sender_name=self.sender_name,
            spam_policy=SpamPolicy(self.spam_policy),
            inbound_policy=InboundPolicy(self.inbound_policy),
            filters=filters,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(mailbox: "Mailbox") -> "MailboxModel":  # noqa: F821
        """Create database model from domain entity.

        Args:
            mailbox: Mailbox domain entity

        Returns:
            Mailbox database model
        """
        return MailboxModel(
            id=mailbox.id,
            tenant_id=mailbox.tenant_id,
            domain_id=mailbox.domain_id,
            local_part=mailbox.local_part,
            active=mailbox.active,
            sender_name=mailbox.sender_name,
            spam_policy=mailbox.spam_policy.value,
            inbound_policy=mailbox.inbound_policy.value,
            filters=mailbox.filters.to_dict(),
            created_at=mailbox.created_at,
            updated_at=mailbox.updated_at,
        )

    def update_from_entity(self, mailbox: "Mailbox") -> None:  # noqa: F821
        """Update model fields from domain entity.

        Args:
            mailbox: Mailbox domain entity
        """
        self.active = mailbox.active
        self.sender_name = mailbox.sender_name
        self.spam_policy = mailbox.spam_policy.value
        self.inbound_policy = mailbox.inbound_policy.value
        self.filters = mailbox.filters.to_dict()
        self.updated_at = mailbox.updated_at
