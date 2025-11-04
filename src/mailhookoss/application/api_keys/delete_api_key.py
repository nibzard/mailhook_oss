"""Delete API key use case."""

from mailhookoss.domain.api_keys.exceptions import APIKeyNotFoundError
from mailhookoss.domain.api_keys.repository import APIKeyRepository
from mailhookoss.domain.api_keys.service import APIKeyService
from mailhookoss.domain.common.exceptions import AuthorizationError


class DeleteAPIKeyUseCase:
    """Use case for deleting an API key."""

    def __init__(self, api_key_repository: APIKeyRepository) -> None:
        """Initialize use case.

        Args:
            api_key_repository: API key repository
        """
        self._api_key_repository = api_key_repository

    async def execute(
        self,
        key_id_or_secret: str,
        tenant_id: str | None = None,
    ) -> None:
        """Delete an API key by ID or secret.

        Args:
            key_id_or_secret: API key ID or full secret
            tenant_id: Tenant ID for authorization (None for internal keys)

        Raises:
            APIKeyNotFoundError: If API key not found
            AuthorizationError: If not authorized to delete this key
        """
        # Check if it's a secret or ID
        api_key = None
        if key_id_or_secret.startswith("mhsec_") or key_id_or_secret.startswith("mhisec_"):
            # It's a secret, hash and lookup
            secret_hash = APIKeyService.hash_secret(key_id_or_secret)
            api_key = await self._api_key_repository.get_by_secret_hash(secret_hash)
        else:
            # It's an ID
            api_key = await self._api_key_repository.get_by_id(key_id_or_secret)

        if not api_key:
            raise APIKeyNotFoundError(key_id_or_secret)

        # Authorization check: can only delete if tenant matches or is internal
        if tenant_id and api_key.tenant_id and api_key.tenant_id != tenant_id:
            raise AuthorizationError(
                f"Not authorized to delete API key '{api_key.id}'"
            )

        # Delete the key
        await self._api_key_repository.delete(api_key.id)
