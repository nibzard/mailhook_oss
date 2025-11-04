"""Tenant API endpoints."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.api.deps import (
    TenantContext,
    get_db_session,
    require_internal_key,
    require_tenant_context,
)
from mailhookoss.api.pagination import PaginatedResponse, create_paginated_response
from mailhookoss.api.v1.schemas.tenant import (
    TenantCreateRequest,
    TenantResponse,
    TenantUpdateRequest,
)
from mailhookoss.application.tenants.create_tenant import CreateTenantUseCase
from mailhookoss.application.tenants.get_tenant import GetTenantUseCase
from mailhookoss.application.tenants.list_tenants import ListTenantsUseCase
from mailhookoss.application.tenants.update_tenant import UpdateTenantUseCase
from mailhookoss.infrastructure.database.repositories.tenant import (
    TenantRepositoryImpl,
)

logger = structlog.get_logger()
router = APIRouter()


def _tenant_to_response(tenant: "Tenant") -> TenantResponse:  # noqa: F821
    """Convert tenant entity to response model.

    Args:
        tenant: Tenant entity

    Returns:
        TenantResponse
    """
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tenant",
    description="Create a new tenant. Internal API keys only.",
)
async def create_tenant(
    request: TenantCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: TenantContext = Depends(require_internal_key),
) -> TenantResponse:
    """Create a new tenant (internal keys only)."""
    tenant_repo = TenantRepositoryImpl(session)
    use_case = CreateTenantUseCase(tenant_repo)

    tenant = await use_case.execute(name=request.name)

    logger.info("tenant_created", tenant_id=tenant.id, name=tenant.name)

    return _tenant_to_response(tenant)


@router.get(
    "",
    response_model=PaginatedResponse[TenantResponse],
    status_code=status.HTTP_200_OK,
    summary="List tenants",
    description="List tenants with cursor-based pagination. Internal API keys only.",
)
async def list_tenants(
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of tenants to return (default: 50, maximum: 100)",
        ),
    ] = 50,
    cursor: Annotated[
        str | None,
        Query(description="Opaque cursor for pagination (treat as a token)"),
    ] = None,
    session: AsyncSession = Depends(get_db_session),
    _: TenantContext = Depends(require_internal_key),
) -> PaginatedResponse[TenantResponse]:
    """List all tenants (internal keys only)."""
    tenant_repo = TenantRepositoryImpl(session)
    use_case = ListTenantsUseCase(tenant_repo)

    tenants, next_cursor, prev_cursor = await use_case.execute(
        limit=limit,
        cursor=cursor,
    )

    return create_paginated_response(
        items=[_tenant_to_response(t) for t in tenants],
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
    )


@router.get(
    "/current",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current tenant",
    description="Get information about the current tenant associated with the API key",
)
async def get_current_tenant(
    tenant_id: str = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_db_session),
) -> TenantResponse:
    """Get current tenant (requires tenant context)."""
    tenant_repo = TenantRepositoryImpl(session)
    use_case = GetTenantUseCase(tenant_repo)

    tenant = await use_case.execute(tenant_id=tenant_id)

    return _tenant_to_response(tenant)


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tenant",
    description="Retrieve a tenant by its identifier. Internal API keys only.",
)
async def get_tenant(
    tenant_id: str,
    session: AsyncSession = Depends(get_db_session),
    _: TenantContext = Depends(require_internal_key),
) -> TenantResponse:
    """Get tenant by ID (internal keys only)."""
    tenant_repo = TenantRepositoryImpl(session)
    use_case = GetTenantUseCase(tenant_repo)

    tenant = await use_case.execute(tenant_id=tenant_id)

    return _tenant_to_response(tenant)


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update tenant",
    description="Update attributes for a tenant. Internal API keys only.",
)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: TenantContext = Depends(require_internal_key),
) -> TenantResponse:
    """Update tenant (internal keys only)."""
    tenant_repo = TenantRepositoryImpl(session)
    use_case = UpdateTenantUseCase(tenant_repo)

    tenant = await use_case.execute(tenant_id=tenant_id, name=request.name)

    logger.info("tenant_updated", tenant_id=tenant.id, name=tenant.name)

    return _tenant_to_response(tenant)
