"""List webhooks use case."""

from mailhookoss.domain.webhooks.entities import Webhook
from mailhookoss.domain.webhooks.repository import WebhookRepository


class ListWebhooksUseCase:
    """Use case for listing webhooks."""

    def __init__(self, webhook_repository: WebhookRepository) -> None:
        """Initialize use case.

        Args:
            webhook_repository: Webhook repository
        """
        self.webhook_repository = webhook_repository

    async def execute(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Webhook], str | None, str | None]:
        """List webhooks for a tenant.

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (webhooks, next_cursor, prev_cursor)
        """
        return await self.webhook_repository.get_by_tenant(
            tenant_id=tenant_id,
            limit=limit,
            cursor=cursor,
        )
