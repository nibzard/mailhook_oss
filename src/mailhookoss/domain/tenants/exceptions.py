"""Tenant domain exceptions."""

from mailhookoss.domain.common.exceptions import DomainException, ValidationError


class TenantError(DomainException):
    """Base exception for tenant-related errors."""

    pass


class InvalidTenantNameError(ValidationError):
    """Raised when tenant name is invalid."""

    pass


class TenantNotFoundError(TenantError):
    """Raised when tenant is not found."""

    def __init__(self, tenant_id: str) -> None:
        super().__init__(f"Tenant with ID '{tenant_id}' not found")
        self.tenant_id = tenant_id


class TenantAlreadyExistsError(TenantError):
    """Raised when attempting to create a duplicate tenant."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Tenant with name '{name}' already exists")
        self.name = name
