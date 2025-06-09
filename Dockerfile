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
    SERVER_PORT=7860

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy application code (includes LICENSE file needed by pyproject.toml)
COPY . .

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only=main

# Create data directory for database
RUN mkdir -p /app/data

# Expose port for Gradio and API
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Use unified launcher (defaults to multi-tenant mode with API enabled via env vars)
CMD ["python", "run.py"]
