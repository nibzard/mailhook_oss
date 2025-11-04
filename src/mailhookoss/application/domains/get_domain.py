"""Get domain use case."""

from mailhookoss.domain.domains.entities import Domain
from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository


class GetDomainUseCase:
    """Use case for retrieving a domain."""

    def __init__(self, domain_repository: DomainRepository) -> None:
        """Initialize use case.

        Args:
            domain_repository: Domain repository
        """
        self._domain_repository = domain_repository

    async def execute(self, domain_or_id: str) -> Domain:
        """Get domain by domain name or ID.

        Args:
            domain_or_id: Domain name or identifier

        Returns:
            Domain entity

        Raises:
            DomainNotFoundError: If domain not found
        """
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain:
            raise DomainNotFoundError(domain_or_id)

        return domain
