# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Installation & Setup
```bash
# Install dependencies (development)
poetry install

# Or install from PyPI (production/end-user)
pip install promptman

# Run from PyPI installation
python -m promptman
```

### Development Commands
```bash
# CRITICAL: Always use Poetry environment to avoid dependency issues
# Running python run.py directly may cause "Create New Prompt" errors

# Run application (different modes)
poetry run python run.py                     # Multi-tenant mode (default)
poetry run python run.py --single-user       # Single-user mode
poetry run python run.py --with-api          # Multi-tenant + Dual-Server API
poetry run python run.py --single-user --with-api  # Single-user + API
poetry run python run.py --debug --port 8080 # Debug mode on custom port

# API Architecture Notes:
# --with-api enables dual-server architecture:
#   - FastAPI Web UI: Main port (e.g., 8080)
#   - FastAPI API Server: Main port + 1 (e.g., 8081)

# Testing - Web UI (FastAPI)
poetry run python tests/integration/test_web_interface_integration.py     # Web interface integration
poetry run python tests/integration/test_web_ui_integration.py            # Web UI functionality
poetry run python tests/e2e/test_web_ui_e2e.py                          # End-to-end browser tests with Playwright

# Testing - Multi-tenant & Architecture
poetry run python tests/integration/test_mt_install.py                    # Multi-tenant setup
poetry run python tests/integration/test_new_architecture_integration.py # New architecture
poetry run python tests/integration/test_langwatch_integration.py        # AI optimization
poetry run python tests/integration/test_api_integration.py              # API integration

# Testing - Enhanced AI Services
poetry run python tests/unit/test_ai_model_config.py                     # AI model configuration unit tests
poetry run python tests/unit/test_ai_model_manager.py                    # AI model manager unit tests
poetry run python tests/integration/test_ai_services_api_integration.py  # AI services API integration
poetry run python tests/integration/test_ai_database_integration.py      # AI database operations
poetry run python tests/e2e/test_enhanced_ai_services_e2e.py            # Enhanced AI services E2E tests

# Docker testing
./scripts/docker-test.sh          # Full Docker validation
docker-compose up -d              # Development stack
docker-compose -f docker-compose.prod.yml up -d  # Production stack
```

### Build and Lint Commands
```bash
# Code Quality Tools (run in sequence for best results)
poetry run black .                           # Format Python code
poetry run isort .                           # Organize imports
poetry run flake8 . --max-line-length=88 --extend-ignore=E203,W503  # Linting
poetry run bandit -r . --skip B101,B602,B603 # Security scanning

# Alternative linting with more modern tools (if available)
# poetry run ruff check .
# poetry run mypy .
# poetry run pytest

# Package build and distribution
poetry build                      # Build wheel and source distribution
poetry publish                    # Publish to PyPI (requires PYPI_API_TOKEN)

# Docker build
docker build -t ai-prompt-manager .
```

## Architecture Overview

### Modern Web UI Architecture (Default)
This project now uses a **modern web interface** as the default, built with FastAPI + HTMX + Tailwind CSS:

**Core Application Components (Root Level):**
- `run.py` - Universal launcher supporting all deployment modes
- `web_app.py` - Modern FastAPI web application
- `auth_manager.py` - Authentication, user management, and tenant isolation
- `prompt_data_manager.py` - Database operations with tenant-aware data access
- `token_calculator.py` - AI model cost estimation and token calculation
- `langwatch_optimizer.py` - AI-powered prompt optimization services
- `api_endpoints.py` - REST API implementation with FastAPI
- `api_endpoints_enhanced.py` - Enhanced AI services REST API with 14 endpoints
- `api_token_manager.py` - Secure API token generation and validation
- `__main__.py` - Package entry point for `python -m promptman` execution

