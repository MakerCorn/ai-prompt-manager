# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

**Test multi-tenant installation:**
```bash
poetry run python test_mt_install.py
```

**Docker build and run:**
```bash
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager
```

**Docker compose for multi-tenant with PostgreSQL:**
```bash
docker-compose up -d
```

## Architecture

This is a Gradio-based web application for managing AI prompts with both single-user and multi-tenant architectures:

### Single-User Version
- `prompt_manager.py` - Original single-user application
- `prompt_data_manager.py` - Database abstraction layer

### Multi-Tenant Version
- `prompt_manager_mt.py` - Multi-tenant application with authentication
- `auth_manager.py` - Authentication, user management, and SSO/ADFS support
- `prompt_data_manager.py` - Enhanced with tenant-aware data isolation
- `run_mt.py` - Multi-tenant application launcher

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