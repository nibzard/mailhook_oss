"""Mailbox repository interface."""

from abc import abstractmethod

from mailhookoss.domain.common.repository import Repository
from mailhookoss.domain.mailboxes.entities import Mailbox


class MailboxRepository(Repository[Mailbox]):
    """Repository interface for Mailbox aggregate."""

    @abstractmethod
    async def get_by_local_part_and_domain(
        self,
        local_part: str,
        domain_id: str,
    ) -> Mailbox | None:
        """Get mailbox by local part and domain ID.

        Args:
            local_part: Local part of email address
            domain_id: Domain ID

        Returns:
            Mailbox if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_alias_or_id(
        self,
        alias_or_id: str,
        domain_id: str,
    ) -> Mailbox | None:
        """Get mailbox by local part (alias) or ID within a domain.

        Args:
            alias_or_id: Local part or mailbox ID
            domain_id: Domain ID

        Returns:
            Mailbox if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_domain(
        self,
        domain_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Mailbox], str | None, str | None]:
        """List mailboxes for a specific domain.

        Args:
            domain_id: Domain identifier
            limit: Maximum number of mailboxes to return
            cursor: Pagination cursor
            search: Optional search query (on local_part)

        Returns:
            Tuple of (mailboxes, next_cursor, prev_cursor)
        """
        pass

    @abstractmethod
    async def list_by_tenant(
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
        pass
