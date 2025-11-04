# MailhookOSS - Implementation Specification

## Overview

MailhookOSS is a multi-tenant email management API service that provides domain management, mailbox (alias) creation, email receiving/sending, email threading, and webhook notifications. This specification outlines the complete architecture and implementation approach following modern Python best practices, Domain-Driven Design (DDD), and the KISS/DRY principles.

## Technology Stack

### Core Technologies
- **Python**: 3.12+ (latest stable)
- **API Framework**: FastAPI 0.110+
- **Validation**: Pydantic v2.6+
- **Package Manager**: UV (Astral's ultra-fast package manager)
- **ASGI Server**: Uvicorn with Gunicorn for production

### Data Layer
- **Primary Database**: PostgreSQL 16+ with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Migrations**: Alembic
- **Cache**: Redis 7+ (for distributed caching and job queue)

### Storage & External Services
- **Object Storage**: S3-compatible storage (AWS S3 or MinIO)
- **Email Provider**: AWS SES (Simple Email Service)
- **File Storage**: S3 for email attachments and raw .eml files

### Background Processing
- **Task Queue**: ARQ (Async Redis Queue) - lightweight, async-native
- **Alternative**: Celery with Redis broker (if more features needed)

### Development Tools
- **Linter/Formatter**: Ruff (replaces Black, isort, flake8)
- **Type Checker**: mypy with strict mode
- **Pre-commit Hooks**: pre-commit framework
- **Testing**: pytest with pytest-asyncio
- **API Testing**: httpx for async client testing
- **Coverage**: pytest-cov

### Additional Libraries
- **Email Parsing**: email library (stdlib) + email-validator
- **HTML Processing**:
  - `markdown` or `python-markdown` for CommonMark
  - `premailer` for CSS inlining
  - `bleach` for HTML sanitization
- **Search**: PostgreSQL full-text search (pg_trgm, tsvector)
- **ID Generation**: `ulid-py` or `nanoid` for sortable unique IDs
- **Webhooks**: `svix` library for Standard Webhooks implementation
- **Logging**: `structlog` for structured logging
- **Configuration**: `pydantic-settings` for environment management
- **HTTP Client**: `httpx` for async HTTP requests

## Architecture Overview

### Layered Architecture (DDD)

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                     │
│  - Controllers/Routes                                       │
│  - Request/Response Models (Pydantic)                       │
│  - Middleware (Auth, Errors, Idempotency)                   │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  - Use Cases / Application Services                         │
│  - DTOs (Data Transfer Objects)                             │
│  - Orchestration Logic                                      │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│  - Entities (Tenant, Domain, Mailbox, Email, etc.)          │
│  - Value Objects (EmailAddress, DNSRecord, etc.)            │
│  - Domain Services (business logic)                         │
│  - Repository Interfaces                                    │
│  - Domain Events                                            │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  - Repository Implementations (SQLAlchemy)                  │
│  - External Service Clients (SES, S3)                       │
│  - Database Models (SQLAlchemy)                             │
│  - Event Publishers                                         │
└─────────────────────────────────────────────────────────────┘
```

### Domain Model

#### Core Bounded Contexts

1. **Identity & Access Management (IAM)**
   - Tenants
   - API Keys
   - Authentication
   - Authorization

2. **Email Domain Management**
   - Domains
   - DNS Records
   - Domain Verification
   - SES Integration

3. **Mailbox Management**
   - Mailboxes (Aliases)
   - Spam Policies
   - Inbound Policies
   - Filter Lists (allow/deny)

4. **Email Processing**
   - Emails
   - Attachments
   - Email Parsing
   - Label Management

5. **Conversation Threading**
   - Threads
   - Thread Participants
   - Thread Aggregation

6. **Email Sending**
   - Email Composition
   - Markdown/HTML Processing
   - Reply Logic
   - SES Sending

7. **Webhook System**
   - Webhooks
   - Webhook Deliveries
   - Delivery Attempts
   - Retry Logic

## Project Structure

```
mailhookoss/
├── pyproject.toml              # UV/pip configuration
├── uv.lock                     # Lock file (auto-generated)
├── .python-version             # Python version specification
├── README.md
├── IMPLEMENTATION_SPEC.md
├── TODO.md
├── .env.example
├── .gitignore
├── docker-compose.yml          # Local development stack
├── Dockerfile
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── conftest.py
│
└── src/
    └── mailhookoss/
        ├── __init__.py
        │
        ├── main.py             # FastAPI application entry point
        ├── config.py           # Application configuration
        │
        ├── api/                # API Layer (FastAPI routes)
        │   ├── __init__.py
        │   ├── deps.py         # Dependencies (auth, db session, etc.)
        │   ├── errors.py       # Error handlers
        │   ├── middleware.py   # Custom middleware
        │   ├── pagination.py   # Pagination helpers
        │   └── v1/
        │       ├── __init__.py
        │       ├── router.py   # Main router
        │       ├── tenants.py
        │       ├── api_keys.py
        │       ├── domains.py
        │       ├── mailboxes.py
        │       ├── emails.py
        │       ├── attachments.py
        │       ├── threads.py
        │       ├── webhooks.py
        │       └── health.py
        │
        ├── application/        # Application Layer (Use Cases)
        │   ├── __init__.py
        │   ├── dtos.py         # Data Transfer Objects
        │   ├── tenants/
        │   │   ├── create_tenant.py
        │   │   ├── update_tenant.py
        │   │   └── get_tenant.py
        │   ├── api_keys/
        │   ├── domains/
        │   ├── mailboxes/
        │   ├── emails/
        │   ├── threads/
        │   └── webhooks/
        │
        ├── domain/             # Domain Layer
        │   ├── __init__.py
        │   │
        │   ├── common/         # Shared domain primitives
        │   │   ├── __init__.py
        │   │   ├── entity.py
        │   │   ├── value_object.py
        │   │   ├── repository.py
        │   │   ├── events.py
        │   │   └── exceptions.py
        │   │
        │   ├── tenants/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   └── exceptions.py
        │   │
        │   ├── api_keys/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── value_objects.py
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   └── exceptions.py
        │   │
        │   ├── domains/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── value_objects.py  # DNSRecord, VerificationStatus, etc.
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   └── exceptions.py
        │   │
        │   ├── mailboxes/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── value_objects.py  # MailboxFilters, SpamPolicy, etc.
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   └── exceptions.py
        │   │
        │   ├── emails/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── value_objects.py  # EmailAddress, EmailVerdicts, etc.
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   ├── parser.py          # MIME parsing
        │   │   ├── search.py          # Search query language
        │   │   └── exceptions.py
        │   │
        │   ├── attachments/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   └── exceptions.py
        │   │
        │   ├── threads/
        │   │   ├── __init__.py
        │   │   ├── entities.py
        │   │   ├── repository.py
        │   │   ├── service.py
        │   │   ├── threading_algorithm.py
        │   │   └── exceptions.py
        │   │
        │   ├── sending/
        │   │   ├── __init__.py
        │   │   ├── composer.py        # Email composition
        │   │   ├── html_processor.py  # Markdown, CSS inlining
        │   │   ├── reply_logic.py
        │   │   └── service.py
        │   │
        │   └── webhooks/
        │       ├── __init__.py
        │       ├── entities.py
        │       ├── value_objects.py   # WebhookFilters, etc.
        │       ├── repository.py
        │       ├── service.py
        │       ├── delivery.py        # Delivery logic
        │       └── exceptions.py
        │
        ├── infrastructure/     # Infrastructure Layer
        │   ├── __init__.py
        │   │
        │   ├── database/
        │   │   ├── __init__.py
        │   │   ├── base.py            # SQLAlchemy Base
        │   │   ├── session.py         # Session management
        │   │   ├── models/            # SQLAlchemy models
        │   │   │   ├── __init__.py
        │   │   │   ├── tenant.py
        │   │   │   ├── api_key.py
        │   │   │   ├── domain.py
        │   │   │   ├── mailbox.py
        │   │   │   ├── email.py
        │   │   │   ├── attachment.py
        │   │   │   ├── thread.py
        │   │   │   └── webhook.py
        │   │   │
        │   │   └── repositories/      # Repository implementations
        │   │       ├── __init__.py
        │   │       ├── tenant.py
        │   │       ├── api_key.py
        │   │       ├── domain.py
        │   │       ├── mailbox.py
        │   │       ├── email.py
        │   │       ├── attachment.py
        │   │       ├── thread.py
        │   │       └── webhook.py
        │   │
        │   ├── storage/
        │   │   ├── __init__.py
        │   │   ├── s3.py              # S3 client wrapper
        │   │   └── local.py           # Local filesystem (dev)
        │   │
        │   ├── email_provider/
        │   │   ├── __init__.py
        │   │   ├── ses.py             # AWS SES client
        │   │   └── mock.py            # Mock for testing
        │   │
        │   ├── cache/
        │   │   ├── __init__.py
        │   │   └── redis.py           # Redis client
        │   │
        │   ├── queue/
        │   │   ├── __init__.py
        │   │   └── arq.py             # ARQ worker configuration
        │   │
        │   └── external/
        │       └── webhook_client.py  # HTTP client for webhook delivery
        │
        ├── workers/            # Background workers
        │   ├── __init__.py
        │   ├── webhook_delivery.py
        │   ├── email_processor.py
        │   └── domain_verification.py
        │
        └── utils/              # Utilities
            ├── __init__.py
            ├── id_generator.py
            ├── datetime.py
            ├── security.py
            └── query_parser.py  # Parse search query language
```

## Key Design Decisions

### 1. Domain-Driven Design (DDD)

**Entities vs Value Objects:**
- **Entities**: Have unique identity (ID), mutable lifecycle
  - Tenant, Domain, Mailbox, Email, Thread, Webhook, APIKey
- **Value Objects**: Immutable, compared by value
  - EmailAddress, DNSRecord, MailboxFilters, EmailVerdicts

**Repositories:**
- Interface defined in domain layer
- Implementation in infrastructure layer
- Async methods for all operations
- Use of specification pattern for complex queries

**Domain Events:**
- EmailReceived
- EmailSent
- DomainVerified
- WebhookDeliveryFailed
- ThreadCreated

### 2. Async-First Architecture

All I/O operations are async:
- Database queries (SQLAlchemy async)
- HTTP requests (httpx)
- File storage (aioboto3 for S3)
- Redis operations (aioredis)
- Background tasks (ARQ)

### 3. Multi-Tenancy Strategy

**Tenant Isolation:**
- All data tables include `tenant_id` column
- Row-level security enforced in repositories
- Tenant context propagated through dependency injection
- Internal API keys can impersonate tenants via `X-Mailhook-Tenant` header

**Tenant Context:**
```python
class TenantContext:
    tenant_id: str | None
    is_internal: bool
```

### 4. Authentication & Authorization

**API Key Types:**
- **Tenant Keys** (`mhsec_*`): Scoped to single tenant
- **Internal Keys** (`mhisec_*`): Can impersonate any tenant

**Authentication Flow:**
1. Extract Bearer token from Authorization header
2. Lookup API key in database
3. Validate expiration
4. For internal keys, check `X-Mailhook-Tenant` header
5. Inject TenantContext into request state

### 5. ID Generation

Use ULID (Universally Unique Lexicographically Sortable Identifier):
- Time-ordered (sortable)
- URL-safe
- 26 characters
- Prefixed for type identification:
  - `tn_*` - Tenant
  - `dom_*` - Domain
  - `mb_*` - Mailbox
  - `eml_*` - Email
  - `att_*` - Attachment
  - `thr_*` - Thread
  - `wh_*` - Webhook
  - `key_*` - API Key
  - `mhsec_*` / `mhisec_*` - API Key Secrets
  - `whsec_*` - Webhook Secrets

### 6. Pagination

Cursor-based pagination:
- Opaque cursor (base64-encoded)
- Includes last seen ID + timestamp
- Support for `next` and `prev` cursors
- Default limit: 50, max: 100 (configurable per endpoint)

### 7. Idempotency

**Idempotency Key Support:**
- Optional `Idempotency-Key` header
- Store request fingerprint in Redis (24h TTL)
- Return cached response for duplicate requests
- Applies to POST/PATCH operations marked with `x-idempotency: true`

### 8. Error Handling

**Error Response Format:**
```json
{
  "error": {
    "code": 400,
    "detail": "Human-readable error message",
    "correlation_id": "req_01HQ5KXJ8Z8N9M2K5D6P7R3S4T"
  }
}
```

**Exception Hierarchy:**
- `DomainException` (base)
  - `EntityNotFound`
  - `ValidationError`
  - `ConflictError`
  - `AuthenticationError`
  - `AuthorizationError`

### 9. Email Threading Algorithm

**Threading Strategy:**
1. Group by `In-Reply-To` and `References` headers
2. Fallback to subject normalization (strip Re:, Fwd:, etc.)
3. Within mailbox scope only
4. Maintain thread participants list
5. Aggregate labels from all emails
6. Track first/last message timestamps

### 10. Email Search

**Query Language:**
```
from:alice@example.com
to:bob@example.com
subject:"invoice"
has:attachment
label:important
before:2024-06-01
after:2024-01-01
```

**Implementation:**
- Parse query into AST
- Convert to SQL WHERE clauses
- Use PostgreSQL full-text search for subject/body
- Index optimization with GIN/GiST

### 11. Webhook Delivery

**Standard Webhooks (https://www.standardwebhooks.com/):**
- HMAC-SHA256 signatures
- `webhook-id`, `webhook-timestamp`, `webhook-signature` headers
- Retry logic: exponential backoff (1s, 5s, 25s, 125s, 625s)
- Max 5 attempts
- Store delivery attempts with responses

**Delivery States:**
- `pending` - Queued for delivery
- `processing` - Currently being delivered
- `delivered` - Successfully delivered (2xx response)
- `failed` - Failed but will retry
- `failed_permanent` - Failed permanently (4xx non-retryable)
- `expired` - Max retries exceeded

### 12. Email Processing Pipeline

**Inbound Email Flow (SES → API):**
1. SES receives email → S3 (raw .eml)
2. SES publishes SNS notification
3. API receives SNS webhook → SQS → Worker
4. Worker:
   - Download .eml from S3
   - Parse MIME (headers, body, attachments)
   - Verify domain ownership
   - Check mailbox filters (allow/deny lists)
   - Apply spam/inbound policies
   - Extract attachments → S3
   - Store email in database
   - Create/update thread
   - Trigger webhooks (email.received event)

**Outbound Email Flow (API → SES):**
1. API receives send request (new thread or reply)
2. Compose email:
   - Convert markdown to HTML (if provided)
   - Inline CSS styles
   - Sanitize HTML
   - Encode attachments
   - Build MIME message
3. Send via SES
4. Store sent email in database
5. Update thread

### 13. HTML Processing

**Markdown to HTML:**
- Use `markdown` library with CommonMark spec
- Wrap in `<div class="response">` for styling
- Optional CSS injection

**CSS Inlining:**
- Use `premailer` to inline styles
- Ensure email client compatibility
- Strip unsafe CSS

**HTML Sanitization:**
- Use `bleach` to sanitize HTML
- Allow safe tags/attributes
- Remove scripts, iframes

### 14. Attachment Storage

**Storage Strategy:**
- Store in S3 with key: `{tenant_id}/{mailbox_id}/{email_id}/{attachment_id}`
- Generate signed URLs (1h expiration) for download
- Store metadata in database (filename, content_type, size)
- Support inline attachments via Content-ID

### 15. Database Schema Design

**Key Considerations:**
- Use UUID/ULID primary keys
- Include `created_at`, `updated_at` timestamps (with triggers)
- Soft deletes with `deleted_at` column
- JSONB columns for flexible data (user_data, headers)
- Array columns for labels
- Full-text search columns (tsvector)
- Proper indexes for performance

**Example Schema (Emails table):**
```sql
CREATE TABLE emails (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    mailbox_id TEXT NOT NULL REFERENCES mailboxes(id),
    thread_id TEXT REFERENCES threads(id),
    message_id TEXT NOT NULL,
    from_addr TEXT NOT NULL,
    from_name TEXT,
    subject TEXT,
    text_body TEXT,
    html_body TEXT,
    original_text TEXT,
    original_html TEXT,
    headers JSONB NOT NULL,
    labels TEXT[] DEFAULT '{}',
    user_data JSONB DEFAULT '{}',
    custom_summary TEXT DEFAULT '',
    verdicts JSONB,
    received_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(subject, '') || ' ' || coalesce(text_body, ''))
    ) STORED
);

