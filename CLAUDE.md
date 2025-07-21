# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Development Setup

```bash
# CRITICAL: Always use Poetry environment to avoid dependency issues
poetry install                          # Install dependencies
poetry run python run.py               # Multi-tenant mode (default)
poetry run python run.py --single-user # Single-user mode
poetry run python run.py --with-api    # Enable dual-server API
```

### Testing

```bash
# Unit tests
poetry run python tests/unit/test_*.py

# Integration tests
poetry run python tests/integration/test_mt_install.py
poetry run python tests/integration/test_api_integration.py

# E2E tests (install dependencies first)
poetry install --with e2e
poetry run playwright install chromium
poetry run python tests/e2e/test_web_ui_e2e.py
```

### Code Quality

```bash
poetry run black .                     # Format code
poetry run isort .                     # Organize imports
poetry run flake8 . --max-line-length=88 --extend-ignore=E203,W503
poetry run bandit -r . --skip B101,B602,B603
```

## Architecture Overview

### Core Application (Root Level)

- `run.py` - Universal launcher supporting all deployment modes
- `web_app.py` - FastAPI web application with Rules Management
- `auth_manager.py` - Authentication, user management, tenant isolation
- `prompt_data_manager.py` - Database operations with tenant-aware data access
- `api_endpoints_enhanced.py` - Enhanced AI services REST API (14 endpoints)
- `language_manager.py` - Multi-language support system (10 languages)

### Modern Architecture (src/)

```text
src/
├── core/                          # Infrastructure layer
│   ├── base/                      # Base classes
│   ├── config/                    # Configuration (AI models, settings)
│   ├── services/                  # Core business services
│   └── exceptions/                # Structured exceptions
├── prompts/                       # Prompt management
├── auth/                          # Authentication module
└── utils/                         # Shared utilities
```

### Web UI (web_templates/)

- **FastAPI + Jinja2** templates with HTMX dynamic updates
- **Tailwind CSS** responsive design
- **Multi-language support** with real-time switching
- **Complete CRUD** for prompts, rules, templates
- **Dark/light theme system** with system preference detection

## Key Development Patterns

### Multi-Tenant Architecture

- All database operations **MUST include tenant_id filtering**
- Complete data isolation between tenants
- Authentication required in multi-tenant mode

### Dual-Server API Mode

When `--with-api` flag is used:

- Web UI: Main port (e.g., 7860)
- FastAPI API: Main port + 1 (e.g., 7861)
- API docs available at `/docs` endpoint

### Critical Environment Requirements

- **Always use Poetry**: `poetry run python` (never direct `python`)
- Avoids dependency issues and "Create New Prompt" errors
- Required for proper FastAPI and python-dotenv loading

## Database Schema

### Core Tables

```sql
-- Multi-tenant isolation
tenants(id, name, subdomain, max_users, is_active)
users(id, tenant_id, email, role, sso_id, is_active)

-- Content management
prompts(id, tenant_id, user_id, name, content, category, tags)
rules(id, tenant_id, user_id, name, title, content, category, tags)
templates(id, tenant_id, user_id, name, content, category)

-- AI services
ai_models(id, tenant_id, user_id, name, provider, model_id, ...)
ai_operation_configs(id, tenant_id, user_id, operation_type, ...)
```

## Testing Strategy

### Test Organization

- `tests/unit/` - Individual component tests
- `tests/integration/` - System integration tests
- `tests/e2e/` - Browser automation with Playwright

### E2E Testing

```bash
# Environment variables for debugging
E2E_HEADLESS=false                      # Visible browser
E2E_SLOW_MO=500                        # Slow motion
```

## Deployment Modes

### Single-User Mode

- No authentication required
- SQLite database
- All features available without login

### Multi-Tenant Mode

- Authentication required (default: admin@localhost / admin123)
- Complete tenant isolation
- 24-hour session expiry

### API-Enabled Mode

- Dual-server architecture
- REST API with Bearer token authentication
- Swagger documentation at `/docs`

## Development Guidelines

### Working with Core Components

- Maintain tenant isolation in all database operations
- Follow existing patterns for authentication
- Test with both SQLite (dev) and PostgreSQL (prod)

### Working with New Architecture (src/)

- Use Service/Repository pattern
- Implement type hints
- Follow dependency injection patterns
- Add comprehensive unit tests

### Adding Features

1. Determine if UI or business logic change
2. Update appropriate templates in `web_templates/`
3. Add service logic in `src/` if needed
4. Implement tests (unit + integration + E2E)
5. Update language files if UI changes

## Package Distribution

- Published to PyPI as `promptman`
- Installation: `pip install promptman`
- Execution: `python -m promptman`
- GitHub Actions automation for releases

Always update CHANGELOG.md when making code changes.