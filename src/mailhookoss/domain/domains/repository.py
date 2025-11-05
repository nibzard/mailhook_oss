"""Domain repository interface."""

from abc import abstractmethod

from mailhookoss.domain.common.repository import Repository
from mailhookoss.domain.domains.entities import Domain


class DomainRepository(Repository[Domain]):
    """Repository interface for Domain aggregate."""

    @abstractmethod
    async def get_by_domain_name(self, domain: str) -> Domain | None:
        """Get domain by domain name.

        Args:
            domain: Domain name

        Returns:
            Domain if found, None otherwise
        """

    @abstractmethod
    async def get_by_domain_or_id(self, domain_or_id: str) -> Domain | None:
        """Get domain by domain name or ID.

        Args:
            domain_or_id: Domain name or domain ID

        Returns:
            Domain if found, None otherwise
        """

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Domain], str | None, str | None]:
        """List domains for a specific tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of domains to return
            cursor: Pagination cursor
            search: Optional search query

        Returns:
            Tuple of (domains, next_cursor, prev_cursor)
        """
