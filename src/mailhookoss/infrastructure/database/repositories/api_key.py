"""API Key repository implementation."""

import base64
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mailhookoss.domain.api_keys.entities import APIKey
from mailhookoss.domain.api_keys.repository import APIKeyRepository
from mailhookoss.infrastructure.database.models.api_key import APIKeyModel


class APIKeyRepositoryImpl(APIKeyRepository):
    """SQLAlchemy implementation of APIKeyRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session

    async def get_by_id(self, id: str) -> APIKey | None:
        """Get API key by ID.

        Args:
            id: API key identifier

        Returns:
            APIKey if found, None otherwise
        """
        result = await self._session.execute(
            select(APIKeyModel).where(APIKeyModel.id == id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_secret_hash(self, secret_hash: str) -> APIKey | None:
        """Get API key by secret hash.

        Args:
            secret_hash: Hashed secret

        Returns:
            APIKey if found, None otherwise
        """
        result = await self._session.execute(
            select(APIKeyModel).where(APIKeyModel.secret_hash == secret_hash)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, entity: APIKey) -> APIKey:
        """Save or update API key.

        Args:
            entity: APIKey entity

        Returns:
            Saved API key
        """
        # Check if exists
        result = await self._session.execute(
            select(APIKeyModel).where(APIKeyModel.id == entity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # For API keys, we generally don't update them
            # But if we do, we'd update relevant fields here
            model = existing
        else:
            # Create new
            model = APIKeyModel.from_entity(entity)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, id: str) -> None:
        """Delete API key by ID.

        Args:
            id: API key identifier
        """
        result = await self._session.execute(
            select(APIKeyModel).where(APIKeyModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, id: str) -> bool:
        """Check if API key exists.

        Args:
            id: API key identifier

        Returns:
            True if API key exists, False otherwise
        """
        result = await self._session.execute(
            select(APIKeyModel.id).where(APIKeyModel.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[APIKey], str | None, str | None]:
        """List API keys for a specific tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of keys to return
            cursor: Pagination cursor

        Returns:
            Tuple of (api_keys, next_cursor, prev_cursor)
        """
        query = select(APIKeyModel).where(
            APIKeyModel.tenant_id == tenant_id
        ).order_by(APIKeyModel.created_at.desc(), APIKeyModel.id.desc())

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(APIKeyModel).where(APIKeyModel.id == last_id)
                )
                last_key = result.scalar_one_or_none()
                if last_key:
                    query = query.where(
                        (APIKeyModel.created_at < last_key.created_at) |
                        ((APIKeyModel.created_at == last_key.created_at) & (APIKeyModel.id < last_id))
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
        api_keys = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and api_keys:
            cursor_data = {"last_id": api_keys[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return api_keys, next_cursor, prev_cursor

    async def list_all(
        self,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[APIKey], str | None, str | None]:
        """List all API keys (internal use only).

        Args:
            limit: Maximum number of keys to return
            cursor: Pagination cursor

        Returns:
            Tuple of (api_keys, next_cursor, prev_cursor)
        """
        query = select(APIKeyModel).order_by(APIKeyModel.created_at.desc(), APIKeyModel.id.desc())

        # Apply cursor if provided
        if cursor:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                result = await self._session.execute(
                    select(APIKeyModel).where(APIKeyModel.id == last_id)
                )
                last_key = result.scalar_one_or_none()
                if last_key:
                    query = query.where(
                        (APIKeyModel.created_at < last_key.created_at) |
                        ((APIKeyModel.created_at == last_key.created_at) & (APIKeyModel.id < last_id))
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
        api_keys = [model.to_entity() for model in models]

        # Generate next cursor
        next_cursor = None
        if has_more and api_keys:
            cursor_data = {"last_id": api_keys[-1].id}
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        prev_cursor = None
        return api_keys, next_cursor, prev_cursor
