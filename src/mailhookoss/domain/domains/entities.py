"""Domain entities."""

from datetime import datetime

from mailhookoss.domain.common.entity import AggregateRoot
from mailhookoss.domain.domains.exceptions import InvalidDomainNameError
from mailhookoss.domain.domains.value_objects import (
    DNSRecord,
    VerificationMethod,
    VerificationStatus,
)


class Domain(AggregateRoot):
    """Domain aggregate root.

    Represents a custom email domain (e.g., acme.dev) that can receive
    and send emails through the service.
    """

    def __init__(
        self,
        id: str,
        tenant_id: str,
        domain: str,
        unicode_domain: str,
        active: bool,
        verification_status: VerificationStatus,
        verification_method: VerificationMethod | None,
        verified_at: datetime | None,
        dns_records: list[DNSRecord],
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize domain.

        Args:
            id: Unique domain identifier
            tenant_id: Owning tenant ID
            domain: ASCII domain name
            unicode_domain: Unicode domain name for display
            active: Whether the domain is active
            verification_status: Verification status
            verification_method: Method used for verification
            verified_at: When domain was verified
            dns_records: DNS records for configuration
            created_at: Creation timestamp
            updated_at: Last update timestamp

        Raises:
            InvalidDomainNameError: If domain name is invalid
        """
        super().__init__(id, created_at, updated_at)
        self._validate_domain_name(domain)
        self._tenant_id = tenant_id
        self._domain = domain
        self._unicode_domain = unicode_domain
        self._active = active
        self._verification_status = verification_status
        self._verification_method = verification_method
        self._verified_at = verified_at
        self._dns_records = dns_records

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def domain(self) -> str:
        """Get ASCII domain name."""
        return self._domain

    @property
    def unicode_domain(self) -> str:
        """Get Unicode domain name."""
        return self._unicode_domain

    @property
    def active(self) -> bool:
        """Get active status."""
        return self._active

    @property
    def verification_status(self) -> VerificationStatus:
        """Get verification status."""
        return self._verification_status

    @property
    def verification_method(self) -> VerificationMethod | None:
        """Get verification method."""
        return self._verification_method

    @property
    def verified_at(self) -> datetime | None:
        """Get verification timestamp."""
        return self._verified_at

    @property
    def dns_records(self) -> list[DNSRecord]:
        """Get DNS records."""
        return self._dns_records.copy()

    def is_verified(self) -> bool:
        """Check if domain is verified."""
        return self._verification_status == VerificationStatus.VERIFIED

    def activate(self) -> None:
        """Activate the domain."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate the domain."""
        self._active = False

    def update_verification_status(
        self,
        status: VerificationStatus,
        verified_at: datetime | None = None,
    ) -> None:
        """Update verification status.

        Args:
            status: New verification status
            verified_at: Verification timestamp (if verified)
        """
        self._verification_status = status
        if status == VerificationStatus.VERIFIED and verified_at:
            self._verified_at = verified_at

    def update_dns_records(self, dns_records: list[DNSRecord]) -> None:
        """Update DNS records.

        Args:
            dns_records: New DNS records
        """
        self._dns_records = dns_records

    @staticmethod
    def _validate_domain_name(domain: str) -> None:
        """Validate domain name.

        Args:
            domain: Domain name to validate

        Raises:
            InvalidDomainNameError: If domain is invalid
        """
        if not domain or not domain.strip():
            raise InvalidDomainNameError("Domain name cannot be empty")

        # Basic validation - could be enhanced with regex
        if len(domain) > 253:
            raise InvalidDomainNameError("Domain name too long (max 253 characters)")

        if ".." in domain:
            raise InvalidDomainNameError("Domain name contains consecutive dots")

        if domain.startswith(".") or domain.endswith("."):
            raise InvalidDomainNameError("Domain name cannot start or end with a dot")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Domain(id={self.id!r}, domain={self.domain!r}, "
            f"status={self.verification_status.value!r})"
        )
