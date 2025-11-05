"""Base value object class for domain models."""

from abc import ABC


class ValueObject(ABC):
    """Base class for all value objects.

    Value objects are immutable and compared by value, not identity.
    They do not have a unique identifier.
    """

    def __eq__(self, other: object) -> bool:
        """Compare value objects by their attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash value object by its attributes."""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """String representation of value object."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