**FastAPI Web UI Architecture (web_templates/ directory):**
```
web_templates/
├── layouts/
│   └── base.html                  # Base template with navigation and theming
├── auth/
│   └── login.html                 # Modern login interface with i18n support
├── prompts/
│   ├── dashboard.html             # Main dashboard with recent prompts
│   ├── list.html                  # Prompt library with search/filter
│   ├── form.html                  # Create/edit prompt with real-time features
│   ├── execute.html               # Prompt execution interface
│   ├── builder.html               # Drag-and-drop prompt builder
│   └── _list_partial.html         # HTMX partial for dynamic updates
├── ai_services/
│   ├── config.html                # Legacy AI service configuration
│   └── enhanced_config.html       # Enhanced AI services with multi-model support
├── settings/
│   ├── index.html                 # Settings hub
│   ├── profile.html               # User profile management
│   └── api_tokens.html            # API token management
├── templates/
│   ├── list.html                  # Template library
│   └── form.html                  # Template creation/editing
├── admin/
│   └── dashboard.html             # Admin control panel
└── static/                        # Static assets (CSS, JS, images)
    ├── css/
    └── js/
```

**FastAPI Web UI Features:**
- **FastAPI + Jinja2**: Server-side rendered templates with modern styling
- **Tailwind CSS**: Responsive, mobile-first design (built-in CSS framework)
- **Multi-language Support**: 10 languages with dynamic switching and real-time translation
- **Session Authentication**: Secure session-based authentication with 24-hour expiry
- **HTMX Integration**: Dynamic content updates without page reloads
- **Modern Components**: Clean forms, navigation, and interactive elements
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Complete CRUD Operations**: Full Create, Read, Update, Delete for prompts and templates
- **Drag-and-Drop Builder**: Visual prompt combination with live preview
- **AI Integration**: Built-in optimization, translation, and token calculation
- **Single-User & Multi-Tenant**: Seamless mode switching with proper isolation

**Modular Architecture (src/):**
```
src/
├── core/                          # Infrastructure layer with AI services
│   ├── base/                      # Base classes (DatabaseManager, ServiceBase)
│   ├── config/                    # Type-safe configuration including AI models
│   │   └── ai_model_config.py     # AI model and provider configuration system
│   ├── services/                  # Core business services
│   │   └── ai_model_manager.py    # AI model management and health checking
│   └── exceptions/                # Structured exception hierarchy
├── auth/                          # Authentication module (experimental)
├── prompts/                       # Prompt management services
└── utils/                         # Shared utilities and helpers
```

### Key Architectural Patterns
- **Modular UI Design**: Separate interfaces for different functionality areas
- **Component-Based Architecture**: Reusable UI components with consistent theming
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Service Layer Pattern**: Business logic encapsulated in service classes
- **Repository Pattern**: Data access abstraction with tenant isolation
- **Dependency Injection**: Testable, loosely-coupled components
- **Multi-Tenant Architecture**: Complete data isolation via tenant_id filtering
- **API-First Design**: RESTful API with comprehensive OpenAPI documentation
- **Package Distribution**: Published as `promptman` on PyPI with automated release workflow

### UI/UX Improvements
- **Modern Navigation**: Sidebar navigation with clear section separation
- **Unified Prompt Management**: Combined creation, editing, and library browsing
- **Enhanced Authentication**: Clean login interface with SSO support
- **Improved Execution Flow**: Streamlined prompt testing and execution
- **Better Settings Organization**: Grouped configuration options
- **Visual Design**: Consistent color scheme and typography
- **Accessibility**: Proper focus management and screen reader support
- **Mobile Optimization**: Touch-friendly interface elements

## Enhanced AI Services Configuration

### Multi-Model Architecture
The application now features a comprehensive AI services configuration system that allows users to configure different models and providers for different operations:

**Core AI Services Components:**
- `src/core/config/ai_model_config.py` - AI model configuration system with provider definitions
- `src/core/services/ai_model_manager.py` - AI model management service with health checking
- `api_endpoints_enhanced.py` - Enhanced API endpoints for AI model management
- `web_templates/ai_services/enhanced_config.html` - Modern tabbed UI for AI configuration

