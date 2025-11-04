"""Update tenant use case."""

from mailhookoss.domain.tenants.entities import Tenant
from mailhookoss.domain.tenants.exceptions import TenantNotFoundError
from mailhookoss.domain.tenants.repository import TenantRepository


class UpdateTenantUseCase:
    """Use case for updating a tenant."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Initialize use case.

        Args:
            tenant_repository: Tenant repository
        """
        self._tenant_repository = tenant_repository

    async def execute(self, tenant_id: str, name: str) -> Tenant:
        """Update tenant.

        Args:
            tenant_id: Tenant identifier
            name: New tenant name

        Returns:
            Updated tenant

        Raises:
            TenantNotFoundError: If tenant not found
            InvalidTenantNameError: If name is invalid
        """
        # Get existing tenant
        tenant = await self._tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(tenant_id)

        # Update name (this validates the name)
        tenant.update_name(name)

        # Save updated tenant
        return await self._tenant_repository.save(tenant)
