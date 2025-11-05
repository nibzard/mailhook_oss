"""List threads use case."""

from mailhookoss.domain.emails.entities import Thread
from mailhookoss.domain.emails.repository import ThreadRepository
from mailhookoss.domain.mailboxes.repository import MailboxRepository


class ListThreadsUseCase:
    """Use case for listing threads in a mailbox."""

    def __init__(
        self,
        thread_repository: ThreadRepository,
        mailbox_repository: MailboxRepository,
    ) -> None:
        """Initialize use case.

        Args:
            thread_repository: Thread repository
            mailbox_repository: Mailbox repository
        """
        self.thread_repository = thread_repository
        self.mailbox_repository = mailbox_repository

    async def execute(
        self,
        tenant_id: str,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Thread], str | None, str | None]:
        """List threads in a mailbox.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (threads, next_cursor, prev_cursor)

        Raises:
            MailboxNotFoundError: If mailbox not found
        """
        # Verify mailbox exists and belongs to tenant
        mailbox = await self.mailbox_repository.get_by_id(mailbox_id)
        if not mailbox or mailbox.tenant_id != tenant_id:
            from mailhookoss.domain.mailboxes.exceptions import MailboxNotFoundError

            raise MailboxNotFoundError(mailbox_id)

        # List threads
        return await self.thread_repository.get_by_mailbox(
            mailbox_id=mailbox_id,
            limit=limit,
            cursor=cursor,
        )
