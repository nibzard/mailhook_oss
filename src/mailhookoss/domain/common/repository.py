"""Repository interfaces for domain models."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from mailhookoss.domain.common.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    """Base repository interface.

    Repositories provide persistence abstraction for domain entities.
    """

    @abstractmethod
    async def get_by_id(self, id: str) -> T | None:
        """Get entity by ID.

        Args:
            id: Entity identifier

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save or update entity.

        Args:
            entity: Entity to save

        Returns:
            Saved entity
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete entity by ID.

        Args:
            id: Entity identifier
        """
        pass

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if entity exists.

        Args:
            id: Entity identifier

        Returns:
            True if entity exists, False otherwise
        """
        pass
