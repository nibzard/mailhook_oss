"""Domain API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.api.deps import get_db_session, get_tenant_context
from mailhookoss.api.models import TenantContext
from mailhookoss.api.v1.schemas.domain import DomainInput, DomainResponse
from mailhookoss.api.v1.schemas.pagination import PaginatedResponse
from mailhookoss.application.domains.create_domain import CreateDomainUseCase
from mailhookoss.application.domains.delete_domain import DeleteDomainUseCase
from mailhookoss.application.domains.get_domain import GetDomainUseCase
from mailhookoss.application.domains.list_domains import ListDomainsUseCase
from mailhookoss.application.domains.update_domain import UpdateDomainUseCase
from mailhookoss.infrastructure.database.repositories.domain import (
    DomainRepositoryImpl,
)
from mailhookoss.infrastructure.database.repositories.tenant import (
    TenantRepositoryImpl,
)

router = APIRouter(prefix="/domains", tags=["Domains"])


@router.post(
    "",
    response_model=DomainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new domain",
    description="Register a new domain for the authenticated tenant. The domain will be in 'pending' verification status.",
)
async def create_domain(
    domain_input: DomainInput,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DomainResponse:
    """Create a new domain."""
    domain_repo = DomainRepositoryImpl(session)
    tenant_repo = TenantRepositoryImpl(session)
    use_case = CreateDomainUseCase(
        domain_repository=domain_repo,
        tenant_repository=tenant_repo,
    )

    domain = await use_case.execute(
        tenant_id=tenant_context.tenant_id,
        domain=domain_input.domain,
        active=domain_input.active,
    )

    await session.commit()
    return DomainResponse.model_validate(domain)


@router.get(
    "",
    response_model=PaginatedResponse[DomainResponse],
    summary="List domains",
    description="List all domains for the authenticated tenant with optional search and pagination.",
)
async def list_domains(
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> PaginatedResponse[DomainResponse]:
    """List domains for the authenticated tenant."""
    domain_repo = DomainRepositoryImpl(session)
    use_case = ListDomainsUseCase(domain_repository=domain_repo)

    domains, next_cursor, prev_cursor = await use_case.execute(
        tenant_id=tenant_context.tenant_id,
        limit=limit,
        cursor=cursor,
        search=search,
    )

    return PaginatedResponse(
        data=[DomainResponse.model_validate(d) for d in domains],
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
    )


@router.get(
    "/{domain_or_id}",
    response_model=DomainResponse,
    summary="Get domain by name or ID",
    description="Retrieve a specific domain by its domain name or ID.",
)
async def get_domain(
    domain_or_id: str,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DomainResponse:
    """Get a domain by domain name or ID."""
    domain_repo = DomainRepositoryImpl(session)
    use_case = GetDomainUseCase(domain_repository=domain_repo)

    domain = await use_case.execute(
        domain_or_id=domain_or_id,
        tenant_id=tenant_context.tenant_id,
    )

    return DomainResponse.model_validate(domain)


@router.patch(
    "/{domain_or_id}",
    response_model=DomainResponse,
    summary="Update domain",
    description="Update domain properties such as active status.",
)
async def update_domain(
    domain_or_id: str,
    domain_input: DomainInput,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DomainResponse:
    """Update a domain."""
    domain_repo = DomainRepositoryImpl(session)
    use_case = UpdateDomainUseCase(domain_repository=domain_repo)

    domain = await use_case.execute(
        domain_or_id=domain_or_id,
        tenant_id=tenant_context.tenant_id,
        active=domain_input.active,
    )

    await session.commit()
    return DomainResponse.model_validate(domain)


@router.delete(
    "/{domain_or_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete domain",
    description="Delete a domain and all its associated mailboxes. This operation cannot be undone.",
)
async def delete_domain(
    domain_or_id: str,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Delete a domain."""
    domain_repo = DomainRepositoryImpl(session)
    use_case = DeleteDomainUseCase(domain_repository=domain_repo)

    await use_case.execute(
        domain_or_id=domain_or_id,
        tenant_id=tenant_context.tenant_id,
    )

    await session.commit()
