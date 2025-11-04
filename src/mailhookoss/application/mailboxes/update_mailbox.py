"""Update mailbox use case."""

from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.domain.mailboxes.entities import Mailbox
from mailhookoss.domain.mailboxes.exceptions import MailboxNotFoundError
from mailhookoss.domain.mailboxes.repository import MailboxRepository
from mailhookoss.domain.mailboxes.value_objects import (
    InboundPolicy,
    MailboxFilters,
    SpamPolicy,
)


class UpdateMailboxUseCase:
    """Use case for updating a mailbox."""

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
        active: bool | None = None,
        sender_name: str | None = None,
        spam_policy: str | None = None,
        inbound_policy: str | None = None,
        add_allow: list[str] | None = None,
        add_deny: list[str] | None = None,
        remove_allow: list[str] | None = None,
        remove_deny: list[str] | None = None,
        set_allow: list[str] | None = None,
        set_deny: list[str] | None = None,
    ) -> Mailbox:
        """Update mailbox.

        Args:
            domain_or_id: Domain name or ID
            alias_or_id: Local part or mailbox ID
            tenant_id: Tenant identifier
            active: Whether mailbox is active (None = no change)
            sender_name: Display name (None = no change)
            spam_policy: Spam policy (None = no change)
            inbound_policy: Inbound policy (None = no change)
            add_allow: Email addresses to add to allow list
            add_deny: Email addresses to add to deny list
            remove_allow: Email addresses to remove from allow list
            remove_deny: Email addresses to remove from deny list
            set_allow: Replace entire allow list (None = no change)
            set_deny: Replace entire deny list (None = no change)

        Returns:
            Updated mailbox

        Raises:
            DomainNotFoundError: If domain not found or doesn't belong to tenant
            MailboxNotFoundError: If mailbox not found
        """
        # Get domain and verify tenant ownership
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain or domain.tenant_id != tenant_id:
            raise DomainNotFoundError(domain_or_id)

        # Get existing mailbox
        mailbox = await self._mailbox_repository.get_by_alias_or_id(
            alias_or_id=alias_or_id,
            domain_id=domain.id,
        )
        if not mailbox:
            raise MailboxNotFoundError(alias_or_id)

        # Update fields if provided
        if active is not None:
            if active:
                mailbox.activate()
            else:
                mailbox.deactivate()

        if sender_name is not None:
            mailbox.update_sender_name(sender_name)

        if spam_policy is not None:
            mailbox.update_spam_policy(SpamPolicy(spam_policy))

        if inbound_policy is not None:
            mailbox.update_inbound_policy(InboundPolicy(inbound_policy))

        # Handle filter updates
        current_filters = mailbox.filters
        new_allow = list(current_filters.allow)
        new_deny = list(current_filters.deny)

        # Apply set operations (replace entire list)
        if set_allow is not None:
            new_allow = set_allow
        if set_deny is not None:
            new_deny = set_deny

        # Apply add operations
        if add_allow:
            for email in add_allow:
                if email.lower() not in [e.lower() for e in new_allow]:
                    new_allow.append(email)
        if add_deny:
            for email in add_deny:
                if email.lower() not in [e.lower() for e in new_deny]:
                    new_deny.append(email)

        # Apply remove operations
        if remove_allow:
            new_allow = [e for e in new_allow if e.lower() not in [r.lower() for r in remove_allow]]
        if remove_deny:
            new_deny = [e for e in new_deny if e.lower() not in [r.lower() for r in remove_deny]]

        # Update filters if any changes were made
        if (set_allow is not None or set_deny is not None or
            add_allow or add_deny or remove_allow or remove_deny):
            updated_filters = MailboxFilters(allow=new_allow, deny=new_deny)
            mailbox.update_filters(updated_filters)

        # Save updated mailbox
        return await self._mailbox_repository.save(mailbox)
