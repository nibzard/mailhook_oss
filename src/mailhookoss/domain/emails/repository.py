"""Email repository interfaces."""

from abc import ABC, abstractmethod

from mailhookoss.domain.emails.entities import Email, Thread


class EmailRepository(ABC):
    """Email repository interface."""

    @abstractmethod
    async def get_by_id(self, id: str) -> Email | None:
        """Get email by ID."""
        ...

    @abstractmethod
    async def save(self, entity: Email) -> Email:
        """Save or update email."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete email by ID."""
        ...

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if email exists."""
        ...

    @abstractmethod
    async def list_by_mailbox(
        self,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
        thread_id: str | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """List emails for a specific mailbox.

        Args:
            mailbox_id: Mailbox identifier
            limit: Maximum number of emails to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by
            thread_id: Optional thread ID to filter by

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)
        """
        ...

    @abstractmethod
    async def list_by_domain(
        self,
        domain_id: str,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """List emails for a specific domain (across all mailboxes).

        Args:
            domain_id: Domain identifier
            tenant_id: Tenant identifier
            limit: Maximum number of emails to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)
        """
        ...


class ThreadRepository(ABC):
    """Thread repository interface."""

    @abstractmethod
    async def get_by_id(self, id: str) -> Thread | None:
        """Get thread by ID."""
        ...

    @abstractmethod
    async def save(self, entity: Thread) -> Thread:
        """Save or update thread."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete thread by ID."""
        ...

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if thread exists."""
        ...

    @abstractmethod
    async def list_by_mailbox(
        self,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Thread], str | None, str | None]:
        """List threads for a specific mailbox.

        Args:
            mailbox_id: Mailbox identifier
            limit: Maximum number of threads to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (threads, next_cursor, prev_cursor)
        """
        ...

    @abstractmethod
    async def list_by_domain(
        self,
        domain_id: str,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Thread], str | None, str | None]:
        """List threads for a specific domain (across all mailboxes).

        Args:
            domain_id: Domain identifier
            tenant_id: Tenant identifier
            limit: Maximum number of threads to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (threads, next_cursor, prev_cursor)
        """
        ...
