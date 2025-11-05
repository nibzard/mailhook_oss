"""Tenant repository interface."""

from abc import abstractmethod

from mailhookoss.domain.common.repository import Repository
from mailhookoss.domain.tenants.entities import Tenant


class TenantRepository(Repository[Tenant]):
    """Repository interface for Tenant aggregate."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Tenant | None:
        """Get tenant by name.

        Args:
            name: Tenant name

        Returns:
            Tenant if found, None otherwise
        """

    @abstractmethod
    async def list(
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
