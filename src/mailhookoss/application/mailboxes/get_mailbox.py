"""Get mailbox use case."""

from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.domain.mailboxes.entities import Mailbox
from mailhookoss.domain.mailboxes.exceptions import MailboxNotFoundError
from mailhookoss.domain.mailboxes.repository import MailboxRepository


class GetMailboxUseCase:
    """Use case for retrieving a mailbox."""

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

    async def execute(
        self,
        domain_or_id: str,
        alias_or_id: str,
        tenant_id: str,
    ) -> Mailbox:
        """Get mailbox by local part (alias) or ID within a domain.

        Args:
            domain_or_id: Domain name or ID
            alias_or_id: Local part or mailbox ID
            tenant_id: Tenant identifier

        Returns:
            Mailbox entity

        Raises:
            DomainNotFoundError: If domain not found or doesn't belong to tenant
            MailboxNotFoundError: If mailbox not found
        """
        # Get domain and verify tenant ownership
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain or domain.tenant_id != tenant_id:
            raise DomainNotFoundError(domain_or_id)

        # Get mailbox
        mailbox = await self._mailbox_repository.get_by_alias_or_id(
            alias_or_id=alias_or_id,
            domain_id=domain.id,
        )
        if not mailbox:
            raise MailboxNotFoundError(alias_or_id)

        return mailbox
