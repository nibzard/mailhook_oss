"""FastAPI dependencies."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Annotated

import structlog
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.api_keys.exceptions import (
    APIKeyExpiredError,
    InvalidAPIKeyError,
)
from mailhookoss.domain.api_keys.service import APIKeyService
from mailhookoss.domain.common.exceptions import AuthenticationError, AuthorizationError
from mailhookoss.infrastructure.database.repositories.api_key import (
    APIKeyRepositoryImpl,
)
from mailhookoss.infrastructure.database.session import get_session

logger = structlog.get_logger()


@dataclass
class TenantContext:
    """Context for authenticated tenant."""

    tenant_id: str | None
    is_internal: bool
    api_key_id: str


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session
    """
    async for session in get_session():
        yield session


async def get_current_api_key(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db_session),
) -> TenantContext:
    """Extract and validate API key from Authorization header.

    Args:
        authorization: Authorization header (Bearer token)
        session: Database session

    Returns:
        TenantContext with authenticated tenant information

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        logger.warning("missing_authorization_header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("invalid_authorization_format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret = parts[1]

    # Hash the secret to look it up
    secret_hash = APIKeyService.hash_secret(secret)

    # Look up API key
    api_key_repo = APIKeyRepositoryImpl(session)
    api_key = await api_key_repo.get_by_secret_hash(secret_hash)

    if not api_key:
        logger.warning("invalid_api_key", secret_prefix=secret[:12])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if expired
    if api_key.is_expired():
        logger.warning("api_key_expired", api_key_id=api_key.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tenant context
    context = TenantContext(
        tenant_id=api_key.tenant_id,
        is_internal=api_key.is_internal(),
        api_key_id=api_key.id,
    )

    logger.info(
        "api_key_authenticated",
        api_key_id=api_key.id,
        tenant_id=context.tenant_id,
        is_internal=context.is_internal,
    )

    return context


async def get_tenant_context(
    tenant_context: TenantContext = Depends(get_current_api_key),
    x_mailhook_tenant: Annotated[str | None, Header()] = None,
) -> TenantContext:
    """Get tenant context with support for internal key impersonation.

    Args:
        tenant_context: Base tenant context from API key
        x_mailhook_tenant: Optional tenant ID for internal key impersonation

    Returns:
        TenantContext with resolved tenant ID

    Raises:
        HTTPException: If impersonation is not allowed
    """
    # If internal key and X-Mailhook-Tenant header is provided, use it
    if tenant_context.is_internal and x_mailhook_tenant:
        logger.info(
            "internal_key_impersonating_tenant",
            api_key_id=tenant_context.api_key_id,
            impersonated_tenant_id=x_mailhook_tenant,
        )
        return TenantContext(
            tenant_id=x_mailhook_tenant,
            is_internal=True,
            api_key_id=tenant_context.api_key_id,
        )

    # If tenant key, must have tenant_id
    if not tenant_context.is_internal and not tenant_context.tenant_id:
        logger.error(
            "tenant_key_without_tenant_id",
            api_key_id=tenant_context.api_key_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid tenant key configuration",
        )

    return tenant_context


async def require_tenant_context(
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> str:
    """Require a tenant context (tenant_id must be present).

    Args:
        tenant_context: Tenant context

    Returns:
        Tenant ID

    Raises:
        HTTPException: If no tenant context available
    """
    if not tenant_context.tenant_id:
        logger.warning(
            "missing_tenant_context",
            api_key_id=tenant_context.api_key_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required. Internal keys must provide X-Mailhook-Tenant header.",
        )

    return tenant_context.tenant_id


async def require_internal_key(
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    """Require an internal API key.

    Args:
        tenant_context: Tenant context

    Returns:
        TenantContext

    Raises:
        HTTPException: If not an internal key
    """
    if not tenant_context.is_internal:
        logger.warning(
            "internal_key_required",
            api_key_id=tenant_context.api_key_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires an internal API key",
        )

    return tenant_context
