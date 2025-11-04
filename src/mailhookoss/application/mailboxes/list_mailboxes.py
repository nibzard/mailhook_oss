"""List mailboxes use case."""

from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.domain.mailboxes.entities import Mailbox
from mailhookoss.domain.mailboxes.repository import MailboxRepository


class ListMailboxesUseCase:
    """Use case for listing mailboxes."""

    def __init__(
        self,
        mailbox_repository: MailboxRepository,
        domain_repository: DomainRepository,
    ) -> None:
        """Initialize use case.

        Args:
            mailbox_repository: Mailbox repository
            domain_repository: Domain repository
        """
        self._mailbox_repository = mailbox_repository
        self._domain_repository = domain_repository

    async def execute_by_domain(
        self,
        domain_or_id: str,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Mailbox], str | None, str | None]:
        """List mailboxes for a specific domain.

        Args:
            domain_or_id: Domain name or ID
            tenant_id: Tenant identifier
            limit: Maximum number of mailboxes to return
            cursor: Pagination cursor
            search: Optional search query

        Returns:
            Tuple of (mailboxes, next_cursor, prev_cursor)

        Raises:
            DomainNotFoundError: If domain not found or doesn't belong to tenant
        """
        # Get domain and verify tenant ownership
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain or domain.tenant_id != tenant_id:
            raise DomainNotFoundError(domain_or_id)

        return await self._mailbox_repository.list_by_domain(
            domain_id=domain.id,
            limit=limit,
            cursor=cursor,
            search=search,
        )

    async def execute_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Mailbox], str | None, str | None]:
        """List all mailboxes for a tenant (across all domains).

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of mailboxes to return
            cursor: Pagination cursor

        Returns:
            Tuple of (mailboxes, next_cursor, prev_cursor)
        """
        return await self._mailbox_repository.list_by_tenant(
            tenant_id=tenant_id,
            limit=limit,
            cursor=cursor,
        )