CREATE INDEX idx_emails_tenant_mailbox ON emails(tenant_id, mailbox_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_emails_thread ON emails(thread_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_emails_labels ON emails USING GIN(labels) WHERE deleted_at IS NULL;
CREATE INDEX idx_emails_search ON emails USING GIN(search_vector);
CREATE INDEX idx_emails_received_at ON emails(received_at DESC);
```

## Configuration Management

**Environment Variables (12-Factor App):**
```python
# src/mailhookoss/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Application
    app_name: str = "MailhookOSS"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # S3
    s3_endpoint: str | None = None
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    s3_region: str = "us-east-1"

    # AWS SES
    ses_region: str = "us-east-1"
    ses_access_key: str
    ses_secret_key: str
    ses_configuration_set: str | None = None

    # Security
    api_key_secret: str  # For HMAC signing
    signed_url_secret: str
    signed_url_expiration: int = 3600  # 1 hour

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100

    # Webhooks
    webhook_timeout: int = 30  # seconds
    webhook_max_retries: int = 5
    webhook_retry_delays: list[int] = [1, 5, 25, 125, 625]

    # Workers
    worker_concurrency: int = 10
```

## Testing Strategy

### Unit Tests
- Domain entities and value objects
- Domain services (business logic)
- Use cases
- Utilities and helpers
- Mock external dependencies

### Integration Tests
- Repository implementations (with test database)
- API endpoints (with test client)
- External service integrations (mocked)
- Background workers

### E2E Tests
- Complete user flows
- Email receiving/sending
- Webhook delivery
- Domain verification

### Test Database
- Use Docker container for PostgreSQL
- Run migrations before tests
- Rollback transactions after each test
- Fixtures for common test data

## Logging & Observability

**Structured Logging (structlog):**
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "email_received",
    email_id="eml_123",
    mailbox_id="mb_456",
    tenant_id="tn_789"
)
```

**Metrics (Prometheus):**
- Request count/latency
- Email processing time
- Webhook delivery success/failure rates
- Database connection pool stats
- Queue depth

**Tracing (OpenTelemetry):**
- Distributed tracing across services
- Track request flow through layers
- Identify performance bottlenecks

## Deployment

**Docker:**
- Multi-stage build for smaller images
- Separate images for API and workers
- Health check endpoints

**Environment:**
- Development: Docker Compose
- Staging/Production: Kubernetes or ECS

**Database Migrations:**
- Run via Alembic
- Automated in CI/CD pipeline
- Support for rollbacks

## Security Considerations

1. **Input Validation**: Pydantic models for all inputs
2. **SQL Injection**: Parameterized queries via SQLAlchemy
3. **XSS Prevention**: HTML sanitization with bleach
4. **API Key Security**: Hashed storage, secure generation
5. **Webhook Signatures**: HMAC verification
6. **Rate Limiting**: Per tenant, per endpoint
7. **Secrets Management**: Environment variables, not in code
8. **TLS/HTTPS**: Required for all external communication
9. **CORS**: Configured appropriately
10. **Dependency Scanning**: Regular security audits

## Performance Optimization

1. **Database Indexes**: Proper indexing for queries
2. **Connection Pooling**: Reuse database connections
3. **Caching**: Redis for frequently accessed data
4. **Async I/O**: Non-blocking operations
5. **Pagination**: Cursor-based for large datasets
6. **Lazy Loading**: Load related data on demand
7. **Background Processing**: Offload heavy tasks to workers
8. **CDN**: For static assets (if applicable)
9. **Query Optimization**: Use explain analyze
10. **Horizontal Scaling**: Stateless API servers

## Development Workflow

1. **Setup**:
   ```bash
   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Clone and setup
   git clone <repo>
   cd mailhookoss
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"

   # Setup pre-commit
   pre-commit install

   # Start services
   docker-compose up -d

   # Run migrations
   alembic upgrade head
   ```

2. **Development**:
   ```bash
   # Run API server
   uvicorn mailhookoss.main:app --reload

   # Run workers
   arq mailhookoss.workers.webhook_delivery.WorkerSettings

   # Run tests
   pytest

   # Type checking
   mypy src/

   # Linting
   ruff check src/

   # Format
   ruff format src/
   ```

3. **Database Changes**:
   ```bash
   # Create migration
   alembic revision --autogenerate -m "description"

   # Apply migration
   alembic upgrade head

   # Rollback
   alembic downgrade -1
   ```

## Next Steps

See TODO.md for detailed implementation tasks. The recommended order:

1. **Phase 1: Foundation**
   - Project setup, configuration, database
   - Core domain models and repositories
   - Basic API structure

2. **Phase 2: Core Features**
   - Tenant and API key management
   - Domain and mailbox management
   - Email storage and retrieval

3. **Phase 3: Advanced Features**
   - Email threading
   - Email sending
   - Webhook system

4. **Phase 4: Polish**
   - Search functionality
   - Background workers
   - Testing and documentation

5. **Phase 5: Production Ready**
   - Performance optimization
   - Security hardening
   - Deployment setup
