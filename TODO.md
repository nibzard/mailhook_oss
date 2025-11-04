# MailhookOSS Implementation TODO

## Project Setup & Infrastructure
- [x] Analyze OpenAPI spec and extract requirements
- [ ] Create comprehensive implementation specification
- [ ] Set up project structure following DDD principles
- [ ] Configure pyproject.toml with all dependencies (FastAPI, Pydantic v2, SQLAlchemy, etc.)
- [ ] Set up UV package manager configuration
- [ ] Configure development environment (pre-commit, ruff, mypy)
- [ ] Set up Docker and docker-compose for local development
- [ ] Configure environment variable management (.env)

## Core Infrastructure Layer
- [ ] Database connection pooling (PostgreSQL with asyncpg)
- [ ] Redis connection for caching and job queue
- [ ] S3/MinIO client for attachment storage
- [ ] AWS SES client for email sending/receiving
- [ ] Logging configuration (structured logging)
- [ ] Metrics and observability setup (Prometheus/OpenTelemetry)
- [ ] Health check endpoints
- [ ] Database migration system (Alembic)

## Domain Layer - Tenants
- [ ] Tenant entity and value objects
- [ ] Tenant repository interface
- [ ] Tenant repository implementation (SQLAlchemy)
- [ ] Tenant service (business logic)
- [ ] Tenant creation use case
- [ ] Tenant update use case
- [ ] Tenant retrieval use cases

## Domain Layer - API Keys
- [ ] API Key entity and value objects
- [ ] API Key repository interface
- [ ] API Key repository implementation
- [ ] API Key service (secret generation, validation)
- [ ] Authentication middleware
- [ ] Tenant impersonation logic for internal keys
- [ ] API Key CRUD use cases

## Domain Layer - Domains
- [ ] Domain entity and value objects
- [ ] DNS Record value object
- [ ] Domain repository interface
- [ ] Domain repository implementation
- [ ] Domain service (business logic)
- [ ] AWS SES integration service
- [ ] Domain verification workflow
- [ ] DNS record generation logic
- [ ] Domain CRUD use cases

## Domain Layer - Mailboxes
- [ ] Mailbox entity and value objects
- [ ] Mailbox filters value object
- [ ] Mailbox repository interface
- [ ] Mailbox repository implementation
- [ ] Mailbox service (business logic)
- [ ] Spam policy enforcement
- [ ] Inbound policy enforcement (thread_trust, permitted_only)
- [ ] Filter list management (allow/deny)
- [ ] Mailbox CRUD use cases

## Domain Layer - Emails
- [ ] Email entity and value objects
- [ ] Email address value object
- [ ] Email verdicts value object
- [ ] Email repository interface
- [ ] Email repository implementation
- [ ] Email parsing service (MIME)
- [ ] Email storage service
- [ ] Email search service (full-text search)
- [ ] Label management
- [ ] User data management
- [ ] Email CRUD use cases
- [ ] Raw email download (.eml)

## Domain Layer - Attachments
- [ ] Attachment entity and value objects
- [ ] Attachment repository interface
- [ ] Attachment repository implementation
- [ ] Attachment storage service (S3)
- [ ] Signed URL generation
- [ ] Attachment extraction from MIME
- [ ] Attachment CRUD use cases
- [ ] Inline attachment handling (Content-ID)

## Domain Layer - Threads
- [ ] Thread entity and value objects
- [ ] Thread repository interface
- [ ] Thread repository implementation
- [ ] Thread service (business logic)
- [ ] Email threading algorithm
- [ ] Thread rebuild functionality
- [ ] Thread aggregation (labels, participants)
- [ ] Thread CRUD use cases

## Domain Layer - Email Sending
- [ ] Email composer service
- [ ] Markdown to HTML conversion (CommonMark)
- [ ] HTML processing (CSS inlining, premailer)
- [ ] Email attachment encoding
- [ ] Reply-to logic (quote previous email)
- [ ] Reply policy implementation (all, all_to, all_thread, author)
- [ ] Auto-reply header insertion
- [ ] New thread creation use case
- [ ] Thread reply use case
- [ ] AWS SES sending integration

## Domain Layer - Webhooks
- [ ] Webhook entity and value objects
- [ ] Webhook filters value object
- [ ] Webhook repository interface
- [ ] Webhook repository implementation
- [ ] Webhook service (business logic)
- [ ] Webhook signature generation (Standard Webhooks)
- [ ] Webhook delivery scheduler
- [ ] Webhook delivery worker (background job)
- [ ] Retry logic with exponential backoff
- [ ] Delivery attempt recording
- [ ] Webhook CRUD use cases
- [ ] Redelivery use case

## API Layer (FastAPI)
- [ ] FastAPI application setup
- [ ] API versioning (/api/v1)
- [ ] OpenAPI/Swagger configuration
- [ ] Request/response models (Pydantic)
- [ ] Error handling middleware
- [ ] Idempotency key middleware
- [ ] Authentication dependency
- [ ] Tenant context dependency
- [ ] Pagination helpers
- [ ] CORS configuration

