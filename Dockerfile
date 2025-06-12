# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOCAL_DEV_MODE=false \
    MULTITENANT_MODE=true \
    ENABLE_API=true \
    DB_TYPE=sqlite \
    DB_PATH=/app/data/prompts.db \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=7860 \
    SECRET_KEY=change-this-secret-key-in-production \
    PYTHONPATH=/app/src:/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy project metadata files first (needed by Poetry)
COPY pyproject.toml poetry.lock LICENSE README.md ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only=main --no-root

# Copy application files after dependencies are installed
COPY *.py ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Create data directory for database
RUN mkdir -p /app/data

# Test that both legacy and new architecture components can be imported and initialized
RUN python scripts/docker-test.py

# Expose port for Gradio and API
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Use unified launcher (defaults to multi-tenant mode with API enabled via env vars)
CMD ["python", "run.py"]
