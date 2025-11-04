"""Main API v1 router."""

from fastapi import APIRouter

from mailhookoss.api.v1 import api_keys, domains, health, mailboxes, tenants

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(domains.router)
api_router.include_router(mailboxes.router)

# TODO: Add other routers
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
# ...