### API Endpoints - Tenants
- [ ] POST /tenants (create)
- [ ] GET /tenants (list - internal only)
- [ ] GET /tenants/current (get current)
- [ ] GET /tenants/{tenant_id} (get - internal only)
- [ ] PATCH /tenants/{tenant_id} (update - internal only)

### API Endpoints - API Keys
- [ ] POST /api-keys (create)
- [ ] GET /api-keys (list)
- [ ] DELETE /api-keys/{api_key_id} (delete)

### API Endpoints - Domains
- [ ] POST /domains (create/update)
- [ ] GET /domains (list)
- [ ] GET /domains/{domain_or_id} (get)
- [ ] DELETE /domains/{domain_or_id} (delete)
- [ ] GET /domains/{domain_or_id}/emails (list emails by domain)
- [ ] GET /domains/{domain_or_id}/threads (list threads by domain)

### API Endpoints - Mailboxes
- [ ] POST /domains/{domain_or_id}/mb (create/update)
- [ ] GET /domains/{domain_or_id}/mb (list)
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id} (get)
- [ ] DELETE /domains/{domain_or_id}/mb/{mailbox_alias_or_id} (delete)

### API Endpoints - Emails
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/emails (list)
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/emails/{email_id} (get)
- [ ] PATCH /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/emails/{email_id} (update)
- [ ] DELETE /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/emails/{email_id} (delete)
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/emails/{email_id}/raw (download)

### API Endpoints - Attachments
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/attachments/{attachment_id}/signed-url (get)
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/attachments/{attachment_id} (download)
- [ ] PATCH /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/attachments/{attachment_id} (update)
- [ ] GET /attachments/{mailbox_id}/{attachment_id}/download (signed download)

### API Endpoints - Threads
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads (list)
- [ ] POST /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads (create new)
- [ ] GET /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads/{thread_id} (get)
- [ ] PATCH /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads/{thread_id} (update)
- [ ] POST /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads/{thread_id}/reply (reply)
- [ ] POST /domains/{domain_or_id}/mb/{mailbox_alias_or_id}/threads/rebuild (rebuild)

### API Endpoints - Webhooks
- [ ] POST /webhooks (create/update)
- [ ] GET /webhooks (list)
- [ ] GET /webhooks/{webhook_id} (get)
- [ ] DELETE /webhooks/{webhook_id} (delete)
- [ ] GET /webhooks/queue (list scheduled deliveries)
- [ ] GET /webhooks/deliveries (list delivery attempts)
- [ ] POST /webhooks/deliveries/{delivery_id}/redeliver (redeliver)

### API Endpoints - Health
- [ ] GET /health (health check)

## Background Workers
- [ ] Webhook delivery worker (Celery/ARQ/Dramatiq)
- [ ] Email processing worker (SES notification handling)
- [ ] Domain verification worker (periodic checks)
- [ ] Cleanup worker (ephemeral webhooks, old delivery attempts)

## Database Schema
- [ ] Tenants table
- [ ] API keys table
- [ ] Domains table
- [ ] DNS records table (or JSONB in domains)
- [ ] Mailboxes table
- [ ] Emails table
- [ ] Attachments table
- [ ] Threads table
- [ ] Thread participants table
- [ ] Email labels table
- [ ] Thread labels table
- [ ] Webhooks table
- [ ] Webhook scheduled deliveries table
- [ ] Webhook delivery attempts table
- [ ] Indexes for performance
- [ ] Full-text search indexes

## Testing
- [ ] Unit tests for entities and value objects
- [ ] Unit tests for services
- [ ] Unit tests for repositories (with test database)
- [ ] Integration tests for API endpoints
- [ ] Integration tests for background workers
- [ ] Integration tests for AWS SES (mocked)
- [ ] Integration tests for S3 (mocked or MinIO)
- [ ] E2E tests for critical flows
- [ ] Load testing for webhook delivery
- [ ] Test fixtures and factories

## Documentation
- [ ] README.md with setup instructions
- [ ] Architecture documentation (ADRs)
- [ ] API documentation (auto-generated from OpenAPI)
- [ ] Development guide
- [ ] Deployment guide
- [ ] Configuration reference
- [ ] Webhook integration guide
- [ ] Email threading algorithm documentation

## Deployment & Operations
- [ ] Dockerfile for application
- [ ] Docker compose for local development
- [ ] Kubernetes manifests (optional)
- [ ] CI/CD pipeline configuration
- [ ] Database backup strategy
- [ ] Monitoring and alerting setup
- [ ] Log aggregation setup
- [ ] Performance tuning guide

## Security
- [ ] API key security review
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (HTML sanitization)
- [ ] CSRF protection (if needed)
- [ ] Rate limiting
- [ ] Input validation (Pydantic)
- [ ] Webhook signature verification
- [ ] Signed URL expiration enforcement
- [ ] Secret management (environment variables, vault)

## Nice to Have / Future Enhancements
- [ ] GraphQL API (alternative to REST)
- [ ] WebSocket support for real-time updates
- [ ] Email templates system
- [ ] Advanced search query language implementation
- [ ] Email scheduling (send later)
- [ ] Email drafts
- [ ] Email encryption (PGP)
- [ ] Multi-provider support (beyond SES)
- [ ] Advanced spam filtering (ML-based)
- [ ] Email analytics and reporting
