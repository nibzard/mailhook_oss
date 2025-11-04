"""Create API key use case."""

from datetime import datetime

from mailhookoss.domain.api_keys.entities import APIKey
from mailhookoss.domain.api_keys.repository import APIKeyRepository
from mailhookoss.domain.api_keys.service import APIKeyService
from mailhookoss.domain.api_keys.value_objects import APIKeyType
from mailhookoss.domain.tenants.exceptions import TenantNotFoundError
from mailhookoss.domain.tenants.repository import TenantRepository


class CreateAPIKeyUseCase:
    """Use case for creating a new API key."""

    def __init__(
        self,
        api_key_repository: APIKeyRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        """Initialize use case.

        Args:
            api_key_repository: API key repository
            tenant_repository: Tenant repository
        """
        self._api_key_repository = api_key_repository
        self._tenant_repository = tenant_repository

    async def execute(
        self,
        tenant_id: str,
        note: str | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[APIKey, str]:
        """Create a new tenant API key.

        Args:
            tenant_id: Tenant identifier
            note: Optional note
            expires_at: Optional expiration timestamp

        Returns:
            Tuple of (APIKey entity, plain text secret)

        Raises:
            TenantNotFoundError: If tenant not found
        """
        # Verify tenant exists
        tenant = await self._tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(tenant_id)

        # Create API key
        api_key, secret = APIKeyService.create_api_key(
            key_type=APIKeyType.TENANT,
            tenant_id=tenant_id,
            note=note,
            expires_at=expires_at,
        )

        # Save API key
        saved_key = await self._api_key_repository.save(api_key)

        return saved_key, secret
