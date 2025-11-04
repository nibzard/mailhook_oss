"""List domains use case."""

from mailhookoss.domain.domains.entities import Domain
from mailhookoss.domain.domains.repository import DomainRepository


class ListDomainsUseCase:
    """Use case for listing domains."""

    def __init__(self, domain_repository: DomainRepository) -> None:
        """Initialize use case.

        Args:
            domain_repository: Domain repository
        """
        self._domain_repository = domain_repository

    async def execute(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Domain], str | None, str | None]:
        """List domains for a tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of domains to return
            cursor: Pagination cursor
            search: Optional search query

        Returns:
            Tuple of (domains, next_cursor, prev_cursor)
        """
        return await self._domain_repository.list_by_tenant(
            tenant_id=tenant_id,
            limit=limit,
            cursor=cursor,
            search=search,
        )