### Supported AI Providers
```python
# 10+ AI Providers supported
AIProvider.OPENAI           # OpenAI GPT models
AIProvider.AZURE_OPENAI     # Azure OpenAI enterprise models
AIProvider.ANTHROPIC        # Claude 3 models (Opus, Sonnet, Haiku)
AIProvider.GOOGLE           # Gemini Pro, Gemini Ultra
AIProvider.OLLAMA           # Local Ollama models
AIProvider.LM_STUDIO        # LM Studio local deployment
AIProvider.LLAMA_CPP        # llama.cpp GGUF models
AIProvider.HUGGINGFACE      # Hugging Face Hub models
AIProvider.COHERE           # Cohere Command models
AIProvider.TOGETHER_AI      # Together AI hosted models
```

### Operation Types
```python
# 11 Operation Types for model specialization
OperationType.DEFAULT                # General purpose operations (primary fallback)
OperationType.PROMPT_ENHANCEMENT     # Improving prompt quality and structure
OperationType.PROMPT_OPTIMIZATION    # Performance and cost optimization
OperationType.PROMPT_TESTING         # Testing and validation (prefer cheap models)
OperationType.MODEL_COMBINING        # Ensemble operations with multiple models
OperationType.TRANSLATION           # Language translation and localization
OperationType.SUMMARIZATION         # Content summarization and condensing
OperationType.CONVERSATION          # Chat and dialogue interactions
OperationType.QUESTION_ANSWERING    # Q&A and information retrieval
OperationType.CONTENT_GENERATION    # Creative writing and content creation
OperationType.CODE_GENERATION       # Programming and code assistance
```

### AI Model Configuration Features
- **Multi-Provider Support**: Configure models from 10+ different AI providers
- **Operation-Specific Models**: Set different models for different types of operations
- **Health Monitoring**: Automatic health checks and availability tracking
- **Intelligent Selection**: Automatic model selection with fallback chains
- **Usage Analytics**: Comprehensive tracking of token usage, costs, and performance
- **API Integration**: RESTful API with 14 endpoints for programmatic management
- **Import/Export**: Configuration backup and migration capabilities

### Database Schema Extensions
```sql
-- New AI Services tables
ai_models(
    id, tenant_id, user_id, name, display_name, provider, model_id,
    description, api_key, api_endpoint, deployment_name, api_version,
    cost_per_1k_input_tokens, cost_per_1k_output_tokens, max_context_length,
    temperature, max_tokens, top_p, frequency_penalty, presence_penalty,
    supports_streaming, supports_function_calling, supports_vision, supports_json_mode,
    is_enabled, is_available, last_health_check, created_at, updated_at
)

ai_operation_configs(
    id, tenant_id, user_id, operation_type, primary_model, fallback_models,
    is_enabled, custom_parameters, created_at, updated_at
)
```

### Testing Coverage
- **Unit Tests**: Complete coverage for AI model configuration and manager services
- **Integration Tests**: Database operations and API endpoint testing
- **E2E Tests**: Browser automation testing for the enhanced AI services UI
- **Multi-Provider Testing**: Health check validation for all supported providers

### API Endpoints
The enhanced AI services provide 14 comprehensive API endpoints:

```bash
# Core model management
GET    /api/ai-models/                    # List all models
POST   /api/ai-models/                    # Add new model
PUT    /api/ai-models/{name}              # Update model
DELETE /api/ai-models/{name}              # Delete model

# Model operations
POST   /api/ai-models/{name}/test         # Test model health
POST   /api/ai-models/health-check        # Check all models

# Configuration management
GET    /api/ai-models/operations          # Get operation configs
PUT    /api/ai-models/operations/{type}   # Update operation config

# System information
GET    /api/ai-models/providers           # List supported providers
GET    /api/ai-models/operation-types     # List operation types

# Analytics and recommendations
GET    /api/ai-models/usage-stats         # Usage statistics
GET    /api/ai-models/recommendations/{type} # Model recommendations

# Import/Export
POST   /api/ai-models/export              # Export configuration
POST   /api/ai-models/import              # Import configuration
```

## Multi-Tenant Security Model

### Tenant Isolation
All database operations include `tenant_id` filtering to ensure complete data separation:
- Users belong to specific tenants and cannot access cross-tenant data
- Prompts, configurations, and API tokens are tenant-scoped
- Admin users can only manage their own tenant

