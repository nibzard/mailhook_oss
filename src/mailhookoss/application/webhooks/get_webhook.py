"""Get webhook use case."""

from mailhookoss.domain.webhooks.entities import Webhook
from mailhookoss.domain.webhooks.exceptions import WebhookNotFoundError
from mailhookoss.domain.webhooks.repository import WebhookRepository


class GetWebhookUseCase:
    """Use case for getting a single webhook."""

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
    ) -> Webhook:
        """Get webhook by ID.

        Args:
            tenant_id: Tenant ID
            webhook_id: Webhook ID

        Returns:
            Webhook entity

        Raises:
            WebhookNotFoundError: If webhook not found
        """
        webhook = await self.webhook_repository.get_by_id(webhook_id)

        if not webhook or webhook.tenant_id != tenant_id:
            raise WebhookNotFoundError(webhook_id)

        return webhook
