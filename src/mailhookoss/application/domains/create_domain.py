"""Create domain use case."""

from datetime import datetime, timezone

from mailhookoss.domain.domains.entities import Domain
from mailhookoss.domain.domains.exceptions import DomainAlreadyExistsError
from mailhookoss.domain.domains.repository import DomainRepository
from mailhookoss.domain.domains.value_objects import VerificationMethod, VerificationStatus
from mailhookoss.domain.tenants.exceptions import TenantNotFoundError
from mailhookoss.domain.tenants.repository import TenantRepository
from mailhookoss.utils.id_generator import generate_domain_id


class CreateDomainUseCase:
    """Use case for creating a new domain."""

    def __init__(
        self,
        domain_repository: DomainRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        """Initialize use case.

        Args:
            domain_repository: Domain repository
            tenant_repository: Tenant repository
        """
        self._domain_repository = domain_repository
        self._tenant_repository = tenant_repository

    async def execute(
        self,
        tenant_id: str,
        domain: str,
        active: bool = True,
    ) -> Domain:
        """Create a new domain.

        Args:
            tenant_id: Tenant identifier
            domain: Domain name
            active: Whether domain is active

        Returns:
            Created domain

        Raises:
            TenantNotFoundError: If tenant not found
            DomainAlreadyExistsError: If domain already exists
            InvalidDomainNameError: If domain name is invalid
        """
        # Verify tenant exists
        tenant = await self._tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(tenant_id)

        # Check if domain already exists
        existing = await self._domain_repository.get_by_domain_name(domain)
        if existing:
            raise DomainAlreadyExistsError(domain)

        # Create new domain
        now = datetime.now(timezone.utc)
        domain_entity = Domain(
            id=generate_domain_id(),
            tenant_id=tenant_id,
            domain=domain,
            unicode_domain=domain,  # TODO: Convert IDN domains
            active=active,
            verification_status=VerificationStatus.PENDING,
            verification_method=VerificationMethod.DNS,
            verified_at=None,
            dns_records=[],  # TODO: Generate DNS records from SES
            created_at=now,
            updated_at=now,
        )

        # Save domain
        return await self._domain_repository.save(domain_entity)