### Database Schema Key Points
```sql
-- Core tables with tenant isolation
tenants(id, name, subdomain, max_users, is_active)
users(id, tenant_id, email, role, sso_id, is_active)
prompts(id, tenant_id, user_id, name, content, category)
api_tokens(id, user_id, tenant_id, token_hash, expires_at)
```

## Environment Configuration

### Core Settings
```bash
# Application Mode
MULTITENANT_MODE=true     # Enable multi-tenant (default)
ENABLE_API=false          # Enable REST API endpoints
LOCAL_DEV_MODE=true       # Development features

# Database
DB_TYPE=sqlite            # sqlite or postgres
DB_PATH=prompts.db        # SQLite path
POSTGRES_DSN=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=auto-generated # JWT signing secret
```

### AI Service Integration
```bash
# Prompt Optimization
PROMPT_OPTIMIZER=langwatch              # langwatch, promptperfect, builtin
LANGWATCH_API_KEY=your_key
PROMPTPERFECT_API_KEY=your_key

# Translation Services  
TRANSLATION_SERVICE=openai              # openai, google, libre, mock
OPENAI_API_KEY=your_key

# Azure AI Services
AZURE_AI_ENABLED=false
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your_key
```

## Testing Strategy

### Test Organization
```
tests/
├── unit/                          # Unit tests for individual components
│   ├── core/                      # Core infrastructure tests
│   ├── auth/                      # Authentication tests
│   └── api/                       # API endpoint tests
├── integration/                   # Integration and system tests
│   ├── test_mt_install.py         # Multi-tenant setup validation
│   ├── test_new_architecture_integration.py  # Modern architecture tests
│   ├── test_langwatch_integration.py         # AI optimization features
│   ├── test_api_integration.py               # Complete API test suite
│   ├── test_web_interface_integration.py     # Web interface integration
│   └── test_web_ui_integration.py            # Web UI functionality
├── e2e/                          # End-to-end browser automation tests
│   ├── conftest.py               # E2E test fixtures and configuration
│   ├── test_authentication_flow.py          # Login/logout workflows
│   ├── test_prompt_management_flow.py       # Prompt creation/management
│   ├── test_api_workflow.py                # API testing scenarios
│   ├── test_deployment_scenarios.py        # Deployment configuration tests
│   └── test_web_ui_e2e.py                  # FastAPI Web UI automation tests
└── fixtures/                      # Test data and fixtures
```

### Testing Commands
```bash
# Test specific components (CRITICAL: Use Poetry environment)
poetry run python tests/integration/test_mt_install.py
poetry run python tests/integration/test_new_architecture_integration.py

# Test Docker deployment
./scripts/docker-test.sh
./scripts/docker-test.sh dev    # Development setup only
./scripts/docker-test.sh prod   # Production setup only

# Run E2E tests
poetry install --with e2e                    # Install E2E dependencies
poetry run playwright install chromium       # Install browser
poetry run pytest tests/e2e/ -v -m "e2e"    # Run E2E test suite
poetry run pytest tests/e2e/ -v --headless=false  # Run with visible browser

# Run Web UI E2E tests (FastAPI + Playwright)
python tests/e2e/test_web_ui_e2e.py         # Direct execution
E2E_HEADLESS=false python tests/e2e/test_web_ui_e2e.py  # With visible browser
E2E_SLOW_MO=500 python tests/e2e/test_web_ui_e2e.py     # Slow motion debugging

# Test imports and basic functionality (CRITICAL: Use Poetry environment)
poetry run python -c "
from auth_manager import AuthManager
from prompt_data_manager import PromptDataManager  
from run import main
print('✅ Core components working')
"

poetry run python -c "
import sys; sys.path.insert(0, 'src')
from src.prompts.services.prompt_service import PromptService
from src.core.config.settings import AppConfig
print('✅ New architecture working')
"
```

## Key Features and Components

### AI-Powered Optimization
- **LangWatch Integration**: Enterprise-grade prompt optimization
- **PromptPerfect**: Specialized prompt refinement
- **Built-in Optimizer**: Rule-based improvements (no external dependencies)
- **Multi-Model Support**: Optimization for GPT-4, Claude, Gemini, etc.

