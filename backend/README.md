# BlueTrace Backend

FastAPI backend for the BlueTrace marine data API.

## Quick Start

```bash
# Install dependencies
poetry install

# Copy environment file
cp env.sample .env

# Start database and Redis
docker-compose up -d db redis

# Run migrations
poetry run alembic upgrade head

# Seed demo data
poetry run python -m app.scripts.seed

# Start development server
make dev
```

## Development

### Commands

```bash
make dev          # Development server with auto-reload
make test         # Run tests with coverage
make lint         # Run linters
make format       # Format code
make migrate      # Run migrations
make seed         # Seed database
make ingest       # Run ingestion workers
```

### Project Structure

```
app/
├── api/v1/          # API endpoints
├── core/            # Core functionality (config, auth, errors)
├── services/        # Business logic
├── ingestion/       # Data ingestion workers
├── models/          # SQLAlchemy models
├── db/              # Database setup
├── telemetry/       # OpenTelemetry
└── scripts/         # CLI scripts

tests/               # Pytest tests
alembic/             # Database migrations
```

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Specific test
poetry run pytest tests/test_auth.py -v
```

## Database

### Migrations

```bash
# Create new migration
poetry run alembic revision -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one
poetry run alembic downgrade -1
```

## API Documentation

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

