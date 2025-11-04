"""API Key domain exceptions."""

from mailhookoss.domain.common.exceptions import AuthenticationError, DomainException


class APIKeyError(DomainException):
    """Base exception for API key-related errors."""

    pass


class APIKeyNotFoundError(APIKeyError):
    """Raised when API key is not found."""

    def __init__(self, key_id: str) -> None:
        super().__init__(f"API key with ID '{key_id}' not found")
        self.key_id = key_id


class APIKeyExpiredError(AuthenticationError):
    """Raised when API key is expired."""

    def __init__(self) -> None:
        super().__init__("API key has expired")


class InvalidAPIKeyError(AuthenticationError):
    """Raised when API key is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid API key")