### Custom Template System
- **Template Directory**: `templates/` with domain-specific templates
- **Variable Substitution**: `{variable_name}` syntax support
- **Built-in Templates**: Default, Business, Technical, Creative, Analytical
- **Template Service**: `src/prompts/services/template_service.py`

### Multi-Language Support
- **10 Languages**: EN, ES, FR, DE, ZH, JA, PT, RU, AR, HI
- **Real-time Switching**: Language selector in UI
- **Translation Integration**: Automatic translation for optimization
- **Internationalization**: `i18n.py` with embedded translations

### Prompt Builder
- **Drag-and-drop Interface**: Visual prompt combination
- **4 Templates**: Sequential, Sections, Layered, Custom
- **Live Preview**: Real-time combination preview
- **Integration**: Works with token calculator and optimization

## Development Guidelines

### Critical Environment Requirements
**ALWAYS use Poetry environment** to avoid dependency issues:
- ❌ `python run.py` - May cause "Create New Prompt" internal server errors
- ✅ `poetry run python run.py` - Proper dependency resolution
- ❌ Direct Python execution - Missing dependencies like `python-dotenv`, `fastapi`
- ✅ Poetry environment - All dependencies available

### Working with Core Components  
When modifying core components (root-level .py files):
- Maintain backward compatibility with existing deployments
- Follow existing patterns for tenant isolation
- Ensure all database operations include tenant_id filtering
- Update corresponding tests in `tests/integration/`
- **CRITICAL**: Test with `poetry run` to ensure dependencies are available

### Working with New Architecture  
When working in `src/` directory:
- Follow Service/Repository pattern
- Use dependency injection for testability
- Implement comprehensive type hints
- Add unit tests in `tests/unit/`
- Follow the base class patterns in `src/core/base/`
- **CRITICAL**: Always test imports with `poetry run` environment
- Update both legacy and new architecture components when making changes

### Database Operations
- **Always include tenant_id** in queries for multi-tenant isolation
- Use `PromptDataManager` for data operations
- Use repository classes in `src/` for new architecture
- Test with both SQLite (development) and PostgreSQL (production)

### API Development
**Dual-Server Architecture**: The application uses a dual-server approach for API integration:

#### Architecture Overview
- **Web UI Server**: Runs on main port (handles UI)
- **FastAPI Server**: Runs on main port + 1 (handles API requests)
- **Threading**: API server runs in separate daemon thread
- **Startup**: Both servers start from single `run.py --with-api` command

#### API Server Details
- **Location**: API endpoints defined in `run.py` (lines 266-289)
- **Base Endpoints**: `/health`, `/info`, `/docs`, `/redoc`, `/`
- **Documentation**: Auto-generated Swagger UI at `/docs`
- **Port Calculation**: `api_port = main_port + 1`

#### Development Workflow
1. **Start with API**: `poetry run python run.py --with-api --port 7860`
2. **Access UI**: http://localhost:7860 (Web interface)
3. **Access API**: http://localhost:7861 (FastAPI server)
4. **API Docs**: http://localhost:7861/docs (Swagger UI)
5. **Test Integration**: `poetry run python tests/integration/test_api_integration.py`

#### Adding New API Endpoints
To add new endpoints, modify the API app creation in `run.py`:
```python
@api_app.get("/your-endpoint")
async def your_function():
    return {"message": "Your response"}
```

#### Additional API Components
- `api_endpoints.py` - Contains APIManager class for advanced features
- `api_token_manager.py` - Authentication and token management
- These can be integrated into the dual-server setup as needed

## Package Distribution

### PyPI Publishing
The project is published to PyPI as `promptman`:
- **Package Name**: `promptman` (not `ai-prompt-manager` - was taken)
- **Installation**: `pip install promptman`
- **Module Execution**: `python -m promptman`
- **Automated Publishing**: GitHub Actions workflow publishes releases to PyPI
- **Publishing Conditions**: Only non-draft, non-prerelease versions are published

### Release Workflow
- **GitHub Actions**: `.github/workflows/release.yml` handles full release automation
- **PyPI Publishing**: Automatic on stable releases using `PYPI_API_TOKEN` secret
- **Docker Images**: Published to `ghcr.io/makercorn/ai-prompt-manager`
- **Release Assets**: Source archives, wheels, Docker images, and documentation

