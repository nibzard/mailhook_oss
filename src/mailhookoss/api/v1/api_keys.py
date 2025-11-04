"""API Key endpoints."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.api.deps import (
    TenantContext,
    get_db_session,
    get_tenant_context,
    require_tenant_context,
)
from mailhookoss.api.pagination import PaginatedResponse, create_paginated_response
from mailhookoss.api.v1.schemas.api_key import (
    APIKeyInput,
    APIKeyResponse,
    APIKeyWithSecretResponse,
)
from mailhookoss.application.api_keys.create_api_key import CreateAPIKeyUseCase
from mailhookoss.application.api_keys.delete_api_key import DeleteAPIKeyUseCase
from mailhookoss.application.api_keys.list_api_keys import ListAPIKeysUseCase
from mailhookoss.infrastructure.database.repositories.api_key import (
    APIKeyRepositoryImpl,
)
from mailhookoss.infrastructure.database.repositories.tenant import (
    TenantRepositoryImpl,
)

logger = structlog.get_logger()
router = APIRouter()


def _api_key_to_response(api_key: "APIKey") -> APIKeyResponse:  # noqa: F821
    """Convert API key entity to response model.

    Args:
        api_key: APIKey entity

    Returns:
        APIKeyResponse
    """
    return APIKeyResponse(
        id=api_key.id,
        key_type=api_key.key_type.value,
        truncated_secret=api_key.truncated_secret,
        tenant_id=api_key.tenant_id,
        note=api_key.note,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


def _api_key_with_secret_to_response(
    api_key: "APIKey",  # noqa: F821
    secret: str,
) -> APIKeyWithSecretResponse:
    """Convert API key entity to response model with secret.

    Args:
        api_key: APIKey entity
        secret: Plain text secret

    Returns:
        APIKeyWithSecretResponse
    """
    return APIKeyWithSecretResponse(
        id=api_key.id,
        key_type=api_key.key_type.value,
        truncated_secret=api_key.truncated_secret,
        tenant_id=api_key.tenant_id,
        note=api_key.note,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        secret=secret,
    )


@router.post(
    "",
    response_model=APIKeyWithSecretResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an API key",
    description="Create a new API key for the authenticated tenant. "
    "The secret will be generated automatically and only shown once in the response.",
)
async def create_api_key(
    request: APIKeyInput,
    tenant_id: str = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_db_session),
) -> APIKeyWithSecretResponse:
    """Create a new API key."""
    api_key_repo = APIKeyRepositoryImpl(session)
    tenant_repo = TenantRepositoryImpl(session)
    use_case = CreateAPIKeyUseCase(api_key_repo, tenant_repo)

    api_key, secret = await use_case.execute(
        tenant_id=tenant_id,
        note=request.note,
        expires_at=request.expires_at,
    )

    logger.info(
        "api_key_created",
        api_key_id=api_key.id,
        tenant_id=tenant_id,
    )

    return _api_key_with_secret_to_response(api_key, secret)


@router.get(
    "",
    response_model=PaginatedResponse[APIKeyResponse],
    status_code=status.HTTP_200_OK,
    summary="List API keys",
    description="Get API keys visible to the caller. Tenant keys receive only their "
    "own tenant's keys, while internal keys can either impersonate a tenant via "
    "`X-Mailhook-Tenant` or, when no tenant is specified, enumerate API keys across all tenants.",
)
async def list_api_keys(
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of API keys to return (default: 50, maximum: 100)",
        ),
    ] = 50,
    cursor: Annotated[
        str | None,
        Query(description="Opaque cursor for pagination (treat as a token)"),
    ] = None,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[APIKeyResponse]:
    """List API keys."""
    api_key_repo = APIKeyRepositoryImpl(session)
    use_case = ListAPIKeysUseCase(api_key_repo)

    # If we have a tenant context, list for that tenant
    # Otherwise (internal key without tenant header), list all
    if tenant_context.tenant_id:
        api_keys, next_cursor, prev_cursor = await use_case.execute_for_tenant(
            tenant_id=tenant_context.tenant_id,
            limit=limit,
            cursor=cursor,
        )
    else:
        api_keys, next_cursor, prev_cursor = await use_case.execute_all(
            limit=limit,
            cursor=cursor,
        )

    return create_paginated_response(
        items=[_api_key_to_response(k) for k in api_keys],
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
    )


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an API key",
    description="Delete an API key by its ID or secret. You can provide either the "
    "API key ID (e.g., 'key_abc123') or the full API key secret (e.g., 'mhsec_...' "
    "for tenant keys or 'mhisec_...' for internal keys).",
)
async def delete_api_key(
    api_key_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete an API key."""
    api_key_repo = APIKeyRepositoryImpl(session)
    use_case = DeleteAPIKeyUseCase(api_key_repo)

    await use_case.execute(
        key_id_or_secret=api_key_id,
        tenant_id=tenant_context.tenant_id,
    )

    logger.info(
        "api_key_deleted",
        api_key_id=api_key_id,
        tenant_id=tenant_context.tenant_id,
    )
