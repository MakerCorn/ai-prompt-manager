# Multi-Tenant AI Prompt Manager

A secure, multi-tenant AI prompt management system with authentication, SSO/ADFS support, and comprehensive admin capabilities.

## 🌟 Features

### 🔐 Authentication & Security
- **Email/Password Authentication**: Secure user login with hashed passwords
- **SSO/ADFS Support**: Integration with Microsoft Azure AD and other SAML providers
- **JWT Session Management**: Secure, expiring session tokens
- **Role-Based Access Control**: Admin, User, and Read-only roles
- **Tenant Isolation**: Complete data separation between organizations

### 🏢 Multi-Tenant Architecture
- **Tenant Management**: Create and manage multiple organizations
- **User Management**: Per-tenant user creation and role assignment
- **Data Isolation**: Prompts, configurations, and users are tenant-specific
- **Scalable Design**: Supports SQLite for development and PostgreSQL for production

### 🛡️ Admin Features
- **System Administration**: Comprehensive admin panel for tenant and user management
- **User Analytics**: View and manage users across all tenants
- **Tenant Configuration**: Set user limits and manage tenant settings
- **Audit Capabilities**: Track user creation and tenant activity

### 🚀 Enhanced Prompt Management
- **Tenant-Aware Prompts**: All prompts are isolated to your organization
- **User Attribution**: Track which user created each prompt
- **Enhanced Search**: Find prompts within your tenant's workspace
- **Category Organization**: Organize prompts by category within your tenant

## 📋 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (recommended) or pip
- Optional: PostgreSQL for production deployment

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd ai-prompt-manager
cp .env.example .env
```

2. **Install Dependencies**
```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

3. **Configure Environment**
Edit `.env` file with your settings:
```env
# Database
DB_TYPE=sqlite
DB_PATH=prompts.db

# Authentication
SECRET_KEY=your-secure-secret-key
LOCAL_DEV_MODE=true

# SSO (optional)
SSO_ENABLED=false
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
```

4. **Launch Application**
```bash
# Multi-tenant version
python run_mt.py

# Or original single-user version
python prompt_manager.py
```

## 🔑 Default Credentials

For local development, the system automatically creates:
- **Tenant**: `localhost`
- **Admin User**: `admin@localhost`
- **Password**: `admin123`

## 📱 Usage

### 1. Login
- Access the application at `http://localhost:7860`
- Use email/password or SSO to authenticate
- Admin users see additional admin panel

### 2. Prompt Management
- Create, edit, and delete prompts within your tenant
- Organize prompts by category and tags
- All prompts are isolated to your organization

### 3. AI Service Configuration
- Configure per-user AI service settings
- Support for OpenAI, LM Studio, Ollama, and Llama.cpp
- Separate enhancement service configuration

### 4. Admin Functions (Admin Only)
- **Tenant Management**: Create new organizations
- **User Management**: Add users to tenants with appropriate roles
- **System Overview**: Monitor tenant and user activity

## 🏗️ Architecture

### Database Schema
```
tenants
├── id (UUID)
├── name
├── subdomain
├── max_users
└── created_at

users
├── id (UUID)
├── tenant_id (FK)
├── email
├── password_hash
├── first_name, last_name
├── role (admin|user|readonly)
├── sso_id (optional)
└── created_at

prompts
├── id
├── tenant_id (FK)
├── user_id (FK)
├── name (unique per tenant)
├── title, content, category, tags
├── is_enhancement_prompt
└── created_at, updated_at

config
├── id
├── tenant_id (FK)
├── user_id (FK)
├── key, value
└── created_at
```

### Security Features
- **PBKDF2 Password Hashing**: Secure password storage
- **JWT Tokens**: Stateless session management with expiration
- **Tenant Isolation**: Row-level security for all data
- **Role-Based Access**: Granular permission control
- **Session Validation**: Automatic token validation and renewal

## 🔧 Configuration

### Database Options

