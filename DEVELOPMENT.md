# BlueTrace Development Guide

This guide covers setting up the BlueTrace development environment, running tests, and contributing to the project.

## Prerequisites

- **Docker & Docker Compose** (v2.0+)
- **Python 3.11+** (for local development)
- **Node.js 20+** (for documentation site)
- **Poetry** (for Python dependency management)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/tritonminingco/BlueTrace.git
cd BlueTrace
```

### 2. Backend Development

```bash
cd backend

# Copy environment file
cp env.sample .env

# Install dependencies (if not using Docker)
poetry install

# Start services with Docker
docker-compose up -d db redis

# Run database migrations
poetry run alembic upgrade head

# Seed demo data
poetry run python -m app.scripts.seed

# Start development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 3. Documentation Site

```bash
cd docs

# Install dependencies
npm install

# Start development server
npm run dev
# Visit http://localhost:3000
```

### 4. Full Stack with Docker

```bash
cd backend

# Start all services including monitoring
docker-compose up -d

# Check health
curl http://localhost:8080/v1/health

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

## Development Tools

### Code Quality

```bash
# Format code
poetry run black app/ tests/

# Lint code
poetry run ruff check app/ tests/ --fix

# Type checking
poetry run mypy app/

# Run all quality checks
poetry run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py -v

# View coverage report
open htmlcov/index.html
```

### Database Management

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Downgrade migration
poetry run alembic downgrade -1
```

## API Testing

### Get API Key

After running the seed script, you'll receive an admin API key:

```bash
poetry run python -m app.scripts.seed
```

### Make Requests

```bash
export BLUETRACE_API_KEY="bt_sk_xxxxxxxx.yyyyyyyy"

# Health check (no auth required)
curl http://localhost:8080/v1/health

# Get tides data
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/tides?station_id=DEMO001&start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z"

# Interactive API docs
open http://localhost:8080/docs
```

## Monitoring & Observability

### Metrics

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **API Metrics**: http://localhost:8080/metrics

### Logs

```bash
# View API logs
docker-compose logs -f api

# View worker logs
docker-compose logs -f worker

# View database logs
docker-compose logs -f db
```

## Project Structure

```
bluetrace/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, auth, errors
│   │   ├── services/    # Business logic
│   │   ├── ingestion/   # Data ingesters
│   │   ├── models/      # SQLAlchemy models
│   │   ├── db/          # Database setup
│   │   ├── telemetry/   # OpenTelemetry
│   │   └── scripts/     # CLI scripts
│   ├── tests/           # Pytest tests
│   ├── alembic/         # Database migrations
│   └── docker-compose.yml
├── docs/                # Next.js documentation
├── .github/workflows/   # CI/CD pipelines
└── README.md
```

## Contributing

### Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- **Python**: Black formatting, Ruff linting, MyPy type checking
- **TypeScript**: ESLint, Prettier formatting
- **Tests**: 90%+ coverage required
- **Documentation**: Update relevant docs for new features

## Troubleshooting

### Common Issues

**Docker Desktop not running**
```bash
# Start Docker Desktop manually, then:
docker-compose up -d
```

**Database connection errors**
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
poetry run alembic upgrade head
poetry run python -m app.scripts.seed
```

**Port conflicts**
```bash
# Check what's using the port
netstat -tulpn | grep :8080

# Use different ports in docker-compose.yml
```

**Python dependencies issues**
```bash
# Clean and reinstall
rm -rf .venv
poetry install
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/tritonminingco/BlueTrace/issues)
- **Documentation**: http://localhost:3000 (when running locally)
- **API Docs**: http://localhost:8080/docs
