"""Update webhook use case."""

from mailhookoss.domain.webhooks.entities import Webhook
from mailhookoss.domain.webhooks.exceptions import WebhookNotFoundError
from mailhookoss.domain.webhooks.repository import WebhookRepository
from mailhookoss.domain.webhooks.value_objects import WebhookFilters


class UpdateWebhookUseCase:
    """Use case for updating a webhook."""

    def __init__(self, webhook_repository: WebhookRepository) -> None:
        """Initialize use case.

        Args:
            webhook_repository: Webhook repository
        """
        self.webhook_repository = webhook_repository

    async def execute(
        self,
        tenant_id: str,
        webhook_id: str,
        url: str | None = None,
        events: list[str] | None = None,
        mailbox_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        labels: list[str] | None = None,
        from_patterns: list[str] | None = None,
        to_patterns: list[str] | None = None,
        active: bool | None = None,
        description: str | None = None,
    ) -> Webhook:
        """Update webhook.

        Args:
            tenant_id: Tenant ID
            webhook_id: Webhook ID
            url: New URL
            events: New event list
            mailbox_ids: New mailbox filters
            domain_ids: New domain filters
            labels: New label filters
            from_patterns: New from patterns
            to_patterns: New to patterns
            active: New active status
            description: New description

        Returns:
            Updated Webhook entity

        Raises:
            WebhookNotFoundError: If webhook not found
        """
        webhook = await self.webhook_repository.get_by_id(webhook_id)

        if not webhook or webhook.tenant_id != tenant_id:
            raise WebhookNotFoundError(webhook_id)

        # Build new filters if any filter field is provided
        filters = None
        if any([events, mailbox_ids, domain_ids, labels, from_patterns, to_patterns]):
            filters = WebhookFilters(
                events=events if events is not None else webhook.filters.events,
                mailbox_ids=mailbox_ids if mailbox_ids is not None else webhook.filters.mailbox_ids,
                domain_ids=domain_ids if domain_ids is not None else webhook.filters.domain_ids,
                labels=labels if labels is not None else webhook.filters.labels,
                from_patterns=from_patterns if from_patterns is not None else webhook.filters.from_patterns,
                to_patterns=to_patterns if to_patterns is not None else webhook.filters.to_patterns,
            )

        # Update webhook
        webhook.update(
            url=url,
            filters=filters,
            active=active,
            description=description,
        )

        # Save
        await self.webhook_repository.save(webhook)

        return webhook