**SQLite (Development)**
```env
DB_TYPE=sqlite
DB_PATH=prompts.db
```

**PostgreSQL (Production)**
```env
DB_TYPE=postgres
POSTGRES_DSN=postgresql://user:pass@localhost:5432/dbname
```

### SSO Configuration

**Microsoft Azure AD**
```env
SSO_ENABLED=true
SSO_CLIENT_ID=your-application-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
SSO_REDIRECT_URI=http://localhost:7860/auth/callback
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TYPE` | Database type (sqlite/postgres) | sqlite |
| `DB_PATH` | SQLite database path | prompts.db |
| `POSTGRES_DSN` | PostgreSQL connection string | - |
| `SECRET_KEY` | JWT signing secret | random |
| `LOCAL_DEV_MODE` | Enable local development features | false |
| `SSO_ENABLED` | Enable SSO authentication | false |
| `SERVER_HOST` | Server bind address | 0.0.0.0 |
| `SERVER_PORT` | Server port | 7860 |

## 🐳 Docker Deployment

1. **Build and Run**
```bash
docker-compose up -d
```

2. **PostgreSQL Configuration**
```yaml
# Uncomment in docker-compose.yml
environment:
  DB_TYPE: postgres
  POSTGRES_DSN: postgresql://prompt_user:password@postgres:5432/ai_prompt_manager
```

3. **Production Security**
```yaml
environment:
  SECRET_KEY: your-production-secret-key
  LOCAL_DEV_MODE: "false"
  SSO_ENABLED: "true"
```

## 🔍 API Reference

### Authentication Flow
1. User submits credentials to login endpoint
2. Server validates credentials against tenant database
3. JWT token generated with user/tenant context
4. Token included in subsequent requests
5. Server validates token and loads user context

### Session Management
- **Token Expiry**: 24 hours by default
- **Automatic Refresh**: Client handles token renewal
- **Secure Storage**: Tokens stored securely in client
- **Logout**: Invalidates server-side session record

## 🛠️ Development

### File Structure
```
ai-prompt-manager/
├── auth_manager.py           # Authentication and user management
├── prompt_data_manager.py    # Multi-tenant data access layer
├── prompt_manager_mt.py      # Main multi-tenant application
├── prompt_manager.py         # Original single-user version
├── run_mt.py                # Multi-tenant launcher
├── docker-compose.yml       # Docker deployment
├── .env.example            # Environment configuration template
└── README_MultiTenant.md   # This file
```

### Adding New Features
1. **Database Changes**: Update `PromptDataManager` with tenant-aware queries
2. **Authentication**: Extend `AuthManager` for new auth methods
3. **UI Components**: Add to `prompt_manager_mt.py` with proper auth checks
4. **Admin Features**: Ensure proper role validation

### Testing
```bash
# Install test dependencies
poetry install --with dev

# Run tests
python -m pytest tests/

# Test multi-tenant isolation
python -m pytest tests/test_tenant_isolation.py
```

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Set LOCAL_DEV_MODE=false
- [ ] Use PostgreSQL database
- [ ] Configure HTTPS/TLS
- [ ] Set up SSO/ADFS properly
- [ ] Configure firewall rules
- [ ] Set up backup procedures
- [ ] Monitor application logs

### Performance Optimization
- Use PostgreSQL with connection pooling
- Configure reverse proxy (nginx/Apache)
- Set up monitoring and alerting
- Implement database backup strategy
- Configure log rotation

### Scaling Considerations
- Database connection pooling
- Load balancer configuration
- Session storage (Redis for multi-instance)
- File storage (shared filesystem or S3)
- Container orchestration (Kubernetes)

## 📞 Support

For issues and feature requests:
1. Check existing documentation
2. Search closed issues
3. Create new issue with details
4. Provide environment information

## 📄 License

MIT License - see LICENSE file for details.

---

**🔐 Secure • 🏢 Multi-Tenant • 🚀 Scalable**