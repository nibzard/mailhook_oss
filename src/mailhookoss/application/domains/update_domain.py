"""Update domain use case."""

from mailhookoss.domain.domains.entities import Domain
from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository


class UpdateDomainUseCase:
    """Use case for updating a domain."""

    def __init__(self, domain_repository: DomainRepository) -> None:
        """Initialize use case.

        Args:
            domain_repository: Domain repository
        """
        self._domain_repository = domain_repository

    async def execute(
        self,
        domain_or_id: str,
        active: bool | None = None,
    ) -> Domain:
        """Update domain.

        Args:
            domain_or_id: Domain name or identifier
            active: Whether domain is active (None = no change)

        Returns:
            Updated domain

        Raises:
            DomainNotFoundError: If domain not found
        """
        # Get existing domain
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain:
            raise DomainNotFoundError(domain_or_id)

        # Update active status if provided
        if active is not None:
            if active:
                domain.activate()
            else:
                domain.deactivate()

        # Save updated domain
        return await self._domain_repository.save(domain)
