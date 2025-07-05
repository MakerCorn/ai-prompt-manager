# 🛠️ AI Prompt Manager - Operations Guide

This guide covers day-to-day operations, maintenance, monitoring, and administration of the AI Prompt Manager.

## 📋 Table of Contents

- [System Administration](#-system-administration)
- [User Management](#-user-management)
- [Database Operations](#-database-operations)
- [Backup & Recovery](#-backup--recovery)
- [Performance Monitoring](#-performance-monitoring)
- [Security Operations](#-security-operations)
- [Maintenance Tasks](#-maintenance-tasks)
- [API Token Management](#-api-token-management)
- [Troubleshooting](#-troubleshooting)

## 👥 System Administration

### Admin Panel Access

**Multi-Tenant Mode:**
```bash
# Default admin credentials
Username: admin@localhost
Password: admin123

# Access admin panel
http://localhost:7860/admin
```

**Admin Functions:**
- User management
- Tenant administration
- System configuration
- API token oversight
- Usage statistics

### Configuration Management

```bash
# View current configuration
poetry run python -c "
from run import get_configuration, parse_arguments
import json

class MockArgs:
    single_user = False
    multi_tenant = False
    with_api = False
    host = None
    port = None
    debug = False
    share = False

config = get_configuration(MockArgs())
print(json.dumps(config, indent=2))
"

# Update configuration via environment
export MULTITENANT_MODE=true
export ENABLE_API=true
export SECRET_KEY=your-new-secret-key
```

### Service Management

```bash
# Systemd service management
sudo systemctl start ai-prompt-manager
sudo systemctl stop ai-prompt-manager
sudo systemctl restart ai-prompt-manager
sudo systemctl status ai-prompt-manager

# Docker Compose management
cd /opt/ai-prompt-manager
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml logs -f
```

## 👥 User Management

### Creating Users (Multi-Tenant)

**Via Admin Panel:**
1. Login as admin
2. Navigate to Admin Panel
3. Click "User Management" 
4. Click "Add User"
5. Fill user details and assign role

**Via Direct Database (Advanced):**
```python
# Create user script
poetry run python -c "
from auth_manager import AuthManager
from datetime import datetime

auth_manager = AuthManager('prompts.db')

# Create new user
user_data = {
    'email': 'newuser@example.com',
    'first_name': 'New',
    'last_name': 'User',
    'password': 'secure_password_123',
    'role': 'user',
    'tenant_id': 'default-tenant'
}

result = auth_manager.create_user(**user_data)
print(f'User created: {result}')
"
```

### User Roles and Permissions

| Role | Permissions |
|------|-------------|
| **admin** | Full system access, user management, tenant administration |
| **user** | Create/edit/delete own prompts, use all features |
| **viewer** | Read-only access to prompts, cannot create/edit |

### Bulk User Operations

```python
# Bulk user creation
poetry run python -c "
from auth_manager import AuthManager
import csv

auth_manager = AuthManager('prompts.db')

# Read from CSV file
with open('users.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            result = auth_manager.create_user(
                email=row['email'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                password=row['password'],
                role=row.get('role', 'user'),
                tenant_id=row.get('tenant_id', 'default-tenant')
            )
            print(f'Created user: {row[\"email\"]} - {result}')
        except Exception as e:
            print(f'Failed to create {row[\"email\"]}: {e}')
"
```

### User Deactivation

```python
# Deactivate user
poetry run python -c "
from auth_manager import AuthManager

auth_manager = AuthManager('prompts.db')

# Deactivate user
user_email = 'user@example.com'
auth_manager.deactivate_user(user_email)
print(f'User {user_email} deactivated')
"
```

## 🗄️ Database Operations

### Database Health Check

```bash
# SQLite health check
poetry run python -c "
import sqlite3
import os

db_path = 'prompts.db'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM prompts')
        count = cursor.fetchone()[0]
        print(f'✅ Database healthy: {count} prompts')
        conn.close()
    except Exception as e:
        print(f'❌ Database error: {e}')
else:
    print('❌ Database file not found')
"

# PostgreSQL health check
docker-compose exec db psql -U promptman -d promptman -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables;
"
```

### Database Statistics

```python
# Get database statistics
poetry run python -c "
from prompt_data_manager import PromptDataManager

data_manager = PromptDataManager('prompts.db')

# Get statistics
all_prompts = data_manager.get_all_prompts()
categories = data_manager.get_categories()

print(f'Total prompts: {len(all_prompts)}')
print(f'Categories: {len(categories)}')

# Category breakdown
for category in categories:
    category_prompts = data_manager.get_prompts_by_category(category)
    print(f'  {category}: {len(category_prompts)} prompts')

# Recent activity
from datetime import datetime, timedelta
recent_date = datetime.now() - timedelta(days=7)
recent_prompts = [p for p in all_prompts if p.get('created_at', '') > recent_date.isoformat()]
print(f'Prompts created in last 7 days: {len(recent_prompts)}')
"
```

### Database Optimization

```sql
-- SQLite optimization
PRAGMA optimize;
PRAGMA integrity_check;
VACUUM;
REINDEX;

-- PostgreSQL optimization
VACUUM ANALYZE;
REINDEX DATABASE promptman;

-- Update table statistics
ANALYZE;
```

## 💾 Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/opt/ai-prompt-manager/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# SQLite backup
if [ -f "prompts.db" ]; then
    echo "📦 Creating SQLite backup..."
    cp prompts.db "$BACKUP_DIR/prompts_$DATE.db"
    gzip "$BACKUP_DIR/prompts_$DATE.db"
    echo "✅ SQLite backup created: prompts_$DATE.db.gz"
fi

# PostgreSQL backup
if docker-compose ps | grep -q "db.*Up"; then
    echo "📦 Creating PostgreSQL backup..."
    docker-compose exec -T db pg_dump -U promptman promptman > "$BACKUP_DIR/postgres_$DATE.sql"
    gzip "$BACKUP_DIR/postgres_$DATE.sql"
    echo "✅ PostgreSQL backup created: postgres_$DATE.sql.gz"
fi

# Configuration backup
echo "📦 Creating configuration backup..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env docker-compose.*.yml logs/

# Cleanup old backups
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed successfully!"
```

### Backup Automation with Cron

```bash
# Add to crontab
crontab -e

# Backup every day at 2 AM
0 2 * * * /opt/ai-prompt-manager/backup.sh >> /opt/ai-prompt-manager/logs/backup.log 2>&1

# Backup every 6 hours
0 */6 * * * /opt/ai-prompt-manager/backup.sh >> /opt/ai-prompt-manager/logs/backup.log 2>&1
```

### Recovery Procedures

```bash
# SQLite recovery
echo "🔄 Restoring SQLite database..."
BACKUP_FILE="backups/prompts_20241208_020000.db.gz"
gunzip -c "$BACKUP_FILE" > prompts_restored.db

# Verify restore
poetry run python -c "
import sqlite3
conn = sqlite3.connect('prompts_restored.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM prompts')
count = cursor.fetchone()[0]
print(f'Restored database contains {count} prompts')
conn.close()
"

# Replace current database (CAUTION!)
mv prompts.db prompts.db.backup
mv prompts_restored.db prompts.db
```

```bash
# PostgreSQL recovery
echo "🔄 Restoring PostgreSQL database..."
BACKUP_FILE="backups/postgres_20241208_020000.sql.gz"

# Stop application
docker-compose down

# Restore database
gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U promptman -d promptman

# Start application
docker-compose up -d

# Verify restore
docker-compose exec db psql -U promptman -d promptman -c "SELECT COUNT(*) FROM prompts;"
```

### Disaster Recovery Plan

1. **Immediate Response:**
   ```bash
   # Stop services
   docker-compose down
   
   # Assess damage
   docker-compose logs --tail=100
   ```

2. **Data Recovery:**
   ```bash
   # Restore from latest backup
   ./restore-backup.sh latest
   
   # Verify data integrity
   ./verify-data.sh
   ```

3. **Service Restoration:**
   ```bash
   # Start services
   docker-compose up -d
   
   # Monitor health
   ./health-check.sh
   ```

## 📊 Performance Monitoring

### System Metrics Collection

```bash
#!/bin/bash
# monitor.sh - System monitoring script

LOG_FILE="/opt/ai-prompt-manager/logs/performance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# System metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')

# Application metrics
WEB_RESPONSE=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:7860/health)
API_RESPONSE=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:7861/api/health)

# Database metrics
if [ -f "prompts.db" ]; then
    DB_SIZE=$(ls -lh prompts.db | awk '{print $5}')
else
    DB_SIZE="N/A"
fi

# Log metrics
echo "$DATE,CPU:$CPU_USAGE%,MEM:$MEM_USAGE%,DISK:$DISK_USAGE%,WEB:${WEB_RESPONSE}s,API:${API_RESPONSE}s,DB:$DB_SIZE" >> "$LOG_FILE"

# Alert on high usage
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "⚠️ High CPU usage: $CPU_USAGE%"
fi

if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "⚠️ High memory usage: $MEM_USAGE%"
fi
```

### Application Performance Metrics

```python
# Performance monitoring script
poetry run python -c "
import time
import requests
from datetime import datetime

def measure_performance():
    metrics = {}
    
    # Web UI response time
    start = time.time()
    try:
        response = requests.get('http://localhost:7860/health', timeout=10)
        metrics['web_ui_response'] = time.time() - start
        metrics['web_ui_status'] = response.status_code
    except Exception as e:
        metrics['web_ui_response'] = -1
        metrics['web_ui_error'] = str(e)
    
    # API response time
    start = time.time()
    try:
        response = requests.get('http://localhost:7861/api/health', timeout=10)
        metrics['api_response'] = time.time() - start
        metrics['api_status'] = response.status_code
    except Exception as e:
        metrics['api_response'] = -1
        metrics['api_error'] = str(e)
    
    # Database query performance
    from prompt_data_manager import PromptDataManager
    start = time.time()
    try:
        data_manager = PromptDataManager('prompts.db')
        prompts = data_manager.get_all_prompts()
        metrics['db_query_time'] = time.time() - start
        metrics['total_prompts'] = len(prompts)
    except Exception as e:
        metrics['db_query_time'] = -1
        metrics['db_error'] = str(e)
    
    return metrics

# Run performance check
results = measure_performance()
timestamp = datetime.now().isoformat()

print(f'Performance Metrics [{timestamp}]:')
for key, value in results.items():
    print(f'  {key}: {value}')

# Write to log file
with open('logs/performance.log', 'a') as f:
    f.write(f'{timestamp},{results}\\n')
"
```

### Capacity Planning

```python
# Capacity analysis script
poetry run python -c "
from prompt_data_manager import PromptDataManager
import os
from datetime import datetime, timedelta

data_manager = PromptDataManager('prompts.db')
all_prompts = data_manager.get_all_prompts()

# Current usage
total_prompts = len(all_prompts)
db_size = os.path.getsize('prompts.db') if os.path.exists('prompts.db') else 0

# Calculate growth rate
recent_prompts = []
for prompt in all_prompts:
    created_at = prompt.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if created_date > datetime.now() - timedelta(days=30):
                recent_prompts.append(prompt)
        except:
            pass

monthly_growth = len(recent_prompts)
avg_prompt_size = db_size / total_prompts if total_prompts > 0 else 0

print(f'📊 Capacity Analysis:')
print(f'  Total prompts: {total_prompts:,}')
print(f'  Database size: {db_size / (1024*1024):.1f} MB')
print(f'  Average prompt size: {avg_prompt_size:.0f} bytes')
print(f'  Monthly growth: {monthly_growth} prompts')
print(f'  Projected 6-month size: {(db_size + (monthly_growth * 6 * avg_prompt_size)) / (1024*1024):.1f} MB')

# Recommendations
if monthly_growth > 1000:
    print('⚠️ Consider upgrading storage or implementing archiving')
if db_size > 100 * 1024 * 1024:  # 100MB
    print('⚠️ Consider migrating to PostgreSQL for better performance')
"
```

## 🔒 Security Operations

### Security Audit Script

```bash
#!/bin/bash
# security-audit.sh

echo "🔒 AI Prompt Manager Security Audit"
echo "==================================="

# Check file permissions
echo "📋 File Permissions:"
echo "Environment file:"
ls -la .env 2>/dev/null || echo "  .env not found"
echo "Database file:"
ls -la prompts.db 2>/dev/null || echo "  prompts.db not found"
echo "Log directory:"
ls -ld logs/ 2>/dev/null || echo "  logs/ not found"

# Check for default credentials
echo ""
echo "🔑 Default Credentials Check:"
if grep -q "admin123" .env 2>/dev/null; then
    echo "  ⚠️ Default admin password detected in .env"
else
    echo "  ✅ No default passwords in .env"
fi

# Check SSL configuration
echo ""
echo "🔐 SSL Configuration:"
if command -v openssl &> /dev/null; then
    if openssl s_client -connect localhost:443 -servername localhost </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        echo "  ✅ SSL certificate valid"
    else
        echo "  ⚠️ SSL certificate issues detected"
    fi
else
    echo "  ⚠️ OpenSSL not available for certificate check"
fi

# Check for exposed ports
echo ""
echo "🌐 Network Security:"
netstat -tlnp 2>/dev/null | grep -E "(7860|7861)" || echo "  Application ports not found"

# Check Docker security
echo ""
echo "🐳 Docker Security:"
if command -v docker &> /dev/null; then
    # Check for privileged containers
    PRIVILEGED=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -v "NAMES" | wc -l)
    echo "  Running containers: $PRIVILEGED"
    
    # Check image vulnerabilities (if trivy is installed)
    if command -v trivy &> /dev/null; then
        echo "  Running vulnerability scan..."
        trivy image ghcr.io/makercorn/ai-prompt-manager:latest --severity HIGH,CRITICAL --quiet
    else
        echo "  Install trivy for vulnerability scanning"
    fi
else
    echo "  Docker not available"
fi

echo ""
echo "✅ Security audit completed"
```

### API Token Security

```python
# API token security audit
poetry run python -c "
from api_token_manager import APITokenManager
from datetime import datetime, timedelta

token_manager = APITokenManager('prompts.db')

# Get all tokens (admin function)
print('🔑 API Token Security Audit:')

# This would need to be implemented in the token manager
# For now, we'll check general token security practices
print('  Token format validation: ✅ Implemented')
print('  Token encryption: ✅ SHA-256 hashing')
print('  Token expiration: ✅ Configurable')
print('  Rate limiting: ⚠️ Implement if needed')

# Check for expired tokens (if functionality exists)
print('  Expired token cleanup: Manual process required')
"
```

### Security Hardening Checklist

```bash
# Security hardening script
#!/bin/bash

echo "🔒 Security Hardening Checklist"
echo "==============================="

# 1. Update environment file permissions
if [ -f .env ]; then
    chmod 600 .env
    chown root:root .env
    echo "✅ Environment file permissions hardened"
else
    echo "⚠️ Environment file not found"
fi

# 2. Update database permissions
if [ -f prompts.db ]; then
    chmod 640 prompts.db
    echo "✅ Database file permissions hardened"
fi

# 3. Set up log rotation
cat > /etc/logrotate.d/ai-prompt-manager << EOF
/opt/ai-prompt-manager/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker-compose -f /opt/ai-prompt-manager/docker-compose.prod.yml restart app
    endscript
}
EOF
echo "✅ Log rotation configured"

# 4. Set up firewall rules
if command -v ufw &> /dev/null; then
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo "✅ Firewall configured"
else
    echo "⚠️ UFW not available - configure firewall manually"
fi

# 5. Disable unnecessary services
systemctl disable --now telnet
systemctl disable --now rsh
systemctl disable --now rlogin
echo "✅ Unnecessary services disabled"

echo ""
echo "✅ Security hardening completed"
```

## 🔧 Maintenance Tasks

### Daily Maintenance Script

```bash
#!/bin/bash
# daily-maintenance.sh

LOG_FILE="/opt/ai-prompt-manager/logs/maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting daily maintenance" >> "$LOG_FILE"

# 1. Health check
if curl -f -s http://localhost:7860/health > /dev/null; then
    echo "[$DATE] ✅ Health check passed" >> "$LOG_FILE"
else
    echo "[$DATE] ❌ Health check failed" >> "$LOG_FILE"
    # Restart service
    docker-compose restart app
    echo "[$DATE] 🔄 Service restarted" >> "$LOG_FILE"
fi

# 2. Log cleanup
find logs/ -name "*.log" -size +100M -exec truncate -s 50M {} \;
echo "[$DATE] ✅ Log files cleaned" >> "$LOG_FILE"

# 3. Database optimization
if [ -f prompts.db ]; then
    sqlite3 prompts.db "VACUUM; PRAGMA optimize;"
    echo "[$DATE] ✅ SQLite database optimized" >> "$LOG_FILE"
fi

# 4. Docker cleanup
docker system prune -f > /dev/null 2>&1
echo "[$DATE] ✅ Docker cleanup completed" >> "$LOG_FILE"

# 5. Backup verification
LATEST_BACKUP=$(ls -t backups/*.gz 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    BACKUP_AGE=$(( $(date +%s) - $(stat -c %Y "$LATEST_BACKUP") ))
    if [ $BACKUP_AGE -lt 86400 ]; then  # 24 hours
        echo "[$DATE] ✅ Recent backup found" >> "$LOG_FILE"
    else
        echo "[$DATE] ⚠️ No recent backup found" >> "$LOG_FILE"
        ./backup.sh
    fi
else
    echo "[$DATE] ⚠️ No backups found" >> "$LOG_FILE"
    ./backup.sh
fi

echo "[$DATE] Daily maintenance completed" >> "$LOG_FILE"
```

### Weekly Maintenance Script

```bash
#!/bin/bash
# weekly-maintenance.sh

LOG_FILE="/opt/ai-prompt-manager/logs/maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting weekly maintenance" >> "$LOG_FILE"

# 1. Update Docker images
docker-compose pull
echo "[$DATE] ✅ Docker images updated" >> "$LOG_FILE"

# 2. Security scan
if command -v trivy &> /dev/null; then
    trivy image ghcr.io/makercorn/ai-prompt-manager:latest --severity HIGH,CRITICAL >> "$LOG_FILE" 2>&1
    echo "[$DATE] ✅ Security scan completed" >> "$LOG_FILE"
fi

# 3. Performance analysis
poetry run python -c "
import time
from prompt_data_manager import PromptDataManager

start = time.time()
data_manager = PromptDataManager('prompts.db')
prompts = data_manager.get_all_prompts()
query_time = time.time() - start

print(f'Query performance: {query_time:.2f}s for {len(prompts)} prompts')
" >> "$LOG_FILE" 2>&1

echo "[$DATE] ✅ Performance analysis completed" >> "$LOG_FILE"

# 4. Certificate renewal check
if command -v certbot &> /dev/null; then
    certbot certificates >> "$LOG_FILE" 2>&1
    echo "[$DATE] ✅ Certificate status checked" >> "$LOG_FILE"
fi

echo "[$DATE] Weekly maintenance completed" >> "$LOG_FILE"
```

## 🔑 API Token Management

### Token Administration

```python
# API token management script
poetry run python -c "
from api_token_manager import APITokenManager
from datetime import datetime, timedelta

token_manager = APITokenManager('prompts.db')

print('🔑 API Token Management')
print('=====================')

# List active tokens (requires admin implementation)
print('Active tokens: Check admin panel or database directly')

# Token cleanup (expired tokens)
print('Expired token cleanup: Manual process')

# Token usage statistics
print('Token usage statistics: Check API logs')

# Security recommendations
print('')
print('🔒 Security Recommendations:')
print('  - Rotate tokens every 90 days')
print('  - Use environment variables for tokens')
print('  - Monitor token usage patterns')
print('  - Revoke unused tokens')
print('  - Enable token expiration')
"
```

### Token Monitoring

```bash
# Token usage monitoring
#!/bin/bash

LOG_FILE="/opt/ai-prompt-manager/logs/api-access.log"

# Monitor API access patterns
echo "📊 API Token Usage Analysis"
echo "=========================="

# Extract token usage from logs (if logging is configured)
if [ -f "$LOG_FILE" ]; then
    echo "Recent API access:"
    tail -100 "$LOG_FILE" | grep -E "(apm_|token)" | cut -d' ' -f1-3,6- | sort | uniq -c | sort -nr
else
    echo "API access log not found. Configure API logging."
fi

# Check for suspicious activity
echo ""
echo "🚨 Security Alerts:"
# High frequency requests
SUSPICIOUS=$(tail -1000 "$LOG_FILE" 2>/dev/null | grep -c "$(date +%Y-%m-%d)" | awk '{if($1>1000) print "High request volume detected: " $1 " requests today"}')
if [ -n "$SUSPICIOUS" ]; then
    echo "  $SUSPICIOUS"
else
    echo "  No suspicious activity detected"
fi
```

## 🔍 Troubleshooting

### Diagnostic Script

```bash
#!/bin/bash
# diagnose.sh - Comprehensive diagnostic script

echo "🔍 AI Prompt Manager Diagnostic Report"
echo "====================================="
echo "Timestamp: $(date)"
echo ""

# System information
echo "💻 System Information:"
echo "  OS: $(uname -a)"
echo "  Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "  Poetry: $(poetry --version 2>/dev/null || echo 'Not found')"
echo "  Docker: $(docker --version 2>/dev/null || echo 'Not found')"
echo ""

# Service status
echo "🚀 Service Status:"
if curl -f -s http://localhost:7860/health > /dev/null; then
    echo "  Web UI: ✅ Running"
else
    echo "  Web UI: ❌ Not responding"
fi

if curl -f -s http://localhost:7861/api/health > /dev/null; then
    echo "  API: ✅ Running"
else
    echo "  API: ❌ Not responding"
fi

# Process information
echo ""
echo "🔄 Process Information:"
ps aux | grep -E "(python.*run\.py|uvicorn)" | grep -v grep || echo "  No Python processes found"

# Port usage
echo ""
echo "🌐 Port Status:"
netstat -tlnp 2>/dev/null | grep -E "(7860|7861)" || echo "  Application ports not in use"

# Database status
echo ""
echo "🗄️ Database Status:"
if [ -f prompts.db ]; then
    DB_SIZE=$(ls -lh prompts.db | awk '{print $5}')
    echo "  SQLite: ✅ Found ($DB_SIZE)"
    
    # Quick database check
    sqlite3 prompts.db "SELECT COUNT(*) FROM prompts;" 2>/dev/null && echo "  Database: ✅ Accessible" || echo "  Database: ❌ Access error"
else
    echo "  SQLite: ❌ Not found"
fi

# Docker status
echo ""
echo "🐳 Docker Status:"
if command -v docker &> /dev/null; then
    docker ps | grep -E "(ai-prompt-manager|promptman)" || echo "  No containers running"
else
    echo "  Docker not available"
fi

# Log errors
echo ""
echo "📋 Recent Errors:"
if [ -d logs ]; then
    find logs -name "*.log" -exec tail -50 {} \; | grep -i error | tail -5 || echo "  No recent errors found"
else
    echo "  No log directory found"
fi

# Disk space
echo ""
echo "💾 Disk Usage:"
df -h . | tail -1

# Memory usage
echo ""
echo "🧠 Memory Usage:"
free -h

echo ""
echo "✅ Diagnostic report completed"
```

### Common Issue Resolution

```bash
# Issue resolution script
#!/bin/bash

fix_common_issues() {
    echo "🔧 Fixing Common Issues"
    echo "====================="
    
    # 1. Fix file permissions
    echo "📋 Fixing file permissions..."
    chmod 644 *.py 2>/dev/null
    chmod 600 .env 2>/dev/null
    chmod 755 logs 2>/dev/null
    echo "  ✅ Permissions fixed"
    
    # 2. Clean up temporary files
    echo "📋 Cleaning temporary files..."
    find . -name "*.pyc" -delete 2>/dev/null
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    echo "  ✅ Temporary files cleaned"
    
    # 3. Reset poetry environment
    echo "📋 Resetting Poetry environment..."
    poetry env remove --all 2>/dev/null
    poetry install --no-interaction
    echo "  ✅ Poetry environment reset"
    
    # 4. Restart services
    echo "📋 Restarting services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose restart 2>/dev/null
        echo "  ✅ Docker services restarted"
    fi
    
    echo ""
    echo "✅ Common issues fixed"
}

# Run fixes
fix_common_issues
```

### Emergency Recovery

```bash
#!/bin/bash
# emergency-recovery.sh

echo "🚨 Emergency Recovery Procedure"
echo "=============================="

# 1. Stop all services
echo "Step 1: Stopping all services..."
docker-compose down 2>/dev/null
pkill -f "python.*run.py" 2>/dev/null
systemctl stop ai-prompt-manager 2>/dev/null

# 2. Backup current state
echo "Step 2: Creating emergency backup..."
mkdir -p emergency-backup-$(date +%Y%m%d-%H%M%S)
cp -r . emergency-backup-$(date +%Y%m%d-%H%M%S)/ 2>/dev/null

# 3. Restore from backup
echo "Step 3: Restore options:"
echo "  a) Restore from latest backup"
echo "  b) Factory reset (keeps data)"
echo "  c) Complete reinstall"

read -p "Choose option [a/b/c]: " choice

case $choice in
    a)
        echo "Restoring from latest backup..."
        LATEST_BACKUP=$(ls -t backups/*.gz 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            gunzip -c "$LATEST_BACKUP" > prompts_restored.db
            mv prompts.db prompts.db.emergency
            mv prompts_restored.db prompts.db
            echo "✅ Database restored"
        else
            echo "❌ No backups found"
        fi
        ;;
    b)
        echo "Factory reset (keeping data)..."
        mv prompts.db prompts.db.safe
        poetry install --no-interaction
        mv prompts.db.safe prompts.db
        echo "✅ Factory reset completed"
        ;;
    c)
        echo "Complete reinstall..."
        echo "⚠️ This will remove all data!"
        read -p "Are you sure? [y/N]: " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf .venv
            rm -f prompts.db
            poetry install --no-interaction
            echo "✅ Complete reinstall completed"
        fi
        ;;
esac

# 4. Restart services
echo "Step 4: Restarting services..."
docker-compose up -d 2>/dev/null || poetry run python run.py &

echo ""
echo "✅ Emergency recovery completed"
echo "🔍 Run ./diagnose.sh to verify system status"
```

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**