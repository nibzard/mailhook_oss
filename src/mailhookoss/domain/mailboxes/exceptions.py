"""Mailbox domain exceptions."""

from mailhookoss.domain.common.exceptions import DomainException, ValidationError


class MailboxError(DomainException):
    """Base exception for mailbox-related errors."""



class InvalidLocalPartError(ValidationError):
    """Raised when mailbox local part is invalid."""



class MailboxNotFoundError(MailboxError):
    """Raised when mailbox is not found."""

    def __init__(self, mailbox_id_or_alias: str) -> None:
        super().__init__(f"Mailbox '{mailbox_id_or_alias}' not found")
        self.mailbox_id_or_alias = mailbox_id_or_alias


class MailboxAlreadyExistsError(MailboxError):
    """Raised when mailbox already exists."""

    def __init__(self, local_part: str, domain: str) -> None:
        super().__init__(f"Mailbox '{local_part}@{domain}' already exists")
        self.local_part = local_part
        self.domain = domain
