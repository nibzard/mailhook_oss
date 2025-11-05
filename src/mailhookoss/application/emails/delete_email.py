"""Delete email use case."""

from mailhookoss.domain.emails.exceptions import EmailNotFoundError
from mailhookoss.domain.emails.repository import EmailRepository


class DeleteEmailUseCase:
    """Use case for deleting an email."""

    def __init__(self, email_repository: EmailRepository) -> None:
        """Initialize use case.

        Args:
            email_repository: Email repository
        """
        self.email_repository = email_repository

    async def execute(
        self,
        tenant_id: str,
        mailbox_id: str,
        email_id: str,
    ) -> None:
        """Delete email by ID.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            email_id: Email ID

        Raises:
            EmailNotFoundError: If email not found
        """
        email = await self.email_repository.get_by_id(email_id)

        if not email or email.tenant_id != tenant_id or email.mailbox_id != mailbox_id:
            raise EmailNotFoundError(email_id)

        # Delete email
        await self.email_repository.delete(email_id)
