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

# Test that both legacy and new architecture components can be imported
RUN python -c "\
import sys; \
sys.path.insert(0, '/app/src'); \
import prompt_manager, auth_manager, api_endpoints; \
from src.core.config.settings import AppConfig, DatabaseConfig, DatabaseType; \
from src.prompts.models.prompt import Prompt; \
from src.core.base.database_manager import DatabaseManager; \
from src.prompts.services.prompt_service import PromptService; \
print('✅ Docker build: All imports successful')"

# Test basic new architecture functionality during build
RUN python -c "\
import sys, tempfile, os; \
sys.path.insert(0, '/app/src'); \
from src.core.config.settings import DatabaseConfig, DatabaseType; \
from src.core.base.database_manager import DatabaseManager; \
from src.prompts.services.prompt_service import PromptService; \
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db'); \
temp_db.close(); \
try: \
    db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=temp_db.name); \
    db_manager = DatabaseManager(db_config); \
    prompt_service = PromptService(db_manager); \
    print('✅ Docker build: New architecture services initialized successfully'); \
except Exception as e: \
    print(f'❌ Docker build: New architecture test failed: {e}'); \
    raise; \
finally: \
    try: os.unlink(temp_db.name); \
    except: pass"

# Expose port for Gradio and API
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Use unified launcher (defaults to multi-tenant mode with API enabled via env vars)
CMD ["python", "run.py"]
