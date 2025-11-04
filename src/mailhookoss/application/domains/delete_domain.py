"""Delete domain use case."""

from mailhookoss.domain.domains.exceptions import DomainNotFoundError
from mailhookoss.domain.domains.repository import DomainRepository


class DeleteDomainUseCase:
    """Use case for deleting a domain."""

    def __init__(self, domain_repository: DomainRepository) -> None:
        """Initialize use case.

        Args:
            domain_repository: Domain repository
        """
        self._domain_repository = domain_repository

    async def execute(self, domain_or_id: str) -> None:
        """Delete domain by domain name or ID.

        Args:
            domain_or_id: Domain name or identifier

        Raises:
            DomainNotFoundError: If domain not found
        """
        # Get domain to ensure it exists
        domain = await self._domain_repository.get_by_domain_or_id(domain_or_id)
        if not domain:
            raise DomainNotFoundError(domain_or_id)

        # Delete the domain (cascade will delete mailboxes)
        await self._domain_repository.delete(domain.id)
