"""API Key value objects."""

from enum import Enum


class APIKeyType(str, Enum):
    """API key type enumeration."""

    TENANT = "tenant"
    INTERNAL = "internal"

    @property
    def secret_prefix(self) -> str:
        """Get the secret prefix for this key type."""
        if self == APIKeyType.TENANT:
            return "mhsec"
        return "mhisec"
