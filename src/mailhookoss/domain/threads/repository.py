"""Thread repository interface (already defined in emails/repository.py).

Note: The ThreadRepository interface is currently defined in
domain/emails/repository.py to keep email and thread repositories
together and avoid circular dependencies.

For the actual implementation, see:
- mailhookoss.domain.emails.repository.ThreadRepository
- mailhookoss.infrastructure.database.repositories.thread.ThreadRepositoryImpl
"""