"""Get tenant use case."""

from mailhookoss.domain.tenants.entities import Tenant
from mailhookoss.domain.tenants.exceptions import TenantNotFoundError
from mailhookoss.domain.tenants.repository import TenantRepository


class GetTenantUseCase:
    """Use case for retrieving a tenant."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Initialize use case.

        Args:
            tenant_repository: Tenant repository
        """
        self._tenant_repository = tenant_repository

    async def execute(self, tenant_id: str) -> Tenant:
        """Get tenant by ID.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Tenant entity

        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self._tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(tenant_id)

        return tenant
