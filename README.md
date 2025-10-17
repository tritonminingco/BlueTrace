# BlueTrace

[![CI](https://github.com/yourusername/bluetrace/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/bluetrace/actions/workflows/ci.yml)
[![Docker](https://github.com/yourusername/bluetrace/actions/workflows/docker.yml/badge.svg)](https://github.com/yourusername/bluetrace/actions/workflows/docker.yml)
[![codecov](https://codecov.io/gh/yourusername/bluetrace/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/bluetrace)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Production-grade REST API for marine and coastal datasets**

BlueTrace aggregates public marine and coastal datasets into a clean, queryable interface with API keys, usage metering, and paid tiers. Built for developers who need reliable ocean data.

## Features

### Core Capabilities
- **Multiple Datasets**: Tides, SST, ocean currents, turbidity, and bathymetry
- **Production Ready**: Docker-based deployment with monitoring and logging
- **Developer Friendly**: OpenAPI/Swagger docs, standard REST patterns
- **Secure**: API key authentication with HMAC hashing
- **Metered Billing**: Stripe integration with usage-based pricing

### Technical Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15 with SQLAlchemy 2.x + Alembic
- **Cache/Queue**: Redis 7 + Dramatiq workers
- **Docs**: Next.js 15 with MDX
- **Observability**: OpenTelemetry with structured JSON logging
- **Testing**: pytest with 90%+ coverage target

### Production Features
- Rate limiting with Redis sliding window
- Background workers for data ingestion
- Automatic retries with exponential backoff
- Health checks for all dependencies
- CORS configuration
- Comprehensive error handling

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for docs site)

### Run with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/bluetrace.git
cd bluetrace

# Start all services
cd backend
docker-compose up -d

# Run migrations
docker-compose exec api poetry run alembic upgrade head

# Seed demo data and create admin key
docker-compose exec api poetry run python -m app.scripts.seed

# Check health
curl http://localhost:8080/v1/health
```

### Local Development

```bash
# Backend
cd backend

# Install dependencies
poetry install

# Copy environment file
cp env.sample .env

# Start Postgres and Redis
docker-compose up -d db redis

# Run migrations
poetry run alembic upgrade head

# Seed database
poetry run python -m app.scripts.seed

# Start development server
make dev
# or
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

```bash
# Docs site (separate terminal)
cd docs
npm install
npm run dev
# Visit http://localhost:3000
```

## API Usage

### Get an API Key

After running the seed script, you'll receive an admin API key. Save it securely!

```bash
poetry run python -m app.scripts.seed
```

### Make Your First Request

```bash
export BLUETRACE_API_KEY="bt_sk_xxxxxxxx.yyyyyyyy"

# Health check (no auth required)
curl http://localhost:8080/v1/health

# Get tides data
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/tides?station_id=DEMO001&start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z"

# Get sea surface temperature
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/sst?lat=40.0&lon=-74.0&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z"
```

### Response Format

All endpoints return a standardized envelope:

```json
{
  "data": [
    {
      "station_id": "DEMO001",
      "time": "2024-01-01T00:00:00Z",
      "water_level_m": 1.234
    }
  ],
  "meta": {
    "query": {
      "station_id": "DEMO001",
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-12-31T23:59:59Z"
    },
    "count": 1,
    "source": "NOAA CO-OPS",
    "credits": "Data provided by NOAA",
    "next": null
  }
}
```

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /v1/health` | Health check (no auth) |
| `GET /v1/tides` | Water level measurements |
| `GET /v1/sst` | Sea surface temperature |
| `GET /v1/currents` | Ocean current vectors |
| `GET /v1/turbidity` | Water clarity measurements |
| `GET /v1/bathy/tiles/{z}/{x}/{y}.png` | Bathymetry tiles |
| `POST /v1/admin/keys` | Create API key (admin only) |
| `POST /stripe/webhook` | Stripe webhook handler |

**Interactive Docs**: http://localhost:8080/docs

## Development

### Makefile Commands

```bash
make install      # Install dependencies
make dev         # Run development server
make test        # Run tests with coverage
make ingest      # Run ingestion workers once
make seed        # Seed database with demo data
make migrate     # Run database migrations
make lint        # Run linters
make format      # Format code
make clean       # Clean up cache files
make docker-up   # Start Docker services
make docker-down # Stop Docker services
```

### Running Tests

```bash
cd backend

# Run all tests
make test

# Run specific test file
poetry run pytest tests/test_auth.py

# Run with coverage report
poetry run pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

### Code Quality

This project uses:
- **black** for code formatting
- **ruff** for linting
- **mypy** for type checking
- **pre-commit** hooks for automated checks

```bash
# Setup pre-commit hooks
cd backend
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

## Architecture

```
bluetrace/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   │   └── v1/      # Version 1 endpoints
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
│   └── app/
│       ├── quickstart/
│       ├── pricing/
│       └── api/v1/
└── .github/
    └── workflows/       # CI/CD pipelines
```

## Rate Limits

| Plan | Requests/Minute | Price |
|------|----------------|-------|
| Free | 30 | $0 |
| Pro | 300 | $49/mo + metered |
| Enterprise | Custom | Contact us |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
```

## Security

- API keys stored as HMAC-SHA256 hashes with salt
- Keys never logged in full (only prefix)
- CORS allowlist configuration
- Request timeouts on external fetches
- Stripe webhook signature verification
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic

## Monitoring & Observability

- Structured JSON logging
- OpenTelemetry tracing
- Request ID tracking
- Database and Redis health checks
- Prometheus metrics (planned)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Maintain 90%+ code coverage
- Follow black/ruff formatting
- Add type hints (mypy strict mode)
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data provided by NOAA (National Oceanic and Atmospheric Administration)
- Built with FastAPI, PostgreSQL, Redis, and Next.js
- Inspired by the need for accessible marine data APIs

## Support

- **Documentation**: http://localhost:3000 (when running locally)
- **Issues**: [GitHub Issues](https://github.com/yourusername/bluetrace/issues)
- **Email**: contact@tritonmining.io
- **Twitter**: [@BlueTraceAPI](https://twitter.com/BlueTraceAPI)

## Roadmap

- [ ] Additional data sources (GEBCO, Copernicus)
- [ ] GraphQL API
- [ ] Real-time WebSocket feeds
- [ ] Historical data archives
- [ ] Machine learning predictions
- [ ] Mobile SDKs (iOS/Android)
- [ ] Terraform infrastructure templates
- [ ] Kubernetes Helm charts

---

**Built for ocean data enthusiasts and marine developers**

