# MailhookOSS

> Open-source multi-tenant email management API service

MailhookOSS is a comprehensive email management API service that provides domain management, mailbox (alias) creation, email receiving/sending, email threading, and webhook notifications. Built with modern Python technologies and following Domain-Driven Design (DDD) principles.

## Features

- 🏢 **Multi-tenancy** - Complete tenant isolation and management
- 📧 **Email Management** - Receive, store, and send emails
- 🔗 **Threading** - Automatic email conversation threading
- 📎 **Attachments** - Full attachment support with S3 storage
- 🔔 **Webhooks** - Event notifications with retry logic
- 🌐 **Domain Management** - DNS verification and AWS SES integration
- 📮 **Mailboxes** - Flexible email alias management
- 🔍 **Search** - Powerful query language for email search
- 🔐 **Security** - API key authentication with tenant/internal scopes
- 📊 **Observability** - Structured logging, metrics, and tracing

## Technology Stack

- **Python 3.12+**
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and job queue
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic v2** - Data validation
- **AWS SES** - Email sending/receiving
- **S3** - Attachment storage
- **ARQ** - Background job processing
- **UV** - Ultra-fast package manager

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- UV package manager (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mailhook_oss
   ```

2. **Install UV (recommended)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   # Using UV
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start infrastructure services**
   ```bash
   docker-compose up -d
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the API server**
   ```bash
   # Development mode with auto-reload
   uvicorn mailhookoss.main:app --reload

   # Or using Python
   python -m mailhookoss.main
   ```

8. **Start background workers**
   ```bash
   arq mailhookoss.workers.webhook_delivery.WorkerSettings
   ```

The API will be available at `http://localhost:8000`

- API Documentation: http://localhost:8000/api/v1/docs
- Alternative Docs: http://localhost:8000/api/v1/redoc
- Health Check: http://localhost:8000/api/v1/health
- Metrics: http://localhost:8000/metrics

## Project Structure

```
mailhookoss/
├── src/mailhookoss/           # Main application code
│   ├── api/                   # API layer (FastAPI routes)
│   ├── application/           # Application layer (use cases)
│   ├── domain/                # Domain layer (business logic)
│   ├── infrastructure/        # Infrastructure layer (databases, external services)
│   ├── workers/               # Background workers
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── alembic/                   # Database migrations
├── pyproject.toml             # Project configuration
├── docker-compose.yml         # Local development stack
└── README.md
```

See [IMPLEMENTATION_SPEC.md](IMPLEMENTATION_SPEC.md) for detailed architecture documentation.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mailhookoss --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Code Quality

```bash
# Format code
ruff format src/

# Lint code
ruff check src/

# Type checking
mypy src/

# All checks (pre-commit)
pre-commit run --all-files
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Docker Services

The `docker-compose.yml` provides the following services:

- **PostgreSQL** (5432) - Primary database
- **Redis** (6379) - Cache and job queue
- **MinIO** (9000, 9001) - S3-compatible storage
- **LocalStack** (4566) - AWS services (SES, SNS, SQS)
- **MailHog** (1025, 8025) - Email testing

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset everything (including volumes)
docker-compose down -v
```

## API Documentation

The API follows the OpenAPI 3.1.1 specification. The full spec is available in [api.json](api.json).

### Authentication

All API requests require an API key in the Authorization header:

```bash
curl -H "Authorization: Bearer mhsec_YOUR_API_KEY" \
  http://localhost:8000/api/v1/tenants/current
```

**API Key Types:**
- **Tenant keys** (`mhsec_*`) - Scoped to a single tenant
- **Internal keys** (`mhisec_*`) - Can impersonate tenants via `X-Mailhook-Tenant` header

### Example Requests

```bash
# Get current tenant
curl -H "Authorization: Bearer mhsec_YOUR_KEY" \
  http://localhost:8000/api/v1/tenants/current

# List domains
curl -H "Authorization: Bearer mhsec_YOUR_KEY" \
  http://localhost:8000/api/v1/domains

# Create a mailbox
curl -X POST \
  -H "Authorization: Bearer mhsec_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"local_part": "support"}' \
  http://localhost:8000/api/v1/domains/example.com/mb
```

## Configuration

All configuration is managed through environment variables. See [.env.example](.env.example) for available options.

Key configuration areas:
- Database connection
- Redis connection
- S3/MinIO storage
- AWS SES credentials
- Security secrets
- API settings
- Worker settings

## Architecture

MailhookOSS follows Domain-Driven Design (DDD) principles with a layered architecture:

1. **API Layer** - FastAPI routes, request/response handling
2. **Application Layer** - Use cases, orchestration
3. **Domain Layer** - Business logic, entities, value objects
4. **Infrastructure Layer** - External services, databases

See [IMPLEMENTATION_SPEC.md](IMPLEMENTATION_SPEC.md) for detailed architecture documentation.

## Development Roadmap

See [TODO.md](TODO.md) for the complete development roadmap and task breakdown.

Current status: **Initial Project Setup Complete** ✅

Next phases:
1. Core domain models and repositories
2. API endpoints implementation
3. Email processing pipeline
4. Webhook delivery system
5. Testing and documentation

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

Apache 2.0 - See [LICENSE](LICENSE) for details

## Support

- Documentation: [IMPLEMENTATION_SPEC.md](IMPLEMENTATION_SPEC.md)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## Acknowledgments

Built with modern Python tools:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [UV](https://github.com/astral-sh/uv)
- [Ruff](https://github.com/astral-sh/ruff)
