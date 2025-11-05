"""Create webhook use case."""

from mailhookoss.domain.tenants.repository import TenantRepository
from mailhookoss.domain.webhooks.entities import Webhook
from mailhookoss.domain.webhooks.repository import WebhookRepository
from mailhookoss.domain.webhooks.service import WebhookService
from mailhookoss.domain.webhooks.value_objects import WebhookFilters


class CreateWebhookUseCase:
    """Use case for creating a webhook."""

    def __init__(
        self,
        webhook_repository: WebhookRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        """Initialize use case.

        Args:
            webhook_repository: Webhook repository
            tenant_repository: Tenant repository
        """
        self.webhook_repository = webhook_repository
        self.tenant_repository = tenant_repository

    async def execute(
        self,
        tenant_id: str,
        url: str,
        events: list[str],
        mailbox_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        labels: list[str] | None = None,
        from_patterns: list[str] | None = None,
        to_patterns: list[str] | None = None,
        active: bool = True,
        description: str = "",
    ) -> Webhook:
        """Create a new webhook.

        Args:
            tenant_id: Tenant ID
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            mailbox_ids: Optional mailbox ID filters
            domain_ids: Optional domain ID filters
            labels: Optional label filters
            from_patterns: Optional from address patterns
            to_patterns: Optional to address patterns
            active: Whether webhook is active
            description: Optional description

        Returns:
            Created Webhook entity

        Raises:
            TenantNotFoundError: If tenant not found
            InvalidWebhookURLError: If URL is invalid
        """
        # Verify tenant exists
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            from mailhookoss.domain.tenants.exceptions import TenantNotFoundError

            raise TenantNotFoundError(tenant_id)

        # Generate secret
        secret = WebhookService.generate_webhook_secret()

        # Build filters
        filters = WebhookFilters(
            events=events,
            mailbox_ids=mailbox_ids,
            domain_ids=domain_ids,
            labels=labels,
            from_patterns=from_patterns,
            to_patterns=to_patterns,
        )

        # Create webhook
        webhook = WebhookService.create_webhook(
            tenant_id=tenant_id,
            url=url,
            secret=secret,
            filters=filters,
            active=active,
            description=description,
        )

        # Save
        await self.webhook_repository.save(webhook)

        return webhook
