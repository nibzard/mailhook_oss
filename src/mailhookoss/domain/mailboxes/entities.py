"""Mailbox entities."""

from datetime import datetime

from mailhookoss.domain.common.entity import AggregateRoot
from mailhookoss.domain.mailboxes.exceptions import InvalidLocalPartError
from mailhookoss.domain.mailboxes.value_objects import (
    InboundPolicy,
    MailboxFilters,
    SpamPolicy,
)


class Mailbox(AggregateRoot):
    """Mailbox aggregate root.

    Represents an email alias/mailbox (e.g., support@acme.dev).
    The local_part is the part before @ (e.g., "support").
    """

    def __init__(
        self,
        id: str,
        tenant_id: str,
        domain_id: str,
        local_part: str,
        active: bool,
        sender_name: str,
        spam_policy: SpamPolicy,
        inbound_policy: InboundPolicy,
        filters: MailboxFilters,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize mailbox.

        Args:
            id: Unique mailbox identifier
            tenant_id: Owning tenant ID
            domain_id: Domain ID this mailbox belongs to
            local_part: Local part of email address (before @)
            active: Whether the mailbox is active
            sender_name: Display name for sending emails
            spam_policy: Spam handling policy
            inbound_policy: Inbound participant trust policy
            filters: Email filter lists
            created_at: Creation timestamp
            updated_at: Last update timestamp

        Raises:
            InvalidLocalPartError: If local_part is invalid
        """
        super().__init__(id, created_at, updated_at)
        self._validate_local_part(local_part)
        self._tenant_id = tenant_id
        self._domain_id = domain_id
        self._local_part = local_part
        self._active = active
        self._sender_name = sender_name
        self._spam_policy = spam_policy
        self._inbound_policy = inbound_policy
        self._filters = filters

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def domain_id(self) -> str:
        """Get domain ID."""
        return self._domain_id

    @property
    def local_part(self) -> str:
        """Get local part."""
        return self._local_part

    @property
    def active(self) -> bool:
        """Get active status."""
        return self._active

    @property
    def sender_name(self) -> str:
        """Get sender display name."""
        return self._sender_name

    @property
    def spam_policy(self) -> SpamPolicy:
        """Get spam policy."""
        return self._spam_policy

    @property
    def inbound_policy(self) -> InboundPolicy:
        """Get inbound policy."""
        return self._inbound_policy

    @property
    def filters(self) -> MailboxFilters:
        """Get email filters."""
        return self._filters

    def get_email_address(self, domain_name: str) -> str:
        """Get full email address.

        Args:
            domain_name: Domain name

        Returns:
            Full email address (local@domain)
        """
        return f"{self._local_part}@{domain_name}"

    def activate(self) -> None:
        """Activate the mailbox."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate the mailbox."""
        self._active = False

    def update_sender_name(self, sender_name: str) -> None:
        """Update sender display name.

        Args:
            sender_name: New sender name
        """
        self._sender_name = sender_name

    def update_spam_policy(self, policy: SpamPolicy) -> None:
        """Update spam policy.

        Args:
            policy: New spam policy
        """
        self._spam_policy = policy

    def update_inbound_policy(self, policy: InboundPolicy) -> None:
        """Update inbound policy.

        Args:
            policy: New inbound policy
        """
        self._inbound_policy = policy

    def update_filters(self, filters: MailboxFilters) -> None:
        """Update email filters.

        Args:
            filters: New filters
        """
        self._filters = filters

    def should_accept_email(self, from_email: str) -> bool:
        """Check if email should be accepted based on filters.

        Args:
            from_email: Sender email address

        Returns:
            True if email should be accepted
        """
        # Check deny list first
        if self._filters.is_denied(from_email):
            return False

        # If allow list is configured, must be in it
        if self._filters.has_allow_list():
            return self._filters.is_allowed(from_email)

        # No allow list, accept by default
        return True

    @staticmethod
    def _validate_local_part(local_part: str) -> None:
        """Validate email local part.

        Args:
            local_part: Local part to validate

        Raises:
            InvalidLocalPartError: If local part is invalid
        """
        if not local_part or not local_part.strip():
            raise InvalidLocalPartError("Local part cannot be empty")

        if len(local_part) > 64:
            raise InvalidLocalPartError("Local part too long (max 64 characters)")

        # Basic validation - could be enhanced
        invalid_chars = ["@", " ", "\t", "\n"]
        for char in invalid_chars:
            if char in local_part:
                raise InvalidLocalPartError(f"Local part contains invalid character: {char!r}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Mailbox(id={self.id!r}, local_part={self.local_part!r}, "
            f"domain_id={self.domain_id!r})"
        )
