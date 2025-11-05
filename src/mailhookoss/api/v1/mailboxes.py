"""Mailbox API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.api.deps import TenantContext, get_db_session, get_tenant_context
from mailhookoss.api.pagination import PaginatedResponse
from mailhookoss.api.v1.schemas.mailbox import MailboxInput, MailboxResponse
from mailhookoss.application.mailboxes.create_mailbox import CreateMailboxUseCase
from mailhookoss.application.mailboxes.delete_mailbox import DeleteMailboxUseCase
from mailhookoss.application.mailboxes.get_mailbox import GetMailboxUseCase
from mailhookoss.application.mailboxes.list_mailboxes import ListMailboxesUseCase
from mailhookoss.application.mailboxes.update_mailbox import UpdateMailboxUseCase
from mailhookoss.infrastructure.database.repositories.domain import (
    DomainRepositoryImpl,
)
from mailhookoss.infrastructure.database.repositories.mailbox import (
    MailboxRepositoryImpl,
)

router = APIRouter(prefix="/domains", tags=["Mailboxes"])


@router.post(
    "/{domain_or_id}/mb",
    response_model=MailboxResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new mailbox",
    description="Create a new mailbox within the specified domain.",
)
async def create_mailbox(
    domain_or_id: str,
    mailbox_input: MailboxInput,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MailboxResponse:
    """Create a new mailbox."""
    mailbox_repo = MailboxRepositoryImpl(session)
    domain_repo = DomainRepositoryImpl(session)
    use_case = CreateMailboxUseCase(
        mailbox_repository=mailbox_repo,
        domain_repository=domain_repo,
    )

    mailbox = await use_case.execute(
        domain_or_id=domain_or_id,
        tenant_id=tenant_context.tenant_id,
        local_part=mailbox_input.local_part,
        active=mailbox_input.active,
        sender_name=mailbox_input.sender_name,
        spam_policy=mailbox_input.spam_policy,
        inbound_policy=mailbox_input.inbound_policy,
        filters_allow=mailbox_input.set_allow or [],
        filters_deny=mailbox_input.set_deny or [],
    )

    await session.commit()
    return MailboxResponse.model_validate(mailbox)


@router.get(
    "/{domain_or_id}/mb",
    response_model=PaginatedResponse[MailboxResponse],
    summary="List mailboxes",
    description="List all mailboxes for the specified domain with optional search and pagination.",
)
async def list_mailboxes(
    domain_or_id: str,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> PaginatedResponse[MailboxResponse]:
    """List mailboxes for a domain."""
    mailbox_repo = MailboxRepositoryImpl(session)
    domain_repo = DomainRepositoryImpl(session)
    use_case = ListMailboxesUseCase(
        mailbox_repository=mailbox_repo,
        domain_repository=domain_repo,
    )

    mailboxes, next_cursor, prev_cursor = await use_case.execute_by_domain(
        domain_or_id=domain_or_id,
        tenant_id=tenant_context.tenant_id,
        limit=limit,
        cursor=cursor,
        search=search,
    )

    return PaginatedResponse(
        data=[MailboxResponse.model_validate(m) for m in mailboxes],
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
    )


@router.get(
    "/{domain_or_id}/mb/{mailbox_alias_or_id}",
    response_model=MailboxResponse,
    summary="Get mailbox by alias or ID",
    description="Retrieve a specific mailbox by its local part (alias) or ID.",
)
async def get_mailbox(
    domain_or_id: str,
    mailbox_alias_or_id: str,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MailboxResponse:
    """Get a mailbox by alias or ID."""
    mailbox_repo = MailboxRepositoryImpl(session)
    domain_repo = DomainRepositoryImpl(session)
    use_case = GetMailboxUseCase(
        mailbox_repository=mailbox_repo,
        domain_repository=domain_repo,
    )

    mailbox = await use_case.execute(
        domain_or_id=domain_or_id,
        alias_or_id=mailbox_alias_or_id,
        tenant_id=tenant_context.tenant_id,
    )

    return MailboxResponse.model_validate(mailbox)


@router.patch(
    "/{domain_or_id}/mb/{mailbox_alias_or_id}",
    response_model=MailboxResponse,
    summary="Update mailbox",
    description="Update mailbox properties including active status, sender name, policies, and filters.",
)
async def update_mailbox(
    domain_or_id: str,
    mailbox_alias_or_id: str,
    mailbox_input: MailboxInput,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MailboxResponse:
    """Update a mailbox."""
    mailbox_repo = MailboxRepositoryImpl(session)
    domain_repo = DomainRepositoryImpl(session)
    use_case = UpdateMailboxUseCase(
        mailbox_repository=mailbox_repo,
        domain_repository=domain_repo,
    )

    mailbox = await use_case.execute(
        domain_or_id=domain_or_id,
        alias_or_id=mailbox_alias_or_id,
        tenant_id=tenant_context.tenant_id,
        active=mailbox_input.active,
        sender_name=mailbox_input.sender_name,
        spam_policy=mailbox_input.spam_policy,
        inbound_policy=mailbox_input.inbound_policy,
        add_allow=mailbox_input.add_allow,
        add_deny=mailbox_input.add_deny,
        remove_allow=mailbox_input.remove_allow,
        remove_deny=mailbox_input.remove_deny,
        set_allow=mailbox_input.set_allow,
        set_deny=mailbox_input.set_deny,
    )

    await session.commit()
    return MailboxResponse.model_validate(mailbox)


@router.delete(
    "/{domain_or_id}/mb/{mailbox_alias_or_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete mailbox",
    description="Delete a mailbox and all its associated emails. This operation cannot be undone.",
)
async def delete_mailbox(
    domain_or_id: str,
    mailbox_alias_or_id: str,
    tenant_context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Delete a mailbox."""
    mailbox_repo = MailboxRepositoryImpl(session)
    domain_repo = DomainRepositoryImpl(session)
    use_case = DeleteMailboxUseCase(
        mailbox_repository=mailbox_repo,
        domain_repository=domain_repo,
    )

    await use_case.execute(
        domain_or_id=domain_or_id,
        alias_or_id=mailbox_alias_or_id,
        tenant_id=tenant_context.tenant_id,
    )

    await session.commit()
