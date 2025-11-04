"""API Key domain entities."""

from datetime import datetime

from mailhookoss.domain.api_keys.value_objects import APIKeyType
from mailhookoss.domain.common.entity import AggregateRoot


class APIKey(AggregateRoot):
    """API Key aggregate root.

    API keys are used for authentication. They come in two types:
    - Tenant keys: Scoped to a single tenant
    - Internal keys: Can impersonate any tenant
    """

    def __init__(
        self,
        id: str,
        key_type: APIKeyType,
        secret_hash: str,
        truncated_secret: str,
        tenant_id: str | None,
        note: str | None,
        expires_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize API key.

        Args:
            id: Unique API key identifier
            key_type: Type of API key (tenant or internal)
            secret_hash: Hashed secret for verification
            truncated_secret: First 12 characters for identification
            tenant_id: Tenant ID (null for internal keys)
            note: Optional note describing the key's purpose
            expires_at: Expiration timestamp (null for no expiration)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self._key_type = key_type
        self._secret_hash = secret_hash
        self._truncated_secret = truncated_secret
        self._tenant_id = tenant_id
        self._note = note
        self._expires_at = expires_at

    @property
    def key_type(self) -> APIKeyType:
        """Get API key type."""
        return self._key_type

    @property
    def secret_hash(self) -> str:
        """Get hashed secret."""
        return self._secret_hash

    @property
    def truncated_secret(self) -> str:
        """Get truncated secret for identification."""
        return self._truncated_secret

    @property
    def tenant_id(self) -> str | None:
        """Get tenant ID (null for internal keys)."""
        return self._tenant_id

    @property
    def note(self) -> str | None:
        """Get optional note."""
        return self._note

    @property
    def expires_at(self) -> datetime | None:
        """Get expiration timestamp."""
        return self._expires_at

    def is_expired(self, now: datetime | None = None) -> bool:
        """Check if the API key is expired.

        Args:
            now: Current timestamp (defaults to datetime.utcnow())

        Returns:
            True if expired, False otherwise
        """
        if self._expires_at is None:
            return False

        check_time = now or datetime.utcnow()
        return check_time >= self._expires_at

    def is_internal(self) -> bool:
        """Check if this is an internal key."""
        return self._key_type == APIKeyType.INTERNAL

    def is_tenant_key(self) -> bool:
        """Check if this is a tenant key."""
        return self._key_type == APIKeyType.TENANT

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"APIKey(id={self.id!r}, type={self.key_type.value!r}, "
            f"tenant_id={self.tenant_id!r})"
        )
