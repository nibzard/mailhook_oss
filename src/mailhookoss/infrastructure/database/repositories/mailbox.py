"""Mailbox repository implementation."""

import base64
import json

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.mailboxes.entities import Mailbox
from mailhookoss.domain.mailboxes.repository import MailboxRepository
from mailhookoss.infrastructure.database.models.mailbox import MailboxModel


class MailboxRepositoryImpl(MailboxRepository):
    """SQLAlchemy implementation of MailboxRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> Mailbox | None:
        """Get mailbox by ID.

        Args:
            id: Mailbox identifier

        Returns:
            Mailbox if found, None otherwise
        """
        result = await self._session.execute(
            select(MailboxModel).where(MailboxModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_local_part_and_domain(
        self,
        local_part: str,
        domain_id: str,
    ) -> Mailbox | None:
        """Get mailbox by local part and domain ID.

        Args:
            local_part: Local part of email address
            domain_id: Domain ID

        Returns:
            Mailbox if found, None otherwise
        """
        result = await self._session.execute(
            select(MailboxModel).where(
                MailboxModel.domain_id == domain_id,
                MailboxModel.local_part == local_part,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_alias_or_id(
        self,
        alias_or_id: str,
        domain_id: str,
    ) -> Mailbox | None:
        """Get mailbox by local part (alias) or ID within a domain.

        Args:
            alias_or_id: Local part or mailbox ID
            domain_id: Domain ID

        Returns:
            Mailbox if found, None otherwise
        """
        result = await self._session.execute(
            select(MailboxModel).where(
                MailboxModel.domain_id == domain_id,
                or_(
                    MailboxModel.id == alias_or_id,
                    MailboxModel.local_part == alias_or_id,
                ),
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: Mailbox) -> Mailbox:
        """Save or update mailbox.

        Args:
            entity: Mailbox entity

        Returns:
            Saved mailbox
        """
        # Check if exists
        result = await self._session.execute(
            select(MailboxModel).where(MailboxModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.update_from_entity(entity)
            model = existing
        else:
            # Create new
            model = MailboxModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete mailbox by ID.

        Args:
            id: Mailbox identifier
        """
        result = await self._session.execute(
            select(MailboxModel).where(MailboxModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if mailbox exists.

        Args:
            id: Mailbox identifier

        Returns:
            True if mailbox exists, False otherwise
        """
        result = await self._session.execute(
            select(MailboxModel.id).where(MailboxModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_domain(
        self,
        domain_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Mailbox], str | None, str | None]:
        """List mailboxes for a specific domain.

        Args:
            domain_id: Domain identifier
            limit: Maximum number of mailboxes to return
            cursor: Pagination cursor
            search: Optional search query (on local_part)

        Returns:
            Tuple of (mailboxes, next_cursor, prev_cursor)
        """
        query = select(MailboxModel).where(
            MailboxModel.domain_id == domain_id
        ).order_by(MailboxModel.created_at.desc(), MailboxModel.id.desc())

        # Apply search filter
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(MailboxModel.local_part.ilike(search_pattern))

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(MailboxModel).where(MailboxModel.id == last_id)
                )
                last_mailbox = result.scalar_one_or_none()
                if last_mailbox:
                    query = query.where(
                        (MailboxModel.created_at < last_mailbox.created_at) |
                        ((MailboxModel.created_at == last_mailbox.created_at) & (MailboxModel.id < last_id))
                    )

        # Fetch limit + 1 to determine if there's a next page
        query = query.limit(limit + 1)
        result = await self._session.execute(query)
        models = list(result.scalars().all())

        # Check if there are more results
        has_more = len(models) > limit
        if has_more:
            models = models[:limit]

        # Convert to entities
        mailboxes = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and mailboxes:
            cursor_data = {"last_id": mailboxes[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return mailboxes, next_cursor, prev_cursor

    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Mailbox], str | None, str | None]:
        """List all mailboxes for a tenant (across all domains).

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of mailboxes to return
            cursor: Pagination cursor

        Returns:
            Tuple of (mailboxes, next_cursor, prev_cursor)
        """
        query = select(MailboxModel).where(
            MailboxModel.tenant_id == tenant_id
        ).order_by(MailboxModel.created_at.desc(), MailboxModel.id.desc())

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(MailboxModel).where(MailboxModel.id == last_id)
                )
                last_mailbox = result.scalar_one_or_none()
                if last_mailbox:
                    query = query.where(
                        (MailboxModel.created_at < last_mailbox.created_at) |
                        ((MailboxModel.created_at == last_mailbox.created_at) & (MailboxModel.id < last_id))
                    )

        # Fetch limit + 1 to determine if there's a next page
        query = query.limit(limit + 1)
        result = await self._session.execute(query)
        models = list(result.scalars().all())

        # Check if there are more results
        has_more = len(models) > limit
        if has_more:
            models = models[:limit]

        # Convert to entities
        mailboxes = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and mailboxes:
            cursor_data = {"last_id": mailboxes[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return mailboxes, next_cursor, prev_cursor
