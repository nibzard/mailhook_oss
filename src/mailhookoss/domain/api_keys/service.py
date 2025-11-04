"""API Key domain service."""

import hashlib
import secrets
from datetime import datetime

from mailhookoss.domain.api_keys.entities import APIKey
from mailhookoss.domain.api_keys.value_objects import APIKeyType
from mailhookoss.utils.id_generator import generate_api_key_id, generate_id


class APIKeyService:
    """Domain service for API key operations."""

    @staticmethod
    def generate_secret(key_type: APIKeyType) -> str:
        """Generate a new API key secret.

        Args:
            key_type: Type of API key

        Returns:
            Generated secret with appropriate prefix
        """
        prefix = key_type.secret_prefix
        random_part = secrets.token_urlsafe(32)  # 256 bits
        return f"{prefix}_{random_part}"

    @staticmethod
    def hash_secret(secret: str) -> str:
        """Hash an API key secret.

        Args:
            secret: Plain text secret

        Returns:
            Hashed secret (SHA-256)
        """
        return hashlib.sha256(secret.encode()).hexdigest()

    @staticmethod
    def truncate_secret(secret: str) -> str:
        """Truncate secret for identification.

        Args:
            secret: Full secret

        Returns:
            First 12 characters
        """
        return secret[:12] if len(secret) >= 12 else secret

    @staticmethod
    def verify_secret(secret: str, secret_hash: str) -> bool:
        """Verify a secret against its hash.

        Args:
            secret: Plain text secret to verify
            secret_hash: Stored hash

        Returns:
            True if secret matches, False otherwise
        """
        computed_hash = APIKeyService.hash_secret(secret)
        return secrets.compare_digest(computed_hash, secret_hash)

    @staticmethod
    def create_api_key(
        key_type: APIKeyType,
        tenant_id: str | None,
        note: str | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[APIKey, str]:
        """Create a new API key.

        Args:
            key_type: Type of API key
            tenant_id: Tenant ID (required for tenant keys, null for internal)
            note: Optional note
            expires_at: Optional expiration timestamp

        Returns:
            Tuple of (APIKey entity, plain text secret)
        """
        now = datetime.utcnow()
        key_id = generate_api_key_id()
        secret = APIKeyService.generate_secret(key_type)
        secret_hash = APIKeyService.hash_secret(secret)
        truncated_secret = APIKeyService.truncate_secret(secret)

        api_key = APIKey(
            id=key_id,
            key_type=key_type,
            secret_hash=secret_hash,
            truncated_secret=truncated_secret,
            tenant_id=tenant_id,
            note=note,
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )

        return api_key, secret
