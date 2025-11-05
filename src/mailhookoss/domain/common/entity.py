"""Base entity class for domain models."""

from abc import ABC
from datetime import datetime


class Entity(ABC):
    """Base class for all domain entities.

    Entities have a unique identity and mutable state.
    """

    def __init__(self, id: str) -> None:
        """Initialize entity with unique identifier.

        Args:
            id: Unique identifier for the entity
        """
        self._id = id

    @property
    def id(self) -> str:
        """Get entity identifier."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """Compare entities by ID."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash entity by ID."""
        return hash(self.id)


class AggregateRoot(Entity):
    """Base class for aggregate roots.

    Aggregate roots are entities that serve as the entry point
    to an aggregate and enforce consistency boundaries.
    """

    def __init__(self, id: str, created_at: datetime, updated_at: datetime) -> None:
        """Initialize aggregate root.

        Args:
            id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id)
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def touch(self) -> None:
        """Update the updated_at timestamp to current time."""
        self._updated_at = datetime.utcnow()