## Docker Deployment

### Docker Commands
```bash
# Build image locally
docker build -t ai-prompt-manager .

# Run container (single instance)
docker run -p 7860:7860 ai-prompt-manager

# Run with API enabled (dual ports)
docker run -p 7860:7860 -p 7861:7861 -e ENABLE_API=true ai-prompt-manager

# Development stack
docker-compose up -d

# Production stack  
docker-compose -f docker-compose.prod.yml up -d

# Test Docker setup
./scripts/docker-test.sh
```

### Docker Architecture
- **Single Port Mode**: Web UI on port 7860
- **Dual Port Mode**: Web UI on 7860, API on 7861 (when ENABLE_API=true)
- **Health Checks**: Configured for both login and root endpoints
- **Environment Variables**: Full configuration via ENV vars for containerized deployment

## Common Development Tasks

### Working with the FastAPI Web UI Architecture

#### Adding New UI Features
1. **Identify the appropriate UI module**:
   - Authentication changes → `ui/auth_interface.py`
   - Prompt management → `ui/prompt_management.py`
   - Execution/testing → `ui/execution_interface.py`
   - Settings/config → `ui/settings_interface.py`
   - Navigation/layout → `ui/main_interface.py`

2. **Add new UI components**:
   - Use `UIComponents` class for consistent styling
   - Follow the established CSS class naming conventions
   - Add CSS to the appropriate interface's `get_css()` method

3. **Update navigation**:
   - Modify `ui/main_interface.py` for new sections
   - Update navigation event handlers
   - Add appropriate icons and labels

#### Adding New Features (General)
1. Determine if feature belongs in UI layer or business logic
2. For UI features: Add to appropriate UI module
3. For business logic: Create service in appropriate module
4. Add repository layer if data access needed
5. Implement comprehensive tests (unit + E2E)
6. Update API endpoints if needed
7. Update CLAUDE.md with feature details
8. Update pyproject.toml version if releasing

### Testing Changes
1. Run relevant integration tests
2. Test both single-user and multi-tenant modes  
3. Verify Docker deployment works
4. Test API endpoints if modified
5. Validate with different AI service configurations

### Database Changes
1. Update both legacy and new architecture if needed
2. Test with SQLite and PostgreSQL
3. Ensure tenant isolation is maintained
4. Update repository tests
5. Verify migrations work in Docker

## End-to-End (E2E) Testing

### E2E Test Framework
The project includes a comprehensive E2E testing framework using Playwright and Selenium for browser automation:

**Test Categories:**
- **Authentication Flow Tests**: Login, logout, session management, invalid credentials
- **Prompt Management Tests**: Create, edit, delete prompts, library browsing, search functionality
- **API Workflow Tests**: Health checks, authentication, CORS, error handling, performance
- **Deployment Scenario Tests**: Single-user mode, multi-tenant mode, API-enabled configurations
- **Web UI E2E Tests**: FastAPI web interface automation with Playwright for comprehensive UI testing

### E2E Test Configuration
```bash
# Environment Variables for E2E Testing
E2E_HEADLESS=true          # Run tests in headless mode (default: true)
E2E_SLOW_MO=0              # Slow motion delay in milliseconds (default: 0)
```

### E2E Test Execution
```bash
# Install E2E dependencies
poetry install --with e2e

# Install browser dependencies
poetry run playwright install chromium --with-deps

# Run all E2E tests
poetry run pytest tests/e2e/ -v -m "e2e"

# Run specific E2E test categories
poetry run pytest tests/e2e/test_authentication_flow.py -v
poetry run pytest tests/e2e/test_prompt_management_flow.py -v
poetry run pytest tests/e2e/test_api_workflow.py -v
poetry run pytest tests/e2e/test_deployment_scenarios.py -v

# Run with visible browser (for debugging)
E2E_HEADLESS=false poetry run pytest tests/e2e/ -v -m "e2e"

# Run with custom configuration
E2E_HEADLESS=false E2E_SLOW_MO=500 poetry run pytest tests/e2e/ -v -s
```

### Web UI E2E Tests (FastAPI Interface)
The project includes dedicated E2E tests for the FastAPI web interface using Playwright:

