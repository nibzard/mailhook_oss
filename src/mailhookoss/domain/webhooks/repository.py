"""Webhook repository interfaces."""

from abc import abstractmethod

from mailhookoss.domain.common.repository import Repository
from mailhookoss.domain.webhooks.entities import Webhook, WebhookDelivery
from mailhookoss.domain.webhooks.value_objects import DeliveryStatus


class WebhookRepository(Repository[Webhook]):
    """Repository interface for Webhook aggregate."""

    @abstractmethod
    async def get_by_id(self, id: str) -> Webhook | None:
        """Get webhook by ID.

        Args:
            id: Webhook ID

        Returns:
            Webhook entity or None if not found
        """
        ...

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Webhook], str | None, str | None]:
        """Get webhooks for a tenant with pagination.

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (webhooks, next_cursor, prev_cursor)
        """
        ...

    @abstractmethod
    async def get_active_by_tenant(self, tenant_id: str) -> list[Webhook]:
        """Get all active webhooks for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of active Webhook entities
        """
        ...

    @abstractmethod
    async def save(self, webhook: Webhook) -> None:
        """Save webhook.

        Args:
            webhook: Webhook entity to save
        """
        ...

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete webhook by ID.

        Args:
            id: Webhook ID
        """
        ...

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if webhook exists.

        Args:
            id: Webhook ID

        Returns:
            True if webhook exists
        """
        ...


class WebhookDeliveryRepository(Repository[WebhookDelivery]):
    """Repository interface for WebhookDelivery aggregate."""

    @abstractmethod
    async def get_by_id(self, id: str) -> WebhookDelivery | None:
        """Get delivery by ID.

        Args:
            id: Delivery ID

        Returns:
            WebhookDelivery entity or None if not found
        """
        ...

    @abstractmethod
    async def get_by_webhook(
        self,
        webhook_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[WebhookDelivery], str | None, str | None]:
        """Get deliveries for a webhook with pagination.

        Args:
            webhook_id: Webhook ID
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            Tuple of (deliveries, next_cursor, prev_cursor)
        """
        ...

    @abstractmethod
    async def get_pending_deliveries(
        self,
        limit: int = 100,
    ) -> list[WebhookDelivery]:
        """Get pending deliveries ready for processing.

        Args:
            limit: Maximum number of results

        Returns:
            List of pending WebhookDelivery entities
        """
        ...

    @abstractmethod
    async def get_failed_deliveries_for_retry(
        self,
        limit: int = 100,
    ) -> list[WebhookDelivery]:
        """Get failed deliveries ready for retry.

        Args:
            limit: Maximum number of results

        Returns:
            List of failed WebhookDelivery entities ready for retry
        """
        ...

    @abstractmethod
    async def save(self, delivery: WebhookDelivery) -> None:
        """Save webhook delivery.

        Args:
            delivery: WebhookDelivery entity to save
        """
        ...

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete delivery by ID.

        Args:
            id: Delivery ID
        """
        ...

    @abstractmethod
    async def delete_old_deliveries(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> int:
        """Delete old deliveries for a tenant.

        Args:
            tenant_id: Tenant ID
            days: Age threshold in days

        Returns:
            Number of deliveries deleted
        """
        ...

    @abstractmethod
    async def get_delivery_stats(
        self,
        webhook_id: str,
    ) -> dict:
        """Get delivery statistics for a webhook.

        Args:
            webhook_id: Webhook ID

        Returns:
            Dictionary with delivery stats
        """
        ...
