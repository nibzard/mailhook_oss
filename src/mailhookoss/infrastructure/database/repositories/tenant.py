"""Tenant repository implementation."""

import base64
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.tenants.entities import Tenant
from mailhookoss.domain.tenants.repository import TenantRepository
from mailhookoss.infrastructure.database.models.tenant import TenantModel


class TenantRepositoryImpl(TenantRepository):
    """SQLAlchemy implementation of TenantRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> Tenant | None:
        """Get tenant by ID.

        Args:
            id: Tenant identifier

        Returns:
            Tenant if found, None otherwise
        """
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_name(self, name: str) -> Tenant | None:
        """Get tenant by name.

        Args:
            name: Tenant name

        Returns:
            Tenant if found, None otherwise
        """
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.name == name)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: Tenant) -> Tenant:
        """Save or update tenant.

        Args:
            entity: Tenant entity

        Returns:
            Saved tenant
        """
        # Check if exists
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.update_from_entity(entity)
            model = existing
        else:
            # Create new
            model = TenantModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete tenant by ID.

        Args:
            id: Tenant identifier
        """
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if tenant exists.

        Args:
            id: Tenant identifier

        Returns:
            True if tenant exists, False otherwise
        """
        result = await self._session.execute(
            select(TenantModel.id).where(TenantModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list(
        self,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Tenant], str | None, str | None]:
        """List tenants with pagination.

        Args:
            limit: Maximum number of tenants to return
            cursor: Pagination cursor (base64 encoded JSON with last_id)

        Returns:
            Tuple of (tenants, next_cursor, prev_cursor)
        """
        query = select(TenantModel).order_by(TenantModel.created_at.desc(), TenantModel.id.desc())

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                # Get the tenant with last_id to get its created_at
                result = await self._session.execute(
                    select(TenantModel).where(TenantModel.id == last_id)
                )
                last_tenant = result.scalar_one_or_none()
                if last_tenant:
                    query = query.where(
                        (TenantModel.created_at < last_tenant.created_at) |
                        ((TenantModel.created_at == last_tenant.created_at) & (TenantModel.id < last_id))
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
        tenants = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and tenants:
            cursor_data = {"last_id": tenants[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        # For simplicity, we don't support prev_cursor in this implementation
        prev_cursor = None

        return tenants, next_cursor, prev_cursor
