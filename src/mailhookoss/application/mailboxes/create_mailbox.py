"""Create mailbox use case."""

from datetime import UTC, datetime

from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.domain.mailboxes.entities import Mailbox
from mailhookoss.domain.mailboxes.exceptions import MailboxAlreadyExistsError
from mailhookoss.domain.mailboxes.repository import MailboxRepository
from mailhookoss.domain.mailboxes.value_objects import (
    InboundPolicy,
    MailboxFilters,
    SpamPolicy,
)
from mailhookoss.utils.id_generator import generate_mailbox_id


class CreateMailboxUseCase:
    """Use case for creating a new mailbox."""

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
        tenant_id: str,
        local_part: str,
        active: bool = True,
        sender_name: str = "",
        spam_policy: SpamPolicy = SpamPolicy.MARK,
        inbound_policy: InboundPolicy = InboundPolicy.THREAD_TRUST,
        filters_allow: list[str] | None = None,
        filters_deny: list[str] | None = None,
    ) -> Mailbox:
        """Create a new mailbox.

        Args:
            domain_or_id: Domain name or ID
            tenant_id: Tenant identifier
            local_part: Local part of email address
            active: Whether mailbox is active
            sender_name: Display name for sending emails
            spam_policy: Spam handling policy
            inbound_policy: Inbound participant trust policy
            filters_allow: Initial allow list (whitelist)
            filters_deny: Initial deny list (blacklist)

        Returns:
            Created mailbox

        Raises:
            DomainNotFoundError: If domain not found or doesn't belong to tenant
            MailboxAlreadyExistsError: If mailbox already exists
            InvalidLocalPartError: If local part is invalid
        """
        # Get domain and verify tenant ownership
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain or domain.tenant_id != tenant_id:
            raise DomainNotFoundError(domain_or_id)

        # Check if mailbox already exists
        existing = await self._mailbox_repository.get_by_local_part_and_domain(
            local_part=local_part,
            domain_id=domain.id,
        )
        if existing:
            raise MailboxAlreadyExistsError(local_part, domain.domain)

        # Create new mailbox
        now = datetime.now(UTC)
        filters = MailboxFilters(
            allow=filters_allow or [],
            deny=filters_deny or [],
        )
        mailbox = Mailbox(
            id=generate_mailbox_id(),
            tenant_id=domain.tenant_id,
            domain_id=domain.id,
            local_part=local_part,
            active=active,
            sender_name=sender_name,
            spam_policy=spam_policy,
            inbound_policy=inbound_policy,
            filters=filters,
            created_at=now,
            updated_at=now,
        )

        # Save mailbox
        return await self._mailbox_repository.save(mailbox)
