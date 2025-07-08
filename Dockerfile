# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Set environment variables for FastAPI Web UI with Speech Dictation
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
    PYTHONPATH=/app/src:/app \
    PROMPT_OPTIMIZER=builtin \
    TRANSLATION_SERVICE=mock

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
COPY web_templates/ ./web_templates/
COPY templates/ ./templates/
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Create data directory for database and static files
RUN mkdir -p /app/data \
    && mkdir -p /app/web_templates/static/css \
    && mkdir -p /app/web_templates/static/js \
    && touch /app/web_templates/static/css/.gitkeep \
    && touch /app/web_templates/static/js/.gitkeep

# Test that both legacy and new architecture components can be imported and initialized
RUN python scripts/docker-test.py

# Expose ports for FastAPI Web UI and API (dual-server architecture)
EXPOSE 7860
EXPOSE 7861

# Health check for FastAPI web interface
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || curl -f http://localhost:7860/login || exit 1

# Use unified launcher with FastAPI Web UI, multi-tenant mode, and dual-server API
CMD ["python", "run.py", "--with-api"]
