"""List emails use case."""

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.repository import EmailRepository
from mailhookoss.domain.mailboxes.repository import MailboxRepository


class ListEmailsUseCase:
    """Use case for listing emails in a mailbox."""

    def __init__(
        self,
        email_repository: EmailRepository,
        mailbox_repository: MailboxRepository,
    ) -> None:
        """Initialize use case.

        Args:
            email_repository: Email repository
            mailbox_repository: Mailbox repository
        """
        self.email_repository = email_repository
        self.mailbox_repository = mailbox_repository

    async def execute(
        self,
        tenant_id: str,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """List emails in a mailbox.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)

        Raises:
            MailboxNotFoundError: If mailbox not found
        """
        # Verify mailbox exists and belongs to tenant
        mailbox = await self.mailbox_repository.get_by_id(mailbox_id)
        if not mailbox or mailbox.tenant_id != tenant_id:
            from mailhookoss.domain.mailboxes.exceptions import MailboxNotFoundError

            raise MailboxNotFoundError(mailbox_id)

        # List emails
        return await self.email_repository.get_by_mailbox(
            mailbox_id=mailbox_id,
            limit=limit,
            cursor=cursor,
        )
