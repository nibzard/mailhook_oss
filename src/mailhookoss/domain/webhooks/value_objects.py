"""Webhook value objects."""

from dataclasses import dataclass
from enum import Enum

from mailhookoss.domain.common.value_object import ValueObject


class WebhookEvent(str, Enum):
    """Webhook event types."""

    EMAIL_RECEIVED = "email.received"
    EMAIL_SENT = "email.sent"
    EMAIL_BOUNCED = "email.bounced"
    EMAIL_COMPLAINED = "email.complained"
    THREAD_CREATED = "thread.created"
    THREAD_UPDATED = "thread.updated"


class DeliveryStatus(str, Enum):
    """Webhook delivery status."""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    FAILED_PERMANENT = "failed_permanent"
    EXPIRED = "expired"


@dataclass(frozen=True)
class WebhookFilters(ValueObject):
    """Webhook filters for event filtering."""

    events: list[str]  # List of WebhookEvent values
    mailbox_ids: list[str] = None  # type: ignore[assignment]  # Empty means all mailboxes
    domain_ids: list[str] = None  # type: ignore[assignment]  # Empty means all domains
    labels: list[str] = None  # type: ignore[assignment]  # Filter by email labels
    from_patterns: list[str] = None  # type: ignore[assignment]  # Filter by sender patterns
    to_patterns: list[str] = None  # type: ignore[assignment]  # Filter by recipient patterns

    def __post_init__(self) -> None:
        """Initialize empty lists for None fields."""
        # Use object.__setattr__ since this is a frozen dataclass
        if self.mailbox_ids is None:
            object.__setattr__(self, "mailbox_ids", [])
        if self.domain_ids is None:
            object.__setattr__(self, "domain_ids", [])
        if self.labels is None:
            object.__setattr__(self, "labels", [])
        if self.from_patterns is None:
            object.__setattr__(self, "from_patterns", [])
        if self.to_patterns is None:
            object.__setattr__(self, "to_patterns", [])

    def matches_event(self, event: str) -> bool:
        """Check if event matches filter.

        Args:
            event: Event type

        Returns:
            True if event matches
        """
        return event in self.events

    def matches_mailbox(self, mailbox_id: str) -> bool:
        """Check if mailbox matches filter.

        Args:
            mailbox_id: Mailbox ID

        Returns:
            True if mailbox matches (or filter is empty)
        """
        if not self.mailbox_ids:
            return True
        return mailbox_id in self.mailbox_ids

    def matches_domain(self, domain_id: str) -> bool:
        """Check if domain matches filter.

        Args:
            domain_id: Domain ID

        Returns:
            True if domain matches (or filter is empty)
        """
        if not self.domain_ids:
            return True
        return domain_id in self.domain_ids

    def matches_labels(self, email_labels: list[str]) -> bool:
        """Check if email labels match filter.

        Args:
            email_labels: Email labels

        Returns:
            True if any label matches (or filter is empty)
        """
        if not self.labels:
            return True
        return any(label in self.labels for label in email_labels)

    def matches_address_pattern(self, address: str, patterns: list[str]) -> bool:
        """Check if address matches any pattern.

        Args:
            address: Email address
            patterns: List of patterns

        Returns:
            True if address matches any pattern
        """
        if not patterns:
            return True

        address_lower = address.lower()
        for pattern in patterns:
            pattern_lower = pattern.lower()

            # Exact match
            if pattern_lower == address_lower:
                return True

            # Domain wildcard (*@example.com)
            if pattern_lower.startswith("*@"):
                domain = pattern_lower[2:]
                if address_lower.endswith(f"@{domain}"):
                    return True

            # User wildcard (user@*)
            if pattern_lower.endswith("@*"):
                user = pattern_lower[:-2]
                if address_lower.startswith(f"{user}@"):
                    return True

            # Match all
            if pattern_lower == "*":
                return True

        return False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "events": self.events,
            "mailbox_ids": self.mailbox_ids,
            "domain_ids": self.domain_ids,
            "labels": self.labels,
            "from_patterns": self.from_patterns,
            "to_patterns": self.to_patterns,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WebhookFilters":
        """Create from dictionary."""
        return cls(
            events=data.get("events", []),
            mailbox_ids=data.get("mailbox_ids"),
            domain_ids=data.get("domain_ids"),
            labels=data.get("labels"),
            from_patterns=data.get("from_patterns"),
            to_patterns=data.get("to_patterns"),
        )
