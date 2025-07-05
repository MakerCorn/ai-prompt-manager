# 🚀 AI Prompt Manager - Deployment Guide

This comprehensive guide covers all deployment scenarios for the AI Prompt Manager, from development to production environments.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Deployment Modes](#-deployment-modes)
- [Environment Configuration](#-environment-configuration)
- [Docker Deployment](#-docker-deployment)
- [Production Deployment](#-production-deployment)
- [Cloud Deployment](#-cloud-deployment)
- [Security Configuration](#-security-configuration)
- [Monitoring & Logging](#-monitoring--logging)
- [Troubleshooting](#-troubleshooting)

## 🎯 Quick Start

### PyPI Installation (Recommended)

```bash
# Install from PyPI
pip install promptman

# Run the application
python -m promptman

# Access the application
# Web UI: http://localhost:7860
# Default login: admin@localhost / admin123
```

### Poetry Development Setup

```bash
# Clone and setup
git clone https://github.com/MakerCorn/ai-prompt-manager.git
cd ai-prompt-manager
poetry install

# CRITICAL: Always use Poetry environment
poetry run python run.py

# Access the application
# Web UI: http://localhost:7860
```

## 🔧 Deployment Modes

### Single-User Mode

**Best for**: Personal use, development, small teams

```bash
# Poetry
poetry run python run.py --single-user

# PyPI
python -m promptman --single-user

# Docker
docker run -p 7860:7860 -e MULTITENANT_MODE=false ghcr.io/makercorn/ai-prompt-manager:latest
```

**Features:**
- No authentication required
- SQLite database (file-based)
- Single port operation (7860)
- Simplified interface

### Multi-Tenant Mode (Default)

**Best for**: Organizations, multiple users, production

```bash
# Poetry
poetry run python run.py

# PyPI  
python -m promptman

# Docker
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest
```

**Features:**
- Authentication required
- Tenant isolation
- Admin panel available
- PostgreSQL support
- User management

### API-Enabled Mode

**Best for**: Integration with other systems, automation

```bash
# Poetry
poetry run python run.py --with-api

# PyPI
python -m promptman --with-api

# Docker
docker run -p 7860:7860 -p 7861:7861 -e ENABLE_API=true ghcr.io/makercorn/ai-prompt-manager:latest
```

**Features:**
- Dual-server architecture
- Web UI: Port 7860
- API Server: Port 7861
- Interactive API docs at `/docs`
- Token-based authentication

## 🌍 Environment Configuration

### Core Settings

```bash
# Application Mode
MULTITENANT_MODE=true          # Enable multi-tenant (default: true)
ENABLE_API=false               # Enable REST API endpoints (default: false)
LOCAL_DEV_MODE=true            # Development features (default: true)

# Server Configuration
SERVER_HOST=0.0.0.0           # Bind address (default: 0.0.0.0)  
SERVER_PORT=7860              # Main port (default: 7860)
DEBUG=false                   # Debug mode (default: false)

# Security
SECRET_KEY=auto-generated     # JWT signing secret (auto-generated)
SESSION_TIMEOUT=3600          # Session timeout in seconds (default: 3600)

# Database
DB_TYPE=sqlite                # sqlite or postgres (default: sqlite)
DB_PATH=prompts.db            # SQLite path (default: prompts.db)
POSTGRES_DSN=postgresql://user:pass@host:port/db  # PostgreSQL connection
```

### AI Service Integration

```bash
# Prompt Optimization Services
PROMPT_OPTIMIZER=langwatch              # langwatch, promptperfect, builtin
LANGWATCH_API_KEY=your_key             # LangWatch API key
PROMPTPERFECT_API_KEY=your_key         # PromptPerfect API key

# Translation Services
TRANSLATION_SERVICE=openai              # openai, google, libre, mock
OPENAI_API_KEY=your_key                # OpenAI API key
GOOGLE_TRANSLATE_API_KEY=your_key      # Google Translate API key

# Azure AI Services (Optional)
AZURE_AI_ENABLED=false                 # Enable Azure AI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your_key              # Azure OpenAI key
AZURE_OPENAI_VERSION=2023-12-01-preview

# Token Calculation
TOKEN_CALCULATOR_ENABLED=true          # Enable token calculation
DEFAULT_MODEL=gpt-4                    # Default model for calculations
```

### Authentication & SSO

```bash
# Authentication
AUTH_ENABLED=true                      # Enable authentication (multi-tenant)
ALLOW_REGISTRATION=true                # Allow user registration
REQUIRE_EMAIL_VERIFICATION=false       # Email verification requirement

# SSO/ADFS Integration
SSO_ENABLED=false                      # Enable SSO
SSO_PROVIDER=adfs                      # SSO provider (adfs, azure, google)
SSO_CLIENT_ID=your_client_id           # SSO client ID
SSO_CLIENT_SECRET=your_secret          # SSO client secret
SSO_REDIRECT_URI=http://localhost:7860/auth/callback
SSO_AUTHORITY=https://your-adfs-server/adfs
```

## 🐳 Docker Deployment

### Single Container Deployment

```bash
# Basic deployment
docker run -d \
  --name ai-prompt-manager \
  -p 7860:7860 \
  -v prompt_data:/app/data \
  ghcr.io/makercorn/ai-prompt-manager:latest

# With API enabled
docker run -d \
  --name ai-prompt-manager \
  -p 7860:7860 \
  -p 7861:7861 \
  -e ENABLE_API=true \
  -v prompt_data:/app/data \
  ghcr.io/makercorn/ai-prompt-manager:latest

# With environment configuration
docker run -d \
  --name ai-prompt-manager \
  -p 7860:7860 \
  -e MULTITENANT_MODE=true \
  -e SECRET_KEY=your-secret-key \
  -e LANGWATCH_API_KEY=your-langwatch-key \
  -v prompt_data:/app/data \
  ghcr.io/makercorn/ai-prompt-manager:latest
```

### Docker Compose - Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: ghcr.io/makercorn/ai-prompt-manager:latest
    ports:
      - "7860:7860"    # FastAPI Web UI
      - "7861:7861"    # API Server (when enabled)
    environment:
      - MULTITENANT_MODE=true
      - ENABLE_API=true
      - SECRET_KEY=dev-secret-key-change-in-production
      - LANGWATCH_API_KEY=${LANGWATCH_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    volumes:
      - prompt_data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  prompt_data:
```

### Docker Compose - Production

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
      - POSTGRES_DSN=postgresql://promptman:${DB_PASSWORD}@db:5432/promptman
      - SECRET_KEY=${SECRET_KEY}
      - LANGWATCH_API_KEY=${LANGWATCH_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOCAL_DEV_MODE=false
    volumes:
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=promptman
      - POSTGRES_USER=promptman
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U promptman -d promptman"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

## 🏭 Production Deployment

### Prerequisites

```bash
# System requirements
# - CPU: 2+ cores
# - RAM: 4GB+ (8GB recommended)
# - Storage: 10GB+ SSD
# - OS: Linux (Ubuntu 20.04+ recommended)

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Create production directories
sudo mkdir -p /opt/ai-prompt-manager/{data,logs,backups,config}
sudo chown -R $USER:$USER /opt/ai-prompt-manager
```

### Production Environment Setup

```bash
# Create environment file
cat > /opt/ai-prompt-manager/.env << EOF
# Database
DB_PASSWORD=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)

# AI Services (set your actual keys)
LANGWATCH_API_KEY=your_langwatch_key_here
OPENAI_API_KEY=your_openai_key_here
PROMPTPERFECT_API_KEY=your_promptperfect_key_here

# Azure (if using)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your_azure_key_here

# Optional: SSO Configuration
SSO_ENABLED=false
SSO_CLIENT_ID=your_sso_client_id
SSO_CLIENT_SECRET=your_sso_secret
EOF

# Secure the environment file
chmod 600 /opt/ai-prompt-manager/.env
```

### Production Deployment Script

```bash
#!/bin/bash
# deploy-production.sh

set -e

DEPLOY_DIR="/opt/ai-prompt-manager"
cd $DEPLOY_DIR

echo "🚀 Deploying AI Prompt Manager to Production"

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Create backup if database exists
if docker volume inspect ai-prompt-manager_postgres_data >/dev/null 2>&1; then
    echo "💾 Creating database backup..."
    docker-compose -f docker-compose.prod.yml exec -T db \
        pg_dump -U promptman promptman > backups/backup-$(date +%Y%m%d-%H%M%S).sql
fi

# Deploy with zero-downtime
echo "🔄 Deploying with rolling update..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Wait for health check
echo "🏥 Waiting for health checks..."
sleep 30

# Verify deployment
if curl -f http://localhost:7860/health >/dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 Web UI: http://localhost:7860"
    echo "🔌 API: http://localhost:7861"
    echo "📊 API Docs: http://localhost:7861/docs"
else
    echo "❌ Deployment failed - health check failed"
    echo "📋 Recent logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20 app
    exit 1
fi

# Cleanup old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "🎉 Production deployment completed successfully!"
```

### Systemd Service (Optional)

```ini
# /etc/systemd/system/ai-prompt-manager.service
[Unit]
Description=AI Prompt Manager
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ai-prompt-manager
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ai-prompt-manager
sudo systemctl start ai-prompt-manager
sudo systemctl status ai-prompt-manager
```

## ☁️ Cloud Deployment

### AWS ECS Deployment

```json
{
  "family": "ai-prompt-manager",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "ai-prompt-manager",
      "image": "ghcr.io/makercorn/ai-prompt-manager:latest",
      "portMappings": [
        {
          "containerPort": 7860,
          "protocol": "tcp"
        },
        {
          "containerPort": 7861,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MULTITENANT_MODE",
          "value": "true"
        },
        {
          "name": "ENABLE_API",
          "value": "true"
        },
        {
          "name": "DB_TYPE",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:prompt-manager/secret-key"
        },
        {
          "name": "POSTGRES_DSN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:prompt-manager/db-dsn"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-prompt-manager",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:7860/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-prompt-manager
  labels:
    app: ai-prompt-manager
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-prompt-manager
  template:
    metadata:
      labels:
        app: ai-prompt-manager
    spec:
      containers:
      - name: ai-prompt-manager
        image: ghcr.io/makercorn/ai-prompt-manager:latest
        ports:
        - containerPort: 7860
          name: web-ui
        - containerPort: 7861
          name: api
        env:
        - name: MULTITENANT_MODE
          value: "true"
        - name: ENABLE_API
          value: "true"
        - name: DB_TYPE
          value: "postgres"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-prompt-manager-secrets
              key: secret-key
        - name: POSTGRES_DSN
          valueFrom:
            secretKeyRef:
              name: ai-prompt-manager-secrets
              key: postgres-dsn
        livenessProbe:
          httpGet:
            path: /health
            port: 7860
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 7860
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: ai-prompt-manager-service
spec:
  selector:
    app: ai-prompt-manager
  ports:
  - name: web-ui
    port: 80
    targetPort: 7860
  - name: api
    port: 8080
    targetPort: 7861
  type: LoadBalancer
```

## 🔒 Security Configuration

### SSL/TLS Setup (Nginx Reverse Proxy)

```nginx
# /etc/nginx/sites-available/ai-prompt-manager
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Web UI
    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API
    location /api/ {
        proxy_pass http://localhost:7861;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

### Secret Management

```bash
# Generate secure secrets
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)

# Store in environment or secret management system
echo "SECRET_KEY=$SECRET_KEY" >> /opt/ai-prompt-manager/.env
echo "DB_PASSWORD=$DB_PASSWORD" >> /opt/ai-prompt-manager/.env

# Secure the file
chmod 600 /opt/ai-prompt-manager/.env
chown root:root /opt/ai-prompt-manager/.env
```

## 📊 Monitoring & Logging

### Logging Configuration

```yaml
# Add to docker-compose.prod.yml
services:
  app:
    # ... existing config
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    volumes:
      - ./logs:/app/logs
```

### Health Check Monitoring

```bash
#!/bin/bash
# health-monitor.sh

HEALTH_URL="http://localhost:7860/health"
API_HEALTH_URL="http://localhost:7861/api/health"
WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL"

check_service() {
    local url=$1
    local service_name=$2
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $service_name is healthy"
        return 0
    else
        echo "❌ $service_name is unhealthy"
        # Send alert
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 AI Prompt Manager $service_name is down!\"}" \
            "$WEBHOOK_URL"
        return 1
    fi
}

check_service "$HEALTH_URL" "Web UI"
check_service "$API_HEALTH_URL" "API"
```

### Prometheus Metrics (Advanced)

```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

## 🔧 Troubleshooting

### Common Issues

**1. "Create New Prompt" Internal Server Error**
```bash
# Problem: Dependencies not properly resolved
# Solution: Always use Poetry environment
poetry run python run.py  # ✅ Correct
python run.py             # ❌ May cause issues
```

**2. API Server Not Starting**
```bash
# Check if port is in use
lsof -i :7861

# Verify API is enabled
export ENABLE_API=true
poetry run python run.py --with-api --debug
```

**3. Database Connection Issues**
```bash
# Check PostgreSQL connection
docker-compose exec db psql -U promptman -d promptman -c "SELECT 1;"

# Reset SQLite database
rm prompts.db
poetry run python run.py  # Will recreate database
```

**4. Docker Permission Issues**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 /opt/ai-prompt-manager/data
```

**5. SSL Certificate Issues**
```bash
# Renew Let's Encrypt certificates
sudo certbot renew
sudo systemctl reload nginx
```

### Debug Mode

```bash
# Enable debug mode for detailed error information
poetry run python run.py --debug

# Or via environment
export DEBUG=true
poetry run python run.py
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# Search for errors
docker-compose logs app | grep -i error

# View system resource usage
docker stats
```

### Performance Tuning

```bash
# Optimize PostgreSQL
cat >> /opt/ai-prompt-manager/postgresql.conf << EOF
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 64MB
maintenance_work_mem = 256MB
EOF

# Optimize for high concurrency
export WORKERS=4
export MAX_CONNECTIONS=100
```

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**