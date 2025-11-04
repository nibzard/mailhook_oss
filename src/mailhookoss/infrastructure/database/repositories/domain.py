"""Domain repository implementation."""

import base64
import json

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.domains.entities import Domain
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.infrastructure.database.models.domain import DomainModel


class DomainRepositoryImpl(DomainRepository):
    """SQLAlchemy implementation of DomainRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> Domain | None:
        """Get domain by ID.

        Args:
            id: Domain identifier

        Returns:
            Domain if found, None otherwise
        """
        result = await self._session.execute(
            select(DomainModel).where(DomainModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_domain_name(self, domain: str) -> Domain | None:
        """Get domain by domain name.

        Args:
            domain: Domain name

        Returns:
            Domain if found, None otherwise
        """
        result = await self._session.execute(
            select(DomainModel).where(DomainModel.domain == domain)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_domain_or_id(self, domain_or_id: str) -> Domain | None:
        """Get domain by domain name or ID.

        Args:
            domain_or_id: Domain name or domain ID

        Returns:
            Domain if found, None otherwise
        """
        result = await self._session.execute(
            select(DomainModel).where(
                or_(
                    DomainModel.id == domain_or_id,
                    DomainModel.domain == domain_or_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: Domain) -> Domain:
        """Save or update domain.

        Args:
            entity: Domain entity

        Returns:
            Saved domain
        """
        # Check if exists
        result = await self._session.execute(
            select(DomainModel).where(DomainModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.update_from_entity(entity)
            model = existing
        else:
            # Create new
            model = DomainModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete domain by ID.

        Args:
            id: Domain identifier
        """
        result = await self._session.execute(
            select(DomainModel).where(DomainModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if domain exists.

        Args:
            id: Domain identifier

        Returns:
            True if domain exists, False otherwise
        """
        result = await self._session.execute(
            select(DomainModel.id).where(DomainModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Domain], str | None, str | None]:
        """List domains for a specific tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of domains to return
            cursor: Pagination cursor
            search: Optional search query

        Returns:
            Tuple of (domains, next_cursor, prev_cursor)
        """
        query = select(DomainModel).where(
            DomainModel.tenant_id == tenant_id
        ).order_by(DomainModel.created_at.desc(), DomainModel.id.desc())

        # Apply search filter
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(DomainModel.domain.ilike(search_pattern))

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(DomainModel).where(DomainModel.id == last_id)
                )
                last_domain = result.scalar_one_or_none()
                if last_domain:
                    query = query.where(
                        (DomainModel.created_at < last_domain.created_at) |
                        ((DomainModel.created_at == last_domain.created_at) & (DomainModel.id < last_id))
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
        domains = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and domains:
            cursor_data = {"last_id": domains[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return domains, next_cursor, prev_cursor
