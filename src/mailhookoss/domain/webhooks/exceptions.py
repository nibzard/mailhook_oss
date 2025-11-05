"""Webhook domain exceptions."""

from mailhookoss.domain.common.exceptions import DomainException


class WebhookNotFoundError(DomainException):
    """Raised when webhook is not found."""

    def __init__(self, webhook_id: str) -> None:
        """Initialize exception.

        Args:
            webhook_id: Webhook ID that was not found
        """
        super().__init__(f"Webhook not found: {webhook_id}")
        self.webhook_id = webhook_id


class WebhookAlreadyExistsError(DomainException):
    """Raised when webhook URL already exists for tenant."""

    def __init__(self, url: str) -> None:
        """Initialize exception.

        Args:
            url: Webhook URL that already exists
        """
        super().__init__(f"Webhook already exists for URL: {url}")
        self.url = url


class InvalidWebhookURLError(DomainException):
    """Raised when webhook URL is invalid."""

    def __init__(self, url: str, reason: str) -> None:
        """Initialize exception.

        Args:
            url: Invalid webhook URL
            reason: Reason why URL is invalid
        """
        super().__init__(f"Invalid webhook URL '{url}': {reason}")
        self.url = url
        self.reason = reason


class WebhookDeliveryNotFoundError(DomainException):
    """Raised when webhook delivery is not found."""

    def __init__(self, delivery_id: str) -> None:
        """Initialize exception.

        Args:
            delivery_id: Delivery ID that was not found
        """
        super().__init__(f"Webhook delivery not found: {delivery_id}")
        self.delivery_id = delivery_id


class WebhookDeliveryError(DomainException):
    """Raised when webhook delivery fails."""

    def __init__(self, webhook_id: str, error: str) -> None:
        """Initialize exception.

        Args:
            webhook_id: Webhook ID
            error: Error message
        """
        super().__init__(f"Webhook delivery failed for {webhook_id}: {error}")
        self.webhook_id = webhook_id
        self.error = error