```bash
# Install E2E dependencies first
poetry install --with e2e
poetry run playwright install chromium

# Run Web UI E2E tests directly  
poetry run python tests/e2e/test_web_ui_e2e.py

# Run with visible browser for debugging
E2E_HEADLESS=false poetry run python tests/e2e/test_web_ui_e2e.py

# Run with slow motion for detailed observation
E2E_SLOW_MO=500 poetry run python tests/e2e/test_web_ui_e2e.py

# Combined debugging settings
E2E_HEADLESS=false E2E_SLOW_MO=1000 poetry run python tests/e2e/test_web_ui_e2e.py
```

**Web UI Test Coverage:**
- Complete login/logout workflows with multi-tenant authentication
- Navigation menu functionality and responsive design testing
- Language switching and internationalization features
- Full prompt creation, editing, and management workflows
- Search and filtering functionality with HTMX integration
- Prompt execution interface with variable substitution
- AI optimization and translation feature testing
- Settings, profile, and API token management
- Error handling and accessibility basics
- Cross-device responsive design validation

**Key Features:**
- **Multiprocessing Support**: Fixed pickle serialization issues for reliable test execution
- **Category Selection Fix**: Ensures default categories are available for empty databases
- **Single-User Mode Support**: Complete testing coverage for both authentication modes
- **Template Rendering**: Proper UI element handling for both authenticated and single-user modes

**Critical Dependencies:**
- **httpx**: Required for FastAPI TestClient - included in dev/test dependencies
- **playwright**: Required for browser automation - install with `poetry install --with e2e`
- **All imports updated**: Use modern `run.main` and `web_app` components

### E2E Test Infrastructure
- **Test Server**: Automatic app server startup on port 7862 for isolated testing
- **Browser Automation**: Playwright for modern web testing with Chromium
- **API Testing**: Requests library for API endpoint validation
- **Test Isolation**: Each test uses isolated temporary databases and configurations
- **CI/CD Integration**: Automated E2E tests run in GitHub Actions workflow

### E2E Test Fixtures
- `test_config`: Configuration settings for E2E tests
- `app_server`: Automatically started application server instance
- `api_client`: HTTP client for API testing
- `admin_user_data`: Default admin credentials for authentication tests
- `sample_prompt_data`: Sample data for prompt creation tests

## Deployment Modes

### Single-User Mode
```bash
poetry run python run.py --single-user
# - No authentication required
# - SQLite database
# - File-based storage
# - Single port: UI only
# - Full CRUD operations available
# - All features work without login
```

### Multi-Tenant Mode  
```bash
poetry run python run.py
# - Authentication required
# - Complete tenant isolation
# - Admin panel available
# - Default: admin@localhost / admin123
# - Single port: UI only
# - 24-hour session expiry
# - Role-based access control
```

### API-Enabled Mode (Dual-Server Architecture)
```bash  
poetry run python run.py --with-api
# - Dual-server architecture activated
# - Web UI: Main port (e.g., 7860)
# - FastAPI Server: Main port + 1 (e.g., 7861)
# - API documentation at http://localhost:7861/docs
# - Health check at http://localhost:7861/health
# - Both servers managed by single process
# - Automatic port calculation and management
```

### Combined Modes
```bash
# Single-user with API
poetry run python run.py --single-user --with-api
# - No authentication for UI
# - API server on main port + 1
# - Simplified development setup
# - Best for development and testing

# Custom port with API
poetry run python run.py --with-api --port 8080
# - UI: http://localhost:8080
# - API: http://localhost:8081
# - API Docs: http://localhost:8081/docs
# - Flexible port configuration
```

### Docker Deployment
```bash
# Development (with API)
docker-compose up -d
# Maps port 7860 (UI) and 7861 (API)

# Production (with API)
docker-compose -f docker-compose.prod.yml up -d

# Single container with API
docker run -p 7860:7860 -p 7861:7861 -e ENABLE_API=true ghcr.io/makercorn/ai-prompt-manager:latest

# Note: Expose both ports when using --with-api flag
```

Always update the CHANGELOG.md when making changes to code.