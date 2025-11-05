"""Update email use case."""

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.exceptions import EmailNotFoundError
from mailhookoss.domain.emails.repository import EmailRepository


class UpdateEmailUseCase:
    """Use case for updating email metadata."""

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
        labels: list[str] | None = None,
        custom_summary: str | None = None,
        user_data: dict | None = None,
    ) -> Email:
        """Update email metadata.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            email_id: Email ID
            labels: New labels (replaces existing)
            custom_summary: New custom summary
            user_data: New user data (merges with existing)

        Returns:
            Updated Email entity

        Raises:
            EmailNotFoundError: If email not found
        """
        email = await self.email_repository.get_by_id(email_id)

        if not email or email.tenant_id != tenant_id or email.mailbox_id != mailbox_id:
            raise EmailNotFoundError(email_id)

        # Update email
        email.update_metadata(
            labels=labels,
            custom_summary=custom_summary,
            user_data=user_data,
        )

        # Save
        await self.email_repository.save(email)

        return email
