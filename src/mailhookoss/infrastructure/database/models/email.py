"""Email database model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from mailhookoss.domain.emails.entities import Email, Thread
from mailhookoss.domain.emails.value_objects import (
    Attachment,
    EmailAddress,
    EmailDirection,
    EmailHeaders,
    UserData,
)
from mailhookoss.infrastructure.database.models.base import Base, TimestampMixin


class EmailModel(Base, TimestampMixin):
    """Email database model."""

    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mailbox_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message_id: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(1000), nullable=False)
    from_addr: Mapped[dict] = mapped_column(JSON, nullable=False)
    to: Mapped[list] = mapped_column(JSON, nullable=False)
    cc: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    bcc: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    html: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    original_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    original_html: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    headers: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    attachments: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    labels: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    direction: Mapped[str] = mapped_column(String(20), nullable=False, server_default="inbound")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    custom_summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    user_data: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="{}")

    def to_entity(self) -> Email:
        """Convert model to domain entity."""
        return Email(
            id=self.id,
            tenant_id=self.tenant_id,
            mailbox_id=self.mailbox_id,
            thread_id=self.thread_id,
            message_id=self.message_id,
            subject=self.subject,
            from_addr=EmailAddress.from_dict(self.from_addr),
            to=[EmailAddress.from_dict(addr) for addr in self.to],
            cc=[EmailAddress.from_dict(addr) for addr in self.cc],
            bcc=[EmailAddress.from_dict(addr) for addr in self.bcc],
            text=self.text,
            html=self.html,
            original_text=self.original_text,
            original_html=self.original_html,
            headers=EmailHeaders.from_dict(self.headers),
            attachments=[Attachment.from_dict(att) for att in self.attachments],
            labels=self.labels,
            direction=EmailDirection(self.direction),
            received_at=self.received_at,
            custom_summary=self.custom_summary,
            ai_summary=self.ai_summary,
            user_data=UserData.from_dict(self.user_data),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: Email) -> "EmailModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            tenant_id=entity.tenant_id,
            mailbox_id=entity.mailbox_id,
            thread_id=entity.thread_id,
            message_id=entity.message_id,
            subject=entity.subject,
            from_addr=entity.from_addr.to_dict(),
            to=[addr.to_dict() for addr in entity.to],
            cc=[addr.to_dict() for addr in entity.cc],
            bcc=[addr.to_dict() for addr in entity.bcc],
            text=entity.text,
            html=entity.html,
            original_text=entity.original_text,
            original_html=entity.original_html,
            headers=entity.headers.to_dict(),
            attachments=[att.to_dict() for att in entity.attachments],
            labels=entity.labels,
            direction=entity.direction.value,
            received_at=entity.received_at,
            custom_summary=entity.custom_summary,
            ai_summary=entity.ai_summary,
            user_data=entity.user_data.to_dict(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def update_from_entity(self, entity: Email) -> None:
        """Update model from domain entity."""
        self.subject = entity.subject
        self.from_addr = entity.from_addr.to_dict()
        self.to = [addr.to_dict() for addr in entity.to]
        self.cc = [addr.to_dict() for addr in entity.cc]
        self.bcc = [addr.to_dict() for addr in entity.bcc]
        self.text = entity.text
        self.html = entity.html
        self.original_text = entity.original_text
        self.original_html = entity.original_html
        self.headers = entity.headers.to_dict()
        self.attachments = [att.to_dict() for att in entity.attachments]
        self.labels = entity.labels
        self.custom_summary = entity.custom_summary
        self.ai_summary = entity.ai_summary
        self.user_data = entity.user_data.to_dict()
        self.updated_at = entity.updated_at


class ThreadModel(Base, TimestampMixin):
    """Thread database model."""

    __tablename__ = "threads"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mailbox_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(1000), nullable=False)
    participants: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    labels: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    has_attachments: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    has_hidden_messages: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    first_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    custom_summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    user_data: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="{}")

    def to_entity(self) -> Thread:
        """Convert model to domain entity."""
        return Thread(
            id=self.id,
            tenant_id=self.tenant_id,
            mailbox_id=self.mailbox_id,
            subject=self.subject,
            participants=[EmailAddress.from_dict(addr) for addr in self.participants],
            labels=self.labels,
            message_count=self.message_count,
            has_attachments=self.has_attachments,
            has_hidden_messages=self.has_hidden_messages,
            first_message_at=self.first_message_at,
            last_message_at=self.last_message_at,
            custom_summary=self.custom_summary,
            ai_summary=self.ai_summary,
            user_data=UserData.from_dict(self.user_data),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: Thread) -> "ThreadModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            tenant_id=entity.tenant_id,
            mailbox_id=entity.mailbox_id,
            subject=entity.subject,
            participants=[addr.to_dict() for addr in entity.participants],
            labels=entity.labels,
            message_count=entity.message_count,
            has_attachments=entity.has_attachments,
            has_hidden_messages=entity.has_hidden_messages,
            first_message_at=entity.first_message_at,
            last_message_at=entity.last_message_at,
            custom_summary=entity.custom_summary,
            ai_summary=entity.ai_summary,
            user_data=entity.user_data.to_dict(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def update_from_entity(self, entity: Thread) -> None:
        """Update model from domain entity."""
        self.subject = entity.subject
        self.participants = [addr.to_dict() for addr in entity.participants]
        self.labels = entity.labels
        self.message_count = entity.message_count
        self.has_attachments = entity.has_attachments
        self.has_hidden_messages = entity.has_hidden_messages
        self.first_message_at = entity.first_message_at
        self.last_message_at = entity.last_message_at
        self.custom_summary = entity.custom_summary
        self.ai_summary = entity.ai_summary
        self.user_data = entity.user_data.to_dict()
        self.updated_at = entity.updated_at
