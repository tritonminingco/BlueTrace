# BlueTrace Quick Start Guide

Get BlueTrace running in 5 minutes!

## Prerequisites

- Docker & Docker Compose
- Git

## Step 1: Clone and Start Services

```bash
# Clone the repository
git clone https://github.com/yourusername/bluetrace.git
cd bluetrace/backend

# Start all services (PostgreSQL, Redis, API, Worker)
docker-compose up -d

# Wait for services to be healthy (about 10 seconds)
docker-compose ps
```

## Step 2: Run Migrations

```bash
# Apply database schema
docker-compose exec api poetry run alembic upgrade head
```

## Step 3: Seed Demo Data

```bash
# Create admin key and load demo data
docker-compose exec api poetry run python -m app.scripts.seed
```

**Important**: Copy the API key shown - it's only displayed once!

Example output:
```
Your Admin API Key (SAVE THIS - shown only once):

  bt_sk_ABC12345.xyz67890...
```

## Step 4: Test the API

```bash
# Save your API key
export BLUETRACE_API_KEY="bt_sk_ABC12345.xyz67890..."

# Test health endpoint (no auth required)
curl http://localhost:8080/v1/health

# Get tides data
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/tides?station_id=DEMO001&start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z"
```

Expected response:
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
    "count": 1,
    "source": "Demo Dataset",
    "credits": "...",
    "next": null
  }
}
```

## Step 5: Explore the API

### Interactive Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Try More Endpoints

**Sea Surface Temperature:**
```bash
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/sst?lat=40.0&lon=-74.0&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z"
```

**Ocean Currents:**
```bash
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/currents?bbox=-75,38,-74,39&time=2024-01-01T12:00:00Z"
```

**Turbidity:**
```bash
curl -H "X-Api-Key: $BLUETRACE_API_KEY" \
  "http://localhost:8080/v1/turbidity?bbox=-75,38,-74,39&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z"
```

## Step 6: View Logs (Optional)

```bash
# View all logs
docker-compose logs -f

# View API logs only
docker-compose logs -f api

# View worker logs
docker-compose logs -f worker
```

## Troubleshooting

### Services won't start

```bash
# Check service status
docker-compose ps

# Restart services
docker-compose restart

# View logs for errors
docker-compose logs
```

### Database errors

```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec api poetry run alembic upgrade head
docker-compose exec api poetry run python -m app.scripts.seed
```

### Port conflicts

If port 8080, 5432, or 6379 are already in use, edit `docker-compose.yml` to use different ports.

## Next Steps

1. **Read the docs**: See [README.md](README.md) for full documentation
2. **Explore the code**: Check out the backend architecture
3. **Run tests**: `cd backend && make test`
4. **Start the docs site**: `cd docs && npm install && npm run dev`
5. **Create more API keys**: Use the admin key to create keys for different plans

## Common Commands

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d

# View API logs
docker-compose logs -f api

# Run tests
docker-compose exec api poetry run pytest

# Access database
docker-compose exec db psql -U bluetrace -d bluetrace
```

## Local Development (Without Docker)

If you prefer to run locally:

```bash
cd backend

# Install dependencies
poetry install

# Start PostgreSQL and Redis only
docker-compose up -d db redis

# Copy environment file
cp env.sample .env

# Run migrations
poetry run alembic upgrade head

# Seed data
poetry run python -m app.scripts.seed

# Start dev server
make dev
```

## Getting Help

- **Documentation**: http://localhost:8080/docs
- **Issues**: [GitHub Issues](https://github.com/yourusername/bluetrace/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**You're all set! 🌊 Happy coding!**

