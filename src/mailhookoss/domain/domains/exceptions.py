"""Domain domain exceptions."""

from mailhookoss.domain.common.exceptions import DomainException, ValidationError


class DomainError(DomainException):
    """Base exception for domain-related errors."""



class InvalidDomainNameError(ValidationError):
    """Raised when domain name is invalid."""



class DomainNotFoundError(DomainError):
    """Raised when domain is not found."""

    def __init__(self, domain_id_or_name: str) -> None:
        super().__init__(f"Domain '{domain_id_or_name}' not found")
        self.domain_id_or_name = domain_id_or_name


class DomainAlreadyExistsError(DomainError):
    """Raised when domain already exists."""

    def __init__(self, domain: str) -> None:
        super().__init__(f"Domain '{domain}' already exists")
        self.domain = domain


class DomainNotVerifiedError(DomainError):
    """Raised when attempting operation on unverified domain."""

    def __init__(self, domain: str) -> None:
        super().__init__(f"Domain '{domain}' is not verified")
        self.domain = domain
