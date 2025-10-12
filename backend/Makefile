.PHONY: help install dev test ingest seed migrate lint format clean docker-up docker-down

help:
	@echo "BlueTrace Makefile Commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Run development server with auto-reload"
	@echo "  make test        - Run tests with coverage"
	@echo "  make ingest      - Run data ingestion workers once"
	@echo "  make seed        - Seed database with admin key and demo data"
	@echo "  make migrate     - Run database migrations"
	@echo "  make lint        - Run linters (ruff + mypy)"
	@echo "  make format      - Format code with black and ruff"
	@echo "  make clean       - Clean up cache and generated files"
	@echo "  make docker-up   - Start all services with docker-compose"
	@echo "  make docker-down - Stop all services"

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	poetry run pytest

ingest:
	poetry run python -m app.scripts.run_ingest

seed:
	poetry run python -m app.scripts.seed

migrate:
	poetry run alembic upgrade head

lint:
	poetry run ruff check app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run ruff check --fix app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

