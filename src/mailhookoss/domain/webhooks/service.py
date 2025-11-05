"""Webhook domain service."""

import hashlib
import hmac
import json
from datetime import datetime

from mailhookoss.domain.webhooks.entities import Webhook, WebhookDelivery
from mailhookoss.domain.webhooks.exceptions import InvalidWebhookURLError
from mailhookoss.domain.webhooks.value_objects import DeliveryStatus, WebhookFilters
from mailhookoss.utils.id_generator import generate_webhook_delivery_id, generate_webhook_id


class WebhookService:
    """Domain service for webhook operations."""

    @staticmethod
    def create_webhook(
        tenant_id: str,
        url: str,
        secret: str,
        filters: WebhookFilters,
        active: bool = True,
        description: str = "",
    ) -> Webhook:
        """Create a new webhook.

        Args:
            tenant_id: Tenant ID
            url: Webhook endpoint URL
            secret: Webhook secret for signing
            filters: Event filters
            active: Whether webhook is active
            description: Optional description

        Returns:
            New Webhook entity

        Raises:
            InvalidWebhookURLError: If URL is invalid
        """
        # Validate URL
        if not url or not url.startswith(("http://", "https://")):
            raise InvalidWebhookURLError(url, "URL must start with http:// or https://")

        # Generate webhook ID
        webhook_id = generate_webhook_id()

        return Webhook(
            id=webhook_id,
            tenant_id=tenant_id,
            url=url,
            secret=secret,
            filters=filters,
            active=active,
            description=description,
        )

    @staticmethod
    def generate_webhook_secret() -> str:
        """Generate a secure webhook secret.

        Returns:
            Random webhook secret (whsec_ prefixed)
        """
        import secrets

        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Encode as base64
        import base64

        secret = base64.b64encode(random_bytes).decode("utf-8").rstrip("=")
        return f"whsec_{secret}"

    @staticmethod
    def create_delivery(
        webhook_id: str,
        tenant_id: str,
        event_type: str,
        payload: dict,
        max_attempts: int = 5,
    ) -> WebhookDelivery:
        """Create a new webhook delivery.

        Args:
            webhook_id: Webhook ID
            tenant_id: Tenant ID
            event_type: Event type
            payload: Event payload
            max_attempts: Maximum delivery attempts

        Returns:
            New WebhookDelivery entity
        """
        delivery_id = generate_webhook_delivery_id()

        return WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook_id,
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            status=DeliveryStatus.PENDING,
            attempts=0,
            max_attempts=max_attempts,
            next_attempt_at=datetime.utcnow(),
        )

    @staticmethod
    def sign_payload(
        payload: dict,
        secret: str,
        timestamp: datetime,
        webhook_id: str,
    ) -> str:
        """Sign webhook payload using Standard Webhooks format.

        Standard Webhooks uses HMAC-SHA256 signatures with format:
        v1,{base64_signature}

        Signed message format:
        {webhook_id}.{timestamp}.{json_payload}

        Args:
            payload: Event payload
            secret: Webhook secret
            timestamp: Signature timestamp
            webhook_id: Webhook ID

        Returns:
            Signature string (v1,base64signature)
        """
        # Remove whsec_ prefix if present
        if secret.startswith("whsec_"):
            secret = secret[6:]

        # Build signed message
        timestamp_str = str(int(timestamp.timestamp()))
        payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        signed_message = f"{webhook_id}.{timestamp_str}.{payload_json}"

        # Create HMAC-SHA256 signature
        signature_bytes = hmac.new(
            secret.encode("utf-8"),
            signed_message.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        # Encode as base64
        import base64

        signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

        return f"v1,{signature_b64}"

    @staticmethod
    def verify_signature(
        payload: dict,
        secret: str,
        timestamp: datetime,
        webhook_id: str,
        signature: str,
    ) -> bool:
        """Verify webhook signature.

        Args:
            payload: Event payload
            secret: Webhook secret
            timestamp: Signature timestamp
            webhook_id: Webhook ID
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        expected = WebhookService.sign_payload(payload, secret, timestamp, webhook_id)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def build_webhook_headers(
        webhook_id: str,
        signature: str,
        timestamp: datetime,
    ) -> dict[str, str]:
        """Build webhook HTTP headers.

        Following Standard Webhooks specification:
        - webhook-id: Unique webhook identifier
        - webhook-timestamp: Unix timestamp
        - webhook-signature: HMAC signature

        Args:
            webhook_id: Webhook ID
            signature: Webhook signature
            timestamp: Signature timestamp

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Content-Type": "application/json",
            "webhook-id": webhook_id,
            "webhook-timestamp": str(int(timestamp.timestamp())),
            "webhook-signature": signature,
            "User-Agent": "MailhookOSS-Webhooks/1.0",
        }

    @staticmethod
    def is_retriable_status(status_code: int) -> bool:
        """Check if HTTP status code is retriable.

        Args:
            status_code: HTTP status code

        Returns:
            True if status is retriable
        """
        # Retry on:
        # - 408 Request Timeout
        # - 429 Too Many Requests
        # - 500+ Server Errors
        # - Network errors (represented as 0 or negative)
        if status_code <= 0:
            return True
        if status_code == 408:
            return True
        if status_code == 429:
            return True
        if status_code >= 500:
            return True
        return False

    @staticmethod
    def calculate_next_attempt_delay(attempt_number: int) -> int:
        """Calculate delay in seconds for next attempt using exponential backoff.

        Standard Webhooks retry schedule:
        - Attempt 1: immediately
        - Attempt 2: 5 seconds
        - Attempt 3: 25 seconds (5^2)
        - Attempt 4: 125 seconds (5^3)
        - Attempt 5: 625 seconds (5^4)

        Args:
            attempt_number: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        if attempt_number <= 0:
            return 0

        # Exponential backoff: 5^attempt_number
        delay = 5**attempt_number
        # Cap at 1 hour
        return min(delay, 3600)

    @staticmethod
    def build_email_received_payload(
        email_id: str,
        mailbox_id: str,
        domain_id: str,
        from_addr: str,
        to_addrs: list[str],
        subject: str,
        received_at: datetime,
        labels: list[str] | None = None,
        has_attachments: bool = False,
    ) -> dict:
        """Build email.received event payload.

        Args:
            email_id: Email ID
            mailbox_id: Mailbox ID
            domain_id: Domain ID
            from_addr: From email address
            to_addrs: To email addresses
            subject: Email subject
            received_at: Received timestamp
            labels: Email labels
            has_attachments: Whether email has attachments

        Returns:
            Event payload dictionary
        """
        return {
            "event": "email.received",
            "timestamp": received_at.isoformat(),
            "data": {
                "id": email_id,
                "mailbox_id": mailbox_id,
                "domain_id": domain_id,
                "from": from_addr,
                "to": to_addrs,
                "subject": subject,
                "received_at": received_at.isoformat(),
                "labels": labels or [],
                "has_attachments": has_attachments,
            },
        }

    @staticmethod
    def build_email_sent_payload(
        email_id: str,
        mailbox_id: str,
        domain_id: str,
        from_addr: str,
        to_addrs: list[str],
        subject: str,
        sent_at: datetime,
    ) -> dict:
        """Build email.sent event payload.

        Args:
            email_id: Email ID
            mailbox_id: Mailbox ID
            domain_id: Domain ID
            from_addr: From email address
            to_addrs: To email addresses
            subject: Email subject
            sent_at: Sent timestamp

        Returns:
            Event payload dictionary
        """
        return {
            "event": "email.sent",
            "timestamp": sent_at.isoformat(),
            "data": {
                "id": email_id,
                "mailbox_id": mailbox_id,
                "domain_id": domain_id,
                "from": from_addr,
                "to": to_addrs,
                "subject": subject,
                "sent_at": sent_at.isoformat(),
            },
        }

    @staticmethod
    def build_thread_created_payload(
        thread_id: str,
        mailbox_id: str,
        subject: str,
        participants: list[str],
        message_count: int,
        created_at: datetime,
    ) -> dict:
        """Build thread.created event payload.

        Args:
            thread_id: Thread ID
            mailbox_id: Mailbox ID
            subject: Thread subject
            participants: Thread participants
            message_count: Number of messages
            created_at: Created timestamp

        Returns:
            Event payload dictionary
        """
        return {
            "event": "thread.created",
            "timestamp": created_at.isoformat(),
            "data": {
                "id": thread_id,
                "mailbox_id": mailbox_id,
                "subject": subject,
                "participants": participants,
                "message_count": message_count,
                "created_at": created_at.isoformat(),
            },
        }
