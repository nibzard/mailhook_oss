"""List tenants use case."""

from mailhookoss.domain.tenants.entities import Tenant
from mailhookoss.domain.tenants.repository import TenantRepository


class ListTenantsUseCase:
    """Use case for listing tenants."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Initialize use case.

        Args:
            tenant_repository: Tenant repository
        """
        self._tenant_repository = tenant_repository

    async def execute(
        self,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Tenant], str | None, str | None]:
        """List tenants with pagination.

        Args:
            limit: Maximum number of tenants to return
            cursor: Pagination cursor

        Returns:
            Tuple of (tenants, next_cursor, prev_cursor)
        """
        return await self._tenant_repository.list(limit=limit, cursor=cursor)
