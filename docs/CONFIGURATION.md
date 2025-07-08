# ⚙️ Configuration Guide

Complete configuration guide for AI Prompt Manager, covering AI services, deployment options, and system setup.

## Table of Contents

1. [Quick Start](#quick-start)
2. [AI Services Configuration](#ai-services-configuration)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Configuration](#deployment-configuration)
5. [Database Configuration](#database-configuration)
6. [Security Configuration](#security-configuration)

---

## Quick Start

### Basic Installation

```bash
# Install from PyPI
pip install promptman
python -m promptman

# Or install from source
git clone https://github.com/makercorn/ai-prompt-manager.git
cd ai-prompt-manager
poetry install
poetry run python run.py
```

### Configuration Modes

The application supports multiple deployment modes through environment variables:

```bash
# Single-user mode (no authentication)
MULTITENANT_MODE=false poetry run python run.py

# Multi-tenant mode with API
ENABLE_API=true poetry run python run.py --with-api

# Custom port and debug mode
poetry run python run.py --port 8080 --debug
```

## AI Services Configuration

### Overview

The AI Prompt Manager features a comprehensive AI services configuration system supporting 10+ providers with operation-specific model assignment.

### Supported Providers

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-4, GPT-3.5, GPT-4o | Function calling, JSON mode, vision |
| **Azure OpenAI** | Enterprise GPT models | Corporate deployment, compliance |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | Long context, safety-focused |
| **Google** | Gemini Pro, Gemini Ultra | Multimodal capabilities |
| **Ollama** | Local models | Privacy, offline operation |
| **LM Studio** | Local deployment | Custom model hosting |
| **llama.cpp** | GGUF models | Efficient local inference |
| **Hugging Face** | Hub models | Open source models |
| **Cohere** | Command models | Enterprise NLP |
| **Together AI** | Hosted models | Scalable inference |

### Adding AI Model Providers

#### Method 1: Web Interface (Recommended)

1. **Access AI Services**: Navigate to Settings → AI Services
2. **Click "Add Model"** 
3. **Configure the model**:
   ```
   Provider: OpenAI
   Model ID: gpt-4o-mini
   Display Name: GPT-4o Mini
   API Key: sk-...
   Context Length: 128000
   Input Cost: 0.15 per 1K tokens
   Output Cost: 0.60 per 1K tokens
   ```

#### Method 2: Programmatic Configuration

```python
from src.core.config.ai_model_config import ModelConfig, AIProvider

# Add a new OpenAI model
new_model = ModelConfig(
    name="my-gpt-4o",
    provider=AIProvider.OPENAI,
    model_id="gpt-4o-mini",
    display_name="My GPT-4o Mini",
    api_key="sk-your-api-key",
    cost_per_1k_input_tokens=0.15,
    cost_per_1k_output_tokens=0.60,
    max_context_length=128000,
    supports_function_calling=True,
    supports_json_mode=True
)
```

#### Method 3: Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Google Configuration
GOOGLE_API_KEY=your-google-key
GOOGLE_MODEL=gemini-pro

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Operation-Specific Model Assignment

Configure different models for different operations:

```python
# Configure models for specific operations
operation_configs = {
    OperationType.PROMPT_ENHANCEMENT: {
        "primary_model": "gpt-4o-mini",
        "fallback_models": ["claude-3-haiku", "gemini-pro"]
    },
    OperationType.TRANSLATION: {
        "primary_model": "gpt-4",
        "fallback_models": ["claude-3-sonnet"]
    },
    OperationType.CODE_GENERATION: {
        "primary_model": "claude-3-opus",
        "fallback_models": ["gpt-4", "codellama"]
    }
}
```

### Local Model Setup

#### Ollama Setup

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama2
ollama pull codellama
ollama pull mistral

# Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### LM Studio Setup

```bash
# Download LM Studio from https://lmstudio.ai
# Start local server on port 1234
LM_STUDIO_BASE_URL=http://localhost:1234
LM_STUDIO_MODEL=local-model
```

## Environment Configuration

### Core Settings

```bash
# Application Mode
MULTITENANT_MODE=true              # Enable multi-tenant (default)
ENABLE_API=false                   # Enable REST API endpoints
LOCAL_DEV_MODE=true                # Development features
DEBUG=false                        # Debug logging

# Server Configuration
HOST=127.0.0.1                     # Server host
PORT=7860                          # Default port
WORKERS=1                          # Number of workers

# Security
SECRET_KEY=auto-generated           # JWT signing secret (auto-generated if not set)
SESSION_TIMEOUT=86400               # Session timeout in seconds (24 hours)
```

### Database Configuration

```bash
# SQLite (Default)
DB_TYPE=sqlite
DB_PATH=prompts.db

# PostgreSQL (Production)
DB_TYPE=postgres
POSTGRES_DSN=postgresql://user:pass@host:port/db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=promptman
POSTGRES_USER=promptman
POSTGRES_PASSWORD=secure_password
```

### AI Service Integration

```bash
# Prompt Optimization
PROMPT_OPTIMIZER=langwatch          # langwatch, promptperfect, builtin
LANGWATCH_API_KEY=your_key
PROMPTPERFECT_API_KEY=your_key

# Translation Services  
TRANSLATION_SERVICE=openai          # openai, google, libre, mock
GOOGLE_TRANSLATE_API_KEY=your_key
LIBRE_TRANSLATE_URL=http://localhost:5000

# Azure AI Services
AZURE_AI_ENABLED=false
AZURE_TEXT_ANALYTICS_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_TEXT_ANALYTICS_KEY=your_key
```

## Deployment Configuration

### Docker Configuration

#### Single Container

```yaml
# docker-compose.yml
version: '3.8'
services:
  promptman:
    image: ghcr.io/makercorn/ai-prompt-manager:latest
    ports:
      - "7860:7860"
    environment:
      - MULTITENANT_MODE=false
      - OPENAI_API_KEY=sk-your-key
    volumes:
      - ./data:/app/data
```

#### Production Stack

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    image: ghcr.io/makercorn/ai-prompt-manager:latest
    ports:
      - "7860:7860"
      - "7861:7861"
    environment:
      - MULTITENANT_MODE=true
      - ENABLE_API=true
      - DB_TYPE=postgres
      - POSTGRES_DSN=postgresql://promptman:${POSTGRES_PASSWORD}@db:5432/promptman
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=promptman
      - POSTGRES_USER=promptman
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Cloud Deployment

#### Railway

```toml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
```

#### Heroku

```yaml
# app.json
{
  "name": "AI Prompt Manager",
  "description": "Comprehensive AI prompt management system",
  "repository": "https://github.com/makercorn/ai-prompt-manager",
  "keywords": ["ai", "prompts", "management"],
  "env": {
    "OPENAI_API_KEY": {
      "description": "OpenAI API key for AI services"
    },
    "SECRET_KEY": {
      "description": "Secret key for session management",
      "generator": "secret"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "standard-1x"
    }
  },
  "addons": [
    "heroku-postgresql:standard-0"
  ]
}
```

#### AWS ECS

```json
{
  "family": "promptman",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "promptman",
      "image": "ghcr.io/makercorn/ai-prompt-manager:latest",
      "portMappings": [
        {
          "containerPort": 7860,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MULTITENANT_MODE",
          "value": "true"
        },
        {
          "name": "DB_TYPE",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ]
    }
  ]
}
```

## Database Configuration

### SQLite (Development)

```bash
# Default configuration - no setup required
DB_TYPE=sqlite
DB_PATH=prompts.db
```

**Features:**
- Zero configuration
- File-based storage
- Perfect for development
- Automatic migrations

### PostgreSQL (Production)

```bash
# Database setup
createdb promptman
createuser promptman --password

# Configuration
DB_TYPE=postgres
POSTGRES_DSN=postgresql://promptman:password@localhost:5432/promptman
```

**Production PostgreSQL Setup:**

```sql
-- Create database and user
CREATE DATABASE promptman;
CREATE USER promptman WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE promptman TO promptman;

-- Enable required extensions
\c promptman
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Database Migrations

```bash
# Automatic migrations on startup
poetry run python run.py

# Manual migration check
poetry run python -c "
from prompt_data_manager import PromptDataManager
db = PromptDataManager()
db.ensure_schema()
print('✅ Database schema updated')
"
```

## Security Configuration

### Authentication

```bash
# Multi-tenant mode
MULTITENANT_MODE=true
SECRET_KEY=your-256-bit-secret-key
SESSION_TIMEOUT=86400              # 24 hours

# Single-user mode (no auth)
MULTITENANT_MODE=false
```

### API Security

```bash
# API token configuration
API_TOKEN_EXPIRY=2592000           # 30 days (0 for no expiry)
API_RATE_LIMIT=1000                # Requests per hour per token
```

### HTTPS Configuration

```bash
# SSL/TLS configuration
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
FORCE_HTTPS=true
```

### CORS Configuration

```bash
# Cross-origin resource sharing
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_CREDENTIALS=true
```

### Security Headers

```bash
# Security headers
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'
X_FRAME_OPTIONS=DENY
```

## Advanced Configuration

### Logging

```bash
# Logging configuration
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=structured              # structured, simple
LOG_FILE=logs/promptman.log
LOG_ROTATION=daily
```

### Performance

```bash
# Performance tuning
CACHE_TYPE=redis                   # redis, memory, none
REDIS_URL=redis://localhost:6379
CACHE_TIMEOUT=3600                 # 1 hour

# Database connection pooling
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### Monitoring

```bash
# Health check configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PATH=/health

# Metrics collection
METRICS_ENABLED=true
METRICS_PORT=9090
PROMETHEUS_ENDPOINT=/metrics
```

### Backup Configuration

```bash
# Automatic backups
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *          # Daily at 2 AM
BACKUP_RETENTION=30                # Keep 30 days
BACKUP_S3_BUCKET=promptman-backups
```

## Configuration Validation

### Validation Script

```bash
# Validate configuration
poetry run python -c "
import os
from src.core.config.settings import AppConfig

try:
    config = AppConfig()
    print('✅ Configuration valid')
    print(f'Database: {config.database.type}')
    print(f'Mode: {"Multi-tenant" if not config.single_user_mode else "Single-user"}')
    print(f'API: {"Enabled" if config.api_enabled else "Disabled"}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

### Health Check

```bash
# Check system health
curl http://localhost:7860/health

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "ai_services": "configured",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Troubleshooting

### Common Issues

#### Database Connection
```bash
# Test database connection
poetry run python -c "
from prompt_data_manager import PromptDataManager
try:
    db = PromptDataManager()
    db.get_prompts()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### AI Service Configuration
```bash
# Test AI services
poetry run python -c "
from langwatch_optimizer import PromptOptimizer
try:
    optimizer = PromptOptimizer()
    result = optimizer.optimize_prompt('test prompt')
    print('✅ AI services working')
except Exception as e:
    print(f'❌ AI service error: {e}')
"
```

#### Port Conflicts
```bash
# Check port usage
lsof -i :7860
netstat -tulpn | grep 7860

# Use different port
poetry run python run.py --port 8080
```

### Configuration Best Practices

1. **Use environment variables** for sensitive configuration
2. **Validate configuration** before deployment
3. **Use strong secrets** for production deployments
4. **Enable HTTPS** in production
5. **Configure proper logging** for monitoring
6. **Set up automated backups** for important data
7. **Monitor resource usage** and performance
8. **Keep API keys secure** and rotate regularly

---

*This configuration guide covers all aspects of setting up and configuring the AI Prompt Manager. For deployment-specific instructions, see the deployment documentation.*