# AI Prompt Manager

A comprehensive AI prompt management system with both single-user and multi-tenant architectures, featuring authentication, SSO/ADFS support, and admin capabilities.

## Development Commands

**Install dependencies:**
```bash
poetry install
```

**Run the original single-user application:**
```bash
poetry run python prompt_manager.py
```

**Run the multi-tenant application:**
```bash
poetry run python run_mt.py
```

**Run the multi-tenant application with API endpoints:**
```bash
poetry run python run_mt_with_api.py
```

**Test multi-tenant installation:**
```bash
poetry run python test_mt_install.py
```

**Docker build and run (Multi-tenant with API):**
```bash
# Build locally
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager

# Or use pre-built image from GitHub Container Registry
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest
```

**Docker compose for multi-tenant with PostgreSQL:**

```bash
docker-compose up -d
```

**Available Container Images:**

- **Latest**: `ghcr.io/OWNER/REPO:latest` (automatically built from main branch)
- **Tagged Releases**: `ghcr.io/OWNER/REPO:v1.0.0` (built from version tags)
- **Branch Builds**: `ghcr.io/OWNER/REPO:main` (specific branch builds)

**Docker containers include:**

- Multi-tenant web interface with authentication
- Complete REST API with OpenAPI documentation  
- SQLite database (or PostgreSQL with docker-compose)
- Health checks and secure token management
- LangWatch prompt optimization capabilities

## Architecture

This is a Gradio-based web application for managing AI prompts with both single-user and multi-tenant architectures:

### Single-User Version

- `prompt_manager.py` - Original single-user application
- `prompt_data_manager.py` - Database abstraction layer

### Multi-Tenant Version

- `prompt_manager_mt.py` - Multi-tenant application with authentication
- `auth_manager.py` - Authentication, user management, and SSO/ADFS support
- `prompt_data_manager.py` - Enhanced with tenant-aware data isolation
- `api_token_manager.py` - Secure API token management system
- `api_endpoints.py` - REST API endpoints for programmatic access
- `langwatch_optimizer.py` - LangWatch prompt optimization integration
- `run_mt.py` - Multi-tenant application launcher
- `run_mt_with_api.py` - Combined web UI and API server launcher

### Database Architecture

- **Single-User**: SQLite with local `prompts.db` file
- **Multi-Tenant**: SQLite or PostgreSQL with tenant isolation
- Database selection controlled by `.env` file with `DB_TYPE` and connection parameters

### Multi-Tenant Features

- **Authentication**: Email/password + SSO/ADFS support with JWT sessions
- **Tenant Isolation**: Complete data separation between organizations
- **User Management**: Role-based access (admin, user, readonly)
- **Admin Interface**: Tenant and user management for administrators
- **Data Security**: Row-level security and encrypted sessions
- **API Access**: Secure REST API with token-based authentication
- **Token Management**: Create, manage, and revoke API tokens with expiration
- **LangWatch Integration**: AI-powered prompt optimization with accept/reject workflow

### Key Features Architecture

- **Name-based prompt system**: All prompts require unique names (per tenant in MT)
- **Tenant-aware data access**: All operations respect tenant boundaries
- **Dual AI service configuration**: Separate configs for primary execution and prompt enhancement
- **Category-based organization**: Tree view display with category grouping
- **Enhancement system**: Uses different AI models to improve existing prompts

### Data Flow

**Single-User:**

1. `PromptDataManager` handles all database operations
2. `AIPromptManager` wraps data operations and adds AI service integration
3. Gradio interface functions bridge UI events to business logic

**Multi-Tenant:**

1. `AuthManager` handles authentication and user/tenant management
2. `PromptDataManager` initialized with tenant/user context for data isolation
3. `AIPromptManager` wraps authenticated operations
4. Gradio interface includes authentication flow and role-based access
5. AI service calls support OpenAI, LM Studio, Ollama, and Llama.cpp APIs

## Multi-Tenant Configuration

### Local Development

Default credentials for testing:

- **Email**: admin@localhost
- **Password**: admin123  
- **Tenant**: localhost

### Environment Configuration

Configure via `.env` file:

```env
# Database
DB_TYPE=sqlite  # or postgres
DB_PATH=prompts.db
POSTGRES_DSN=postgresql://user:pass@host:port/db

# Authentication
SECRET_KEY=your-secure-secret-key
LOCAL_DEV_MODE=true

# SSO (optional)
SSO_ENABLED=false
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/tenant-id

# LangWatch Optimization (optional)
LANGWATCH_API_KEY=your-langwatch-api-key
LANGWATCH_PROJECT_ID=ai-prompt-manager
```

## Database Configuration

Configure via `.env` file:

- SQLite: `DB_TYPE=sqlite` and `DB_PATH=prompts.db`
- PostgreSQL: `DB_TYPE=postgres` and `POSTGRES_DSN=connection_string`

## AI Service Integration

The application supports multiple AI services with unified interface:

- OpenAI-compatible (including LM Studio)
- Ollama native API
- Llama.cpp server API

Each service type has specific payload formatting in `call_ai_service()` method.

## Features

### 🔐 Authentication & Security (Multi-Tenant)

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

- **Tenant-Aware Prompts**: All prompts are isolated to your organization (MT)
- **User Attribution**: Track which user created each prompt (MT)
- **Enhanced Search**: Find prompts within your tenant's workspace
- **Category Organization**: Organize prompts by category within your tenant
- **AI Service Integration**: Support for multiple AI providers
- **Prompt Enhancement**: Use different models to improve existing prompts

### 🔑 API Features (Multi-Tenant)

- **Secure Token System**: Generate cryptographically secure API tokens
- **Token Expiration**: Set custom expiration times for enhanced security
- **Token Management**: View, revoke, and manage all your tokens
- **REST API Endpoints**: Programmatic access to all your prompts
- **OpenAPI Documentation**: Interactive API documentation and testing
- **Rate Limiting**: Built-in protection against abuse

### 🚀 LangWatch Optimization (Multi-Tenant)

- **AI-Powered Optimization**: Enhance prompts using LangWatch intelligence
- **Context-Aware**: Provide optimization context for better results
- **Model-Specific**: Optimize for different target AI models
- **Visual Feedback**: See optimization score and detailed suggestions
- **Accept/Reject Workflow**: Review and approve optimizations before applying
- **Retry Capability**: Re-run optimization with different parameters

## Quick Start

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
Edit `.env` file with your settings

4. **Launch Application**

```bash
# Multi-tenant version with API (recommended)
poetry run python run_mt_with_api.py

# Or multi-tenant version without API
poetry run python run_mt.py

# Or original single-user version
poetry run python prompt_manager.py
```

## Default Credentials (Multi-Tenant)

For local development, the system automatically creates:

- **Tenant**: `localhost`
- **Admin User**: `admin@localhost`
- **Password**: `admin123`

## Usage

### 1. Login (Multi-Tenant)

- Access the application at `http://localhost:7860`
- Use email/password or SSO to authenticate
- Admin users see additional admin panel

### 2. Prompt Management

- Create, edit, and delete prompts within your tenant
- Organize prompts by category and tags
- All prompts are isolated to your organization (MT)

### 3. AI Service Configuration

- Configure per-user AI service settings (MT) or global settings (single-user)
- Support for OpenAI, LM Studio, Ollama, and Llama.cpp
- Separate enhancement service configuration

### 4. Admin Functions (Admin Only - Multi-Tenant)

- **Tenant Management**: Create new organizations
- **User Management**: Add users to tenants with appropriate roles
- **System Overview**: Monitor tenant and user activity

### 5. API Usage (Multi-Tenant with API)

- **Token Creation**: Generate secure API tokens in Account Settings
- **API Documentation**: Access interactive docs at `/api/docs`
- **Programmatic Access**: Use REST endpoints for automation
- **Token Security**: Manage token expiration and revocation

### 6. LangWatch Optimization (Multi-Tenant)

- **Optimize Prompts**: Use the LangWatch optimization section in Prompt Management
- **Provide Context**: Add context about your prompt's purpose for better results
- **Review Results**: Examine optimization score, suggestions, and reasoning
- **Accept/Reject**: Choose to accept the optimized version or keep the original
- **Retry**: Try optimization again with different context or target model

## Production Deployment

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set LOCAL_DEV_MODE=false
- [ ] Use PostgreSQL database
- [ ] Configure HTTPS/TLS
- [ ] Set up SSO/ADFS properly
- [ ] Configure firewall rules
- [ ] Set up backup procedures
- [ ] Monitor application logs

### Docker Deployment

**Development (with local build):**

