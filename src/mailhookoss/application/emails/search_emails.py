"""Search emails use case."""

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.repository import EmailRepository
from mailhookoss.domain.emails.search import EmailSearchService
from mailhookoss.domain.mailboxes.repository import MailboxRepository


class SearchEmailsUseCase:
    """Use case for searching emails with query language."""

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
        query: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """Search emails with query language.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            query: Search query
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)

        Raises:
            MailboxNotFoundError: If mailbox not found
            ValidationError: If query is invalid
        """
        # Verify mailbox exists and belongs to tenant
        mailbox = await self.mailbox_repository.get_by_id(mailbox_id)
        if not mailbox or mailbox.tenant_id != tenant_id:
            from mailhookoss.domain.mailboxes.exceptions import MailboxNotFoundError

            raise MailboxNotFoundError(mailbox_id)

        # Validate query
        is_valid, error = EmailSearchService.validate_query(query)
        if not is_valid:
            from mailhookoss.domain.common.exceptions import ValidationError

            raise ValidationError(f"Invalid search query: {error}")

        # Parse query
        parsed_query = EmailSearchService.parse_query(query)

        # Build filters
        filters = EmailSearchService.build_sql_filters(parsed_query)

        # Search emails
        return await self.email_repository.search(
            mailbox_id=mailbox_id,
            filters=filters,
            limit=limit,
            cursor=cursor,
        )
