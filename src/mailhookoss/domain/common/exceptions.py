"""Domain layer exceptions."""


class DomainException(Exception):
    """Base exception for all domain exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID '{entity_id}' not found")


class ValidationError(DomainException):
    """Raised when domain validation fails."""


class ConflictError(DomainException):
    """Raised when an operation conflicts with existing state."""


class AuthenticationError(DomainException):
    """Raised when authentication fails."""


class AuthorizationError(DomainException):
    """Raised when authorization fails."""


class InvalidOperationError(DomainException):
    """Raised when an invalid operation is attempted."""