```bash
docker-compose up -d
```

**Production (with published images):**

```bash
# Set environment variables
export SECRET_KEY="your-production-secret-key"
export SSO_ENABLED="true"
export SSO_CLIENT_ID="your-sso-client-id"

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d
```

**Available Images:**

- `ghcr.io/OWNER/REPO:latest` - Latest development build
- `ghcr.io/OWNER/REPO:v1.0.0` - Stable tagged releases
- `ghcr.io/OWNER/REPO:main` - Main branch builds

**Production Configuration:**

```yaml
# Production docker-compose.prod.yml uses:
environment:
  DB_TYPE: postgres
  POSTGRES_DSN: postgresql://prompt_user:password@postgres:5432/ai_prompt_manager
  SECRET_KEY: ${SECRET_KEY}
  LOCAL_DEV_MODE: "false"
```

## API Reference (Multi-Tenant)

### Authentication

All API endpoints require a valid API token in the Authorization header:

```bash
Authorization: Bearer apm_your_token_here
```

### Base URL
```
http://localhost:7860/api
```

### Key Endpoints

**📝 List All Prompts**

```bash
GET /api/prompts
curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts
```

**🔍 Get Prompt by Name**

```bash
GET /api/prompts/name/{prompt_name}
curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts/name/my-prompt
```

**🆔 Get Prompt by ID**

```bash
GET /api/prompts/{prompt_id}
curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts/123
```

**📊 Search Prompts**

```bash
GET /api/search?q=keyword
curl -H "Authorization: Bearer apm_your_token" "http://localhost:7860/api/search?q=creative"
```

**📁 Get Categories**

```bash
GET /api/categories
curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/categories
```

**📈 Get Statistics**

```bash
GET /api/stats
curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/stats
```

### Interactive Documentation

- **Swagger UI**: http://localhost:7860/api/docs
- **ReDoc**: http://localhost:7860/api/redoc

### Example Response

```json
{
  "prompts": [
    {
      "id": 1,
      "name": "creative-writing",
      "title": "Creative Writing Assistant",
      "content": "You are a creative writing assistant...",
      "category": "Writing",
      "tags": "creative,writing",
      "is_enhancement_prompt": false,
      "user_id": "user-123",
      "created_at": "2025-01-08T10:00:00",
      "updated_at": "2025-01-08T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

## Testing

**Test API integration:**

```bash
poetry run python test_standalone_api.py
```

**Test multi-tenant setup:**

```bash
poetry run python test_mt_install.py
```

**Test LangWatch optimization:**

```bash
poetry run python test_langwatch_integration.py
```

## CI/CD Pipeline

The project includes automated GitHub workflows:

**🔄 Continuous Integration:**

- **Test and Validation**: Runs Python tests, Docker builds, and integration tests on every PR
- **Multi-platform Testing**: Tests both Python application and Docker containers
- **Code Quality**: Syntax checking and import validation

**🚀 Continuous Deployment:**

- **Docker Image Building**: Automatically builds and pushes images to GitHub Container Registry
- **Multi-tag Strategy**: Creates `latest`, branch-specific, and version tags
- **Security**: Uses GitHub's built-in GITHUB_TOKEN for authentication

**📦 Release Management:**

- **Automated Releases**: Creates GitHub releases when version tags are pushed
- **Changelog Generation**: Automatically generates release notes from commits
- **Container Updates**: Updates documentation with new image versions

**Workflow Triggers:**

- `main` branch pushes → Build and push `latest` image
- Version tags (v*.*.*) → Build versioned image and create release
- Pull requests → Run tests and build validation (no push)

## License

**Non-Commercial License** - This software is licensed for non-commercial use only.

### License Summary
- ✅ **Personal use** - Individual, educational, and research purposes
- ✅ **Non-profit organizations** - For non-commercial activities  
- ✅ **Academic institutions** - Research and educational use
- ❌ **Commercial use** - Business operations, revenue generation, or profit
- ❌ **Selling or licensing** - Without explicit commercial license agreement

### Commercial Licensing
For commercial use, please contact the copyright holder to obtain a separate commercial license agreement.

See the [LICENSE](LICENSE) file for complete details.

---

**🔐 Secure • 🏢 Multi-Tenant • 🚀 Scalable • 🤖 AI-Powered • 🔌 API-Ready**