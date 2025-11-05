"""Update thread use case."""

from mailhookoss.domain.emails.entities import Thread
from mailhookoss.domain.emails.repository import ThreadRepository


class UpdateThreadUseCase:
    """Use case for updating thread metadata."""

    def __init__(self, thread_repository: ThreadRepository) -> None:
        """Initialize use case.

        Args:
            thread_repository: Thread repository
        """
        self.thread_repository = thread_repository

    async def execute(
        self,
        tenant_id: str,
        mailbox_id: str,
        thread_id: str,
        labels: list[str] | None = None,
    ) -> Thread:
        """Update thread metadata.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            thread_id: Thread ID
            labels: New labels (replaces existing)

        Returns:
            Updated Thread entity

        Raises:
            ThreadNotFoundError: If thread not found
        """
        thread = await self.thread_repository.get_by_id(thread_id)

        if not thread or thread.tenant_id != tenant_id or thread.mailbox_id != mailbox_id:
            from mailhookoss.domain.emails.exceptions import ThreadNotFoundError

            raise ThreadNotFoundError(thread_id)

        # Update thread labels
        if labels is not None:
            thread.update_metadata(labels=labels)

        # Save
        await self.thread_repository.save(thread)

        return thread
