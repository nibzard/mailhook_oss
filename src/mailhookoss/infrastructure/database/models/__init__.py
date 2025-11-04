"""Database models."""

from mailhookoss.infrastructure.database.models.api_key import APIKeyModel
from mailhookoss.infrastructure.database.models.domain import DomainModel
from mailhookoss.infrastructure.database.models.email import EmailModel, ThreadModel
from mailhookoss.infrastructure.database.models.mailbox import MailboxModel
from mailhookoss.infrastructure.database.models.tenant import TenantModel

__all__ = [
    "APIKeyModel",
    "DomainModel",
    "EmailModel",
    "MailboxModel",
    "TenantModel",
    "ThreadModel",
]
