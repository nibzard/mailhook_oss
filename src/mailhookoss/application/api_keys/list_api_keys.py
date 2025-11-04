"""List API keys use case."""

from mailhookoss.domain.api_keys.entities import APIKey
from mailhookoss.domain.api_keys.repository import APIKeyRepository


class ListAPIKeysUseCase:
    """Use case for listing API keys."""

    def __init__(self, api_key_repository: APIKeyRepository) -> None:
        """Initialize use case.

        Args:
            api_key_repository: API key repository
        """
        self._api_key_repository = api_key_repository

    async def execute_for_tenant(
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
        return await self._api_key_repository.list_by_tenant(
            tenant_id=tenant_id,
            limit=limit,
            cursor=cursor,
        )

    async def execute_all(
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
        return await self._api_key_repository.list_all(
            limit=limit,
            cursor=cursor,
        )
