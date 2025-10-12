FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bluetrace && chown -R bluetrace:bluetrace /app
USER bluetrace

# Expose port
EXPOSE 8080

# Run application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_conf.py"]

