"""Main API v1 router."""

from fastapi import APIRouter

from mailhookoss.api.v1 import health

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, tags=["health"])

# TODO: Add other routers
# api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
# api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
# ...
