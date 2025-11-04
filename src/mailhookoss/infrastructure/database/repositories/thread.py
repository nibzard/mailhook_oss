"""Thread repository implementation."""

import base64
import json

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.emails.entities import Thread
from mailhookoss.domain.emails.repository import ThreadRepository
from mailhookoss.infrastructure.database.models.email import ThreadModel


class ThreadRepositoryImpl(ThreadRepository):
    """SQLAlchemy implementation of ThreadRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> Thread | None:
        """Get thread by ID.

        Args:
            id: Thread identifier

        Returns:
            Thread if found, None otherwise
        """
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: Thread) -> Thread:
        """Save or update thread.

        Args:
            entity: Thread entity

        Returns:
            Saved thread
        """
        # Check if exists
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.update_from_entity(entity)
            model = existing
        else:
            # Create new
            model = ThreadModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete thread by ID.

        Args:
            id: Thread identifier
        """
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if thread exists.

        Args:
            id: Thread identifier

        Returns:
            True if thread exists, False otherwise
        """
        result = await self._session.execute(
            select(ThreadModel.id).where(ThreadModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_mailbox(
        self,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Thread], str | None, str | None]:
        """List threads for a specific mailbox.

        Args:
            mailbox_id: Mailbox identifier
            limit: Maximum number of threads to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (threads, next_cursor, prev_cursor)
        """
        query = select(ThreadModel).where(
            ThreadModel.mailbox_id == mailbox_id
        ).order_by(ThreadModel.last_message_at.desc(), ThreadModel.id.desc())

        # Apply search filter (subject)
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(ThreadModel.subject.ilike(search_pattern))

        # Apply label filter
        if labels:
            # Filter threads that have ALL specified labels
            for label in labels:
                query = query.where(ThreadModel.labels.contains([label]))

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(ThreadModel).where(ThreadModel.id == last_id)
                )
                last_thread = result.scalar_one_or_none()
                if last_thread:
                    query = query.where(
                        (ThreadModel.last_message_at < last_thread.last_message_at) |
                        ((ThreadModel.last_message_at == last_thread.last_message_at) & (ThreadModel.id < last_id))
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
        threads = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and threads:
            cursor_data = {"last_id": threads[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return threads, next_cursor, prev_cursor

    async def list_by_domain(
        self,
        domain_id: str,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Thread], str | None, str | None]:
        """List threads for a specific domain (across all mailboxes).

        Args:
            domain_id: Domain identifier
            tenant_id: Tenant identifier
            limit: Maximum number of threads to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (threads, next_cursor, prev_cursor)
        """
        # Import here to avoid circular dependency
        from mailhookoss.infrastructure.database.models.mailbox import MailboxModel

        # Get all mailbox IDs for this domain
        result = await self._session.execute(
            select(MailboxModel.id).where(
                and_(
                    MailboxModel.domain_id == domain_id,
                    MailboxModel.tenant_id == tenant_id,
                )
            )
        )
        mailbox_ids = [row[0] for row in result.all()]

        if not mailbox_ids:
            return [], None, None

        query = select(ThreadModel).where(
            ThreadModel.mailbox_id.in_(mailbox_ids)
        ).order_by(ThreadModel.last_message_at.desc(), ThreadModel.id.desc())

        # Apply search filter
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(ThreadModel.subject.ilike(search_pattern))

        # Apply label filter
        if labels:
            for label in labels:
                query = query.where(ThreadModel.labels.contains([label]))

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(ThreadModel).where(ThreadModel.id == last_id)
                )
                last_thread = result.scalar_one_or_none()
                if last_thread:
                    query = query.where(
                        (ThreadModel.last_message_at < last_thread.last_message_at) |
                        ((ThreadModel.last_message_at == last_thread.last_message_at) & (ThreadModel.id < last_id))
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
        threads = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and threads:
            cursor_data = {"last_id": threads[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return threads, next_cursor, prev_cursor
