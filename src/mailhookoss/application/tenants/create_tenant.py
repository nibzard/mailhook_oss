"""Create tenant use case."""

from datetime import datetime, timezone

from mailhookoss.domain.tenants.entities import Tenant
from mailhookoss.domain.tenants.exceptions import TenantAlreadyExistsError
from mailhookoss.domain.tenants.repository import TenantRepository
from mailhookoss.utils.id_generator import generate_tenant_id


class CreateTenantUseCase:
    """Use case for creating a new tenant."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Initialize use case.

        Args:
            tenant_repository: Tenant repository
        """
        self._tenant_repository = tenant_repository

    async def execute(self, name: str) -> Tenant:
        """Create a new tenant.

        Args:
            name: Tenant name

        Returns:
            Created tenant

        Raises:
            TenantAlreadyExistsError: If tenant with name already exists
            InvalidTenantNameError: If name is invalid
        """
        # Check if tenant with name already exists
        existing = await self._tenant_repository.get_by_name(name)
        if existing:
            raise TenantAlreadyExistsError(name)

        # Create new tenant
        now = datetime.now(timezone.utc)
        tenant = Tenant(
            id=generate_tenant_id(),
            name=name,
            created_at=now,
            updated_at=now,
        )

        # Save tenant
        return await self._tenant_repository.save(tenant)
