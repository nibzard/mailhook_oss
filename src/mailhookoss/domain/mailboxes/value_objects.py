"""Mailbox value objects."""

from enum import Enum

from mailhookoss.domain.common.value_object import ValueObject


class SpamPolicy(str, Enum):
    """Spam handling policy."""

    MARK = "mark"  # Apply $junk label
    DELETE = "delete"  # Drop spam at receipt


class InboundPolicy(str, Enum):
    """Inbound participant trust policy."""

    THREAD_TRUST = "thread_trust"  # Trust existing thread participants
    PERMITTED_ONLY = "permitted_only"  # Only allow-listed senders


class MailboxFilters(ValueObject):
    """Email filter lists for a mailbox."""

    def __init__(
        self,
        allow: list[str] | None = None,
        deny: list[str] | None = None,
    ) -> None:
        """Initialize mailbox filters.

        Args:
            allow: List of allowed email addresses (whitelist)
            deny: List of denied email addresses (blacklist)
        """
        self.allow = allow or []
        self.deny = deny or []

    def is_allowed(self, email: str) -> bool:
        """Check if email address is explicitly allowed.

        Args:
            email: Email address to check

        Returns:
            True if in allow list, False otherwise
        """
        return email.lower() in [a.lower() for a in self.allow]

    def is_denied(self, email: str) -> bool:
        """Check if email address is denied.

        Args:
            email: Email address to check

        Returns:
            True if in deny list, False otherwise
        """
        return email.lower() in [d.lower() for d in self.deny]

    def has_allow_list(self) -> bool:
        """Check if allow list is configured.

        Returns:
            True if allow list is not empty
        """
        return len(self.allow) > 0

    def add_to_allow(self, email: str) -> None:
        """Add email to allow list.

        Args:
            email: Email address to allow
        """
        if not self.is_allowed(email):
            self.allow.append(email.lower())

    def add_to_deny(self, email: str) -> None:
        """Add email to deny list.

        Args:
            email: Email address to deny
        """
        if not self.is_denied(email):
            self.deny.append(email.lower())

    def remove_from_allow(self, email: str) -> None:
        """Remove email from allow list.

        Args:
            email: Email address to remove
        """
        self.allow = [a for a in self.allow if a.lower() != email.lower()]

    def remove_from_deny(self, email: str) -> None:
        """Remove email from deny list.

        Args:
            email: Email address to remove
        """
        self.deny = [d for d in self.deny if d.lower() != email.lower()]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "allow": self.allow,
            "deny": self.deny,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MailboxFilters":
        """Create MailboxFilters from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            MailboxFilters instance
        """
        return cls(
            allow=data.get("allow", []),
            deny=data.get("deny", []),
        )

    @classmethod
    def empty(cls) -> "MailboxFilters":
        """Create empty filters.

        Returns:
            Empty MailboxFilters
        """
        return cls(allow=[], deny=[])
