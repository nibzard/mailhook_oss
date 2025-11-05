"""Webhook domain entities."""

from datetime import datetime

from mailhookoss.domain.common.entity import AggregateRoot
from mailhookoss.domain.webhooks.value_objects import DeliveryStatus, WebhookFilters


class Webhook(AggregateRoot):
    """Webhook aggregate root."""

    def __init__(
        self,
        id: str,
        tenant_id: str,
        url: str,
        secret: str,
        filters: WebhookFilters,
        active: bool = True,
        description: str = "",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Webhook.

        Args:
            id: Webhook ID
            tenant_id: Tenant ID
            url: Webhook endpoint URL
            secret: Webhook secret for signing
            filters: Event filters
            active: Whether webhook is active
            description: Optional description
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(
            id=id,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
        )
        self._tenant_id = tenant_id
        self._url = url
        self._secret = secret
        self._filters = filters
        self._active = active
        self._description = description

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def url(self) -> str:
        """Get webhook URL."""
        return self._url

    @property
    def secret(self) -> str:
        """Get webhook secret."""
        return self._secret

    @property
    def filters(self) -> WebhookFilters:
        """Get event filters."""
        return self._filters

    @property
    def active(self) -> bool:
        """Get active status."""
        return self._active

    @property
    def description(self) -> str:
        """Get description."""
        return self._description

    def update(
        self,
        url: str | None = None,
        filters: WebhookFilters | None = None,
        active: bool | None = None,
        description: str | None = None,
    ) -> None:
        """Update webhook properties.

        Args:
            url: New URL
            filters: New filters
            active: New active status
            description: New description
        """
        if url is not None:
            self._url = url
        if filters is not None:
            self._filters = filters
        if active is not None:
            self._active = active
        if description is not None:
            self._description = description

        self.touch()

    def deactivate(self) -> None:
        """Deactivate webhook."""
        self._active = False
        self.touch()

    def activate(self) -> None:
        """Activate webhook."""
        self._active = True
        self.touch()

    def should_trigger_for_event(
        self,
        event: str,
        mailbox_id: str,
        domain_id: str,
        labels: list[str] | None = None,
        from_addr: str | None = None,
        to_addrs: list[str] | None = None,
    ) -> bool:
        """Check if webhook should trigger for an event.

        Args:
            event: Event type
            mailbox_id: Mailbox ID
            domain_id: Domain ID
            labels: Email labels
            from_addr: From address
            to_addrs: To addresses

        Returns:
            True if webhook should trigger
        """
        if not self._active:
            return False

        # Check event filter
        if not self._filters.matches_event(event):
            return False

        # Check mailbox filter
        if not self._filters.matches_mailbox(mailbox_id):
            return False

        # Check domain filter
        if not self._filters.matches_domain(domain_id):
            return False

        # Check label filter
        if labels and not self._filters.matches_labels(labels):
            return False

        # Check from pattern
        if from_addr and self._filters.from_patterns:
            if not self._filters.matches_address_pattern(from_addr, self._filters.from_patterns):
                return False

        # Check to pattern
        if to_addrs and self._filters.to_patterns:
            # Check if any recipient matches
            matches = any(
                self._filters.matches_address_pattern(addr, self._filters.to_patterns)
                for addr in to_addrs
            )
            if not matches:
                return False

        return True


class WebhookDelivery(AggregateRoot):
    """Webhook delivery aggregate root."""

    def __init__(
        self,
        id: str,
        webhook_id: str,
        tenant_id: str,
        event_type: str,
        payload: dict,
        status: DeliveryStatus = DeliveryStatus.PENDING,
        attempts: int = 0,
        max_attempts: int = 5,
        next_attempt_at: datetime | None = None,
        last_attempt_at: datetime | None = None,
        last_response_status: int | None = None,
        last_response_body: str | None = None,
        last_error: str | None = None,
        delivered_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize WebhookDelivery.

        Args:
            id: Delivery ID
            webhook_id: Webhook ID
            tenant_id: Tenant ID
            event_type: Event type
            payload: Event payload
            status: Delivery status
            attempts: Number of delivery attempts
            max_attempts: Maximum number of attempts
            next_attempt_at: Next scheduled attempt
            last_attempt_at: Last attempt timestamp
            last_response_status: Last HTTP response status
            last_response_body: Last HTTP response body
            last_error: Last error message
            delivered_at: Successful delivery timestamp
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(
            id=id,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
        )
        self._webhook_id = webhook_id
        self._tenant_id = tenant_id
        self._event_type = event_type
        self._payload = payload
        self._status = status
        self._attempts = attempts
        self._max_attempts = max_attempts
        self._next_attempt_at = next_attempt_at
        self._last_attempt_at = last_attempt_at
        self._last_response_status = last_response_status
        self._last_response_body = last_response_body
        self._last_error = last_error
        self._delivered_at = delivered_at

    @property
    def webhook_id(self) -> str:
        """Get webhook ID."""
        return self._webhook_id

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def event_type(self) -> str:
        """Get event type."""
        return self._event_type

    @property
    def payload(self) -> dict:
        """Get event payload."""
        return self._payload

    @property
    def status(self) -> DeliveryStatus:
        """Get delivery status."""
        return self._status

    @property
    def attempts(self) -> int:
        """Get number of attempts."""
        return self._attempts

    @property
    def max_attempts(self) -> int:
        """Get maximum attempts."""
        return self._max_attempts

    @property
    def next_attempt_at(self) -> datetime | None:
        """Get next attempt timestamp."""
        return self._next_attempt_at

    @property
    def last_attempt_at(self) -> datetime | None:
        """Get last attempt timestamp."""
        return self._last_attempt_at

    @property
    def last_response_status(self) -> int | None:
        """Get last response status."""
        return self._last_response_status

    @property
    def last_response_body(self) -> str | None:
        """Get last response body."""
        return self._last_response_body

    @property
    def last_error(self) -> str | None:
        """Get last error message."""
        return self._last_error

    @property
    def delivered_at(self) -> datetime | None:
        """Get delivered timestamp."""
        return self._delivered_at

    def mark_processing(self) -> None:
        """Mark delivery as processing."""
        self._status = DeliveryStatus.PROCESSING
        self.touch()

    def mark_delivered(self, response_status: int, response_body: str | None = None) -> None:
        """Mark delivery as successful.

        Args:
            response_status: HTTP response status
            response_body: HTTP response body
        """
        self._status = DeliveryStatus.DELIVERED
        self._delivered_at = datetime.utcnow()
        self._last_response_status = response_status
        self._last_response_body = response_body
        self.touch()

    def mark_failed(
        self,
        error: str,
        response_status: int | None = None,
        response_body: str | None = None,
        is_permanent: bool = False,
    ) -> None:
        """Mark delivery as failed.

        Args:
            error: Error message
            response_status: HTTP response status (if applicable)
            response_body: HTTP response body (if applicable)
            is_permanent: Whether failure is permanent (no retry)
        """
        self._attempts += 1
        self._last_attempt_at = datetime.utcnow()
        self._last_error = error
        self._last_response_status = response_status
        self._last_response_body = response_body

        if is_permanent:
            self._status = DeliveryStatus.FAILED_PERMANENT
            self._next_attempt_at = None
        elif self._attempts >= self._max_attempts:
            self._status = DeliveryStatus.EXPIRED
            self._next_attempt_at = None
        else:
            self._status = DeliveryStatus.FAILED
            # Calculate next attempt time with exponential backoff
            delay_seconds = min(2 ** self._attempts, 3600)  # Max 1 hour
            self._next_attempt_at = datetime.utcnow().replace(microsecond=0)
            self._next_attempt_at = self._next_attempt_at.replace(second=self._next_attempt_at.second + delay_seconds)

        self.touch()

    def can_retry(self) -> bool:
        """Check if delivery can be retried.

        Returns:
            True if retry is possible
        """
        return (
            self._status == DeliveryStatus.FAILED
            and self._attempts < self._max_attempts
            and self._next_attempt_at is not None
            and self._next_attempt_at <= datetime.utcnow()
        )

    def reset_for_retry(self) -> None:
        """Reset delivery for manual retry."""
        self._status = DeliveryStatus.PENDING
        self._attempts = 0
        self._next_attempt_at = datetime.utcnow()
        self._last_error = None
        self.touch()
