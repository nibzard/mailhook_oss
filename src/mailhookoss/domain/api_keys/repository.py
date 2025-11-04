"""API Key repository interface."""

from abc import abstractmethod

from mailhookoss.domain.api_keys.entities import APIKey
from mailhookoss.domain.common.repository import Repository


class APIKeyRepository(Repository[APIKey]):
    """Repository interface for APIKey aggregate."""

    @abstractmethod
    async def get_by_secret_hash(self, secret_hash: str) -> APIKey | None:
        """Get API key by secret hash.

        Args:
            secret_hash: Hashed secret

        Returns:
            APIKey if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[APIKey], str | None, str | None]:
        """List API keys for a specific tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of keys to return
            cursor: Pagination cursor

        Returns:
            Tuple of (api_keys, next_cursor, prev_cursor)
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[APIKey], str | None, str | None]:
        """List all API keys (internal use only).

        Args:
            limit: Maximum number of keys to return
            cursor: Pagination cursor

        Returns:
            Tuple of (api_keys, next_cursor, prev_cursor)
        """
        pass
