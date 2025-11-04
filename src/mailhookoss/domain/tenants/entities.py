"""Tenant domain entities."""

from datetime import datetime

from mailhookoss.domain.common.entity import AggregateRoot
from mailhookoss.domain.tenants.exceptions import InvalidTenantNameError


class Tenant(AggregateRoot):
    """Tenant aggregate root.

    A tenant represents an organization or user account that owns
    domains, mailboxes, and emails.
    """

    def __init__(
        self,
        id: str,
        name: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize tenant.

        Args:
            id: Unique tenant identifier
            name: Human-readable tenant name
            created_at: Creation timestamp
            updated_at: Last update timestamp

        Raises:
            InvalidTenantNameError: If name is invalid
        """
        super().__init__(id, created_at, updated_at)
        self._validate_name(name)
        self._name = name

    @property
    def name(self) -> str:
        """Get tenant name."""
        return self._name

    def update_name(self, name: str) -> None:
        """Update tenant name.

        Args:
            name: New tenant name

        Raises:
            InvalidTenantNameError: If name is invalid
        """
        self._validate_name(name)
        self._name = name

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate tenant name.

        Args:
            name: Tenant name to validate

        Raises:
            InvalidTenantNameError: If name is invalid
        """
        if not name or not name.strip():
            raise InvalidTenantNameError("Tenant name cannot be empty")

        if len(name) > 255:
            raise InvalidTenantNameError("Tenant name cannot exceed 255 characters")

    def __repr__(self) -> str:
        """String representation."""
        return f"Tenant(id={self.id!r}, name={self.name!r})"
