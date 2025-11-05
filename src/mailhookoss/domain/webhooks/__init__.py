"""Webhook domain module."""

from mailhookoss.domain.webhooks.entities import Webhook, WebhookDelivery
from mailhookoss.domain.webhooks.exceptions import (
    InvalidWebhookURLError,
    WebhookAlreadyExistsError,
    WebhookDeliveryError,
    WebhookDeliveryNotFoundError,
    WebhookNotFoundError,
)
from mailhookoss.domain.webhooks.repository import WebhookDeliveryRepository, WebhookRepository
from mailhookoss.domain.webhooks.service import WebhookService
from mailhookoss.domain.webhooks.value_objects import DeliveryStatus, WebhookEvent, WebhookFilters

__all__ = [
    "Webhook",
    "WebhookDelivery",
    "WebhookRepository",
    "WebhookDeliveryRepository",
    "WebhookService",
    "WebhookEvent",
    "WebhookFilters",
    "DeliveryStatus",
    "WebhookNotFoundError",
    "WebhookAlreadyExistsError",
    "InvalidWebhookURLError",
    "WebhookDeliveryNotFoundError",
    "WebhookDeliveryError",
]
