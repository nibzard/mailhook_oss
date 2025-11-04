"""Email repository implementation."""

import base64
import json

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.repository import EmailRepository
from mailhookoss.infrastructure.database.models.email import EmailModel


class EmailRepositoryImpl(EmailRepository):
    """SQLAlchemy implementation of EmailRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> Email | None:
        """Get email by ID.

        Args:
            id: Email identifier

        Returns:
            Email if found, None otherwise
        """
        result = await self._session.execute(
            select(EmailModel).where(EmailModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: Email) -> Email:
        """Save or update email.

        Args:
            entity: Email entity

        Returns:
            Saved email
        """
        # Check if exists
        result = await self._session.execute(
            select(EmailModel).where(EmailModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.update_from_entity(entity)
            model = existing
        else:
            # Create new
            model = EmailModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete email by ID.

        Args:
            id: Email identifier
        """
        result = await self._session.execute(
            select(EmailModel).where(EmailModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if email exists.

        Args:
            id: Email identifier

        Returns:
            True if email exists, False otherwise
        """
        result = await self._session.execute(
            select(EmailModel.id).where(EmailModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_mailbox(
        self,
        mailbox_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
        thread_id: str | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """List emails for a specific mailbox.

        Args:
            mailbox_id: Mailbox identifier
            limit: Maximum number of emails to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by
            thread_id: Optional thread ID to filter by

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)
        """
        query = select(EmailModel).where(
            EmailModel.mailbox_id == mailbox_id
        ).order_by(EmailModel.received_at.desc(), EmailModel.id.desc())

        # Apply search filter (subject, from, to)
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(
                or_(
                    EmailModel.subject.ilike(search_pattern),
                    EmailModel.text.ilike(search_pattern),
                )
            )

        # Apply label filter
        if labels:
            # Filter emails that have ALL specified labels
            for label in labels:
                query = query.where(EmailModel.labels.contains([label]))

        # Apply thread filter
        if thread_id:
            query = query.where(EmailModel.thread_id == thread_id)

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(EmailModel).where(EmailModel.id == last_id)
                )
                last_email = result.scalar_one_or_none()
                if last_email:
                    query = query.where(
                        (EmailModel.received_at < last_email.received_at) |
                        ((EmailModel.received_at == last_email.received_at) & (EmailModel.id < last_id))
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
        emails = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and emails:
            cursor_data = {"last_id": emails[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return emails, next_cursor, prev_cursor

    async def list_by_domain(
        self,
        domain_id: str,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        labels: list[str] | None = None,
    ) -> tuple[list[Email], str | None, str | None]:
        """List emails for a specific domain (across all mailboxes).

        Args:
            domain_id: Domain identifier
            tenant_id: Tenant identifier
            limit: Maximum number of emails to return
            cursor: Pagination cursor
            search: Optional search query
            labels: Optional list of labels to filter by

        Returns:
            Tuple of (emails, next_cursor, prev_cursor)
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

        query = select(EmailModel).where(
            EmailModel.mailbox_id.in_(mailbox_ids)
        ).order_by(EmailModel.received_at.desc(), EmailModel.id.desc())

        # Apply search filter
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(
                or_(
                    EmailModel.subject.ilike(search_pattern),
                    EmailModel.text.ilike(search_pattern),
                )
            )

        # Apply label filter
        if labels:
            for label in labels:
                query = query.where(EmailModel.labels.contains([label]))

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(EmailModel).where(EmailModel.id == last_id)
                )
                last_email = result.scalar_one_or_none()
                if last_email:
                    query = query.where(
                        (EmailModel.received_at < last_email.received_at) |
                        ((EmailModel.received_at == last_email.received_at) & (EmailModel.id < last_id))
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
        emails = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and emails:
            cursor_data = {"last_id": emails[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return emails, next_cursor, prev_cursor
