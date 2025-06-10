# AI Prompt Manager

A comprehensive AI prompt management system with unified architecture supporting both single-user and multi-tenant deployments. Features advanced authentication, real-time token cost estimation, AI-powered prompt optimization, and secure API access.

## 📋 Table of Contents

- [🌟 Key Features](#-key-features)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Configuration](#️-configuration)
- [🌐 Multi-Language Support](#-multi-language-support)
- [🧮 Token Calculator Guide](#-token-calculator-guide)
- [📝 Prompt Management](#-prompt-management)
- [🔑 API Access](#-api-access)
- [🏢 Multi-Tenant Features](#-multi-tenant-features)
- [🚀 Development](#-development)
- [🔒 Production Deployment](#-production-deployment)
- [🚀 Multi-Language Quick Reference](#-multi-language-quick-reference)
- [📚 Additional Resources](#-additional-resources)
- [📄 License](#-license)

## 🌟 Key Features

### 🏗️ **Unified Architecture**
- **Single Codebase**: Supports both single-user and multi-tenant modes
- **Environment-Based Configuration**: Switch modes via environment variables
- **Backward Compatible**: Existing installations continue working unchanged

### 🔐 **Security & Authentication**
- **Multi-Tenant Isolation**: Complete data separation between organizations
- **SSO/ADFS Integration**: Enterprise authentication with Microsoft Azure AD
- **Role-Based Access**: Admin, User, and Read-only permission levels
- **JWT Session Management**: Secure, stateless authentication tokens
- **API Token System**: Secure programmatic access with expiring tokens

### 🧮 **Advanced AI Features**
- **Token Calculator**: Real-time cost estimation for all major AI models
- **LangWatch Integration**: AI-powered prompt optimization and suggestions
- **Multi-Provider Support**: OpenAI, Claude, Gemini, LM Studio, Ollama, Llama.cpp
- **Enhancement Engine**: Improve prompts using different AI models

### 🌐 **Modern User Experience**
- **Multi-Language Support**: 10 languages with real-time switching
- **Responsive Design**: Mobile-first, adaptive interface
- **Modern UI Components**: Professional styling with accessibility features
- **Dark Mode Support**: Automatic theme switching
- **Intuitive Navigation**: Simplified, context-aware interface

### 🔌 **Developer Experience**
- **REST API**: Comprehensive API with interactive documentation
- **Docker Support**: Production-ready containerization
- **Database Flexibility**: SQLite for development, PostgreSQL for production
- **Comprehensive Testing**: Full test suite with isolation verification

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (recommended) or pip
- Optional: PostgreSQL for production

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd ai-prompt-manager
poetry install

# Copy and customize configuration
cp .env.example .env
# Edit .env file for your specific setup
```

2. **Launch Application**
```bash
# Universal launcher with smart defaults (recommended)
poetry run python run.py

# Command line mode selection
poetry run python run.py --single-user     # Single-user mode
poetry run python run.py --with-api        # Multi-tenant + API
poetry run python run.py --single-user --with-api  # Single-user + API

# Custom server configuration
poetry run python run.py --port 8080 --host 127.0.0.1
python run.py --help  # See all options
```

3. **Access Application**
- Open browser to `http://localhost:7860`
- Login with: `admin@localhost` / `admin123` (multi-tenant)

### Docker Deployment
```bash
# Quick start
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest

# With PostgreSQL
docker-compose up -d
```

---

## ⚙️ Configuration

### Application Modes

The unified AI Prompt Manager supports multiple deployment modes controlled by environment variables:

#### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Application Mode
MULTITENANT_MODE=true          # Enable multi-tenant mode (default: true)
ENABLE_API=false               # Enable REST API endpoints (default: false)

# Server Configuration  
SERVER_HOST=0.0.0.0           # Server host (default: 0.0.0.0)
SERVER_PORT=7860              # Server port (default: 7860)

# Database Configuration
DB_TYPE=sqlite                # Database type: sqlite or postgres (default: sqlite)
DB_PATH=prompts.db           # SQLite database path (default: prompts.db)
POSTGRES_DSN=postgresql://... # PostgreSQL connection string (if using postgres)

# Development
DEBUG=false                   # Enable debug mode (default: false)
LOCAL_DEV_MODE=true          # Enable local development features (default: false)
```

#### Mode Combinations

1. **Single-User Mode** (Legacy compatibility)
   ```bash
   MULTITENANT_MODE=false
   ENABLE_API=false
   ```

2. **Multi-Tenant Mode** (Recommended)
   ```bash
   MULTITENANT_MODE=true
   ENABLE_API=false
   ```

3. **Multi-Tenant with API** (Full featured)
   ```bash
   MULTITENANT_MODE=true
   ENABLE_API=true
   ```

### Quick Mode Examples

**Using Command Line Arguments:**
```bash
# Single-user mode (no authentication)
python run.py --single-user

# Multi-tenant mode with API
python run.py --with-api

# Single-user mode with API
python run.py --single-user --with-api

# Custom server settings
python run.py --port 8080 --host 127.0.0.1

# Debug mode with public sharing
python run.py --debug --share
```

**Using Environment Variables:**
```bash
# Single-user mode
MULTITENANT_MODE=false python run.py

# Multi-tenant with API
ENABLE_API=true python run.py

# Production mode with PostgreSQL
DB_TYPE=postgres POSTGRES_DSN="postgresql://user:pass@localhost/prompts" python run.py

# Full configuration
MULTITENANT_MODE=true ENABLE_API=true SERVER_PORT=8080 DEBUG=false python run.py
```

---

## 🌐 Multi-Language Support

AI Prompt Manager supports **10 languages** with real-time interface switching, making it accessible to users worldwide. The internationalization system provides comprehensive translations for all UI elements.

### 🌍 Supported Languages

| Language | Code | Native Name | Status |
|----------|------|-------------|--------|
| **English** | `en` | English | ✅ Complete |
| **Spanish** | `es` | Español | ✅ Complete |
| **French** | `fr` | Français | ✅ Complete |
| **German** | `de` | Deutsch | ✅ Complete |
| **Chinese** | `zh` | 中文 | ✅ Complete |
| **Japanese** | `ja` | 日本語 | ✅ Complete |
| **Portuguese** | `pt` | Português | ✅ Complete |
| **Russian** | `ru` | Русский | ✅ Complete |
| **Arabic** | `ar` | العربية | ✅ Complete |
| **Hindi** | `hi` | हिन्दी | ✅ Complete |

### 🔄 How to Change Language

#### **Method 1: Using the Interface (Recommended)**
1. **Locate the Language Selector**: Look for the 🌐 Language dropdown in the top-right corner
2. **Select Your Language**: Click the dropdown and choose your preferred language
3. **Instant Update**: The interface will immediately switch to the selected language

#### **Method 2: Environment Configuration**
Set the default language for new sessions:

```bash
# Set default language (optional)
DEFAULT_LANGUAGE=es python run.py  # Spanish
DEFAULT_LANGUAGE=fr python run.py  # French
DEFAULT_LANGUAGE=zh python run.py  # Chinese
```

#### **Method 3: URL Parameter**
Access the interface with a specific language:

```bash
# Examples
http://localhost:7860/?lang=es  # Spanish
http://localhost:7860/?lang=fr  # French
http://localhost:7860/?lang=zh  # Chinese
```

### 🎯 What Gets Translated

The multi-language system covers **all user-facing elements**:

#### **Interface Elements**
- ✅ Navigation menus and tabs
- ✅ Button labels and actions
- ✅ Form fields and placeholders
- ✅ Status messages and notifications
- ✅ Help text and tooltips

#### **Application Sections**
- ✅ **Authentication**: Login forms, SSO options
- ✅ **Prompt Management**: Add, edit, delete prompts
- ✅ **Library**: Search, categories, filters
- ✅ **Token Calculator**: Model selection, cost estimation
- ✅ **API Management**: Token creation, documentation
- ✅ **Settings**: Configuration options
- ✅ **Admin Panel**: User and tenant management

#### **AI Features**
- ✅ **LangWatch Integration**: Optimization interface
- ✅ **Enhancement Engine**: Prompt improvement tools
- ✅ **Error Messages**: Validation and system feedback

### 🌐 Translation Feature

When using the interface in a non-English language, AI Prompt Manager provides an automatic **translation feature** to help you work with AI enhancement tools that work best with English prompts.

#### **How Translation Works**

1. **Automatic Detection**: Translation button appears automatically when UI language is not English
2. **One-Click Translation**: Click "Translate to English" button in prompt editor
3. **Smart Replacement**: Translated text replaces original content in the editor
4. **Validation**: Translated text undergoes validation before saving
5. **Status Feedback**: Clear success/error messages guide the process

#### **Supported Translation Services**

| Service | Quality | Setup | Cost |
|---------|---------|-------|------|
| **OpenAI** | ⭐⭐⭐⭐⭐ | API Key | Paid |
| **Google Translate** | ⭐⭐⭐⭐ | API Key | Paid |
| **LibreTranslate** | ⭐⭐⭐ | Optional Key | Free/Paid |
| **Mock** | ⭐ | None | Free |

#### **Configuration**

Set up translation services via environment variables:

```bash
# Use OpenAI for highest quality
TRANSLATION_SERVICE=openai
OPENAI_API_KEY=your_openai_api_key

# Use Google Translate  
TRANSLATION_SERVICE=google
GOOGLE_TRANSLATE_API_KEY=your_google_key

# Use LibreTranslate (open source)
TRANSLATION_SERVICE=libre
LIBRETRANSLATE_URL=https://libretranslate.de/translate
LIBRETRANSLATE_API_KEY=optional_key

# Use mock for testing (default)
TRANSLATION_SERVICE=mock
```

#### **Usage Workflow**

1. **Switch Language**: Change UI to your preferred language (Spanish, French, etc.)
2. **Write Prompt**: Enter your prompt in your native language
3. **Translate**: Click the "🌐 Translate to English" button that appears
4. **Enhance**: Use the translated English text with AI enhancement tools
5. **Save**: Save the improved prompt after validation

#### **Example**

```text
Original (Spanish): "Escribe un poema sobre la naturaleza"
Translated (English): "Write a poem about nature"  
Enhanced (English): "Create a beautiful, evocative poem about the wonders 
                     of nature, focusing on vivid imagery and emotional depth"
```

### 🔧 Advanced Configuration

#### **Programmatic Language Control**
Access the internationalization system programmatically:

```python
from i18n import i18n, t

# Get available languages
languages = i18n.get_available_languages()
print(languages)  # {'en': 'English', 'es': 'Español', ...}

# Change language
i18n.set_language('es')

# Translate text
title = t('app.title')  # Returns translated app title
welcome = t('auth.welcome', name='John')  # With parameters
```

#### **Custom Translations**
Extend translations for custom deployments:

```python
# Add custom translations
from i18n import i18n

# Add new language or extend existing
custom_translations = {
    'custom.message': 'My custom message',
    'custom.button': 'Custom Button'
}

# Extend existing language
i18n.translations['en'].update(custom_translations)
```

### 🌟 Language Features

#### **Smart Fallbacks**
- **Automatic Fallback**: Missing translations default to English
- **Graceful Degradation**: Untranslated keys display as readable text
- **Context Preservation**: Formatting and parameters work across all languages

#### **Cultural Considerations**
- **Text Direction**: Right-to-left support for Arabic
- **Number Formatting**: Locale-appropriate number display
- **Date Formats**: Regional date and time formatting
- **Currency**: Localized cost estimates in token calculator

#### **Accessibility**
- **Screen Readers**: Proper language attributes for assistive technology
- **Keyboard Navigation**: Language switching via keyboard shortcuts
- **High Contrast**: Language selector works with accessibility themes

### 🎨 UI Adaptations

The interface automatically adapts to different languages:

#### **Layout Flexibility**
- **Dynamic Text Sizing**: Accommodates longer/shorter translations
- **Responsive Labels**: Forms adjust to text length variations
- **Icon Consistency**: Universal icons complement text labels

#### **Typography**
- **Font Support**: Web fonts that support all character sets
- **Readability**: Optimized contrast and spacing for each language
- **Consistency**: Unified styling across all language versions

### 🔍 Technical Details

#### **Translation Architecture**
- **Embedded Translations**: No external files required for reliability
- **Key-Based System**: Hierarchical translation keys (e.g., `auth.login`)
- **Parameter Support**: Dynamic content with variable substitution
- **Caching**: Efficient translation loading and memory usage

#### **File Structure**
```
ai-prompt-manager/
├── i18n.py                 # Internationalization system
├── ui_components.py        # Language-aware UI components
└── prompt_manager.py       # Main interface with i18n integration
```

#### **Browser Support**
- **Modern Browsers**: Full support in Chrome, Firefox, Safari, Edge
- **Fallback Support**: Graceful degradation in older browsers
- **Mobile Optimized**: Touch-friendly language switching on mobile devices

### ❓ Troubleshooting

#### **Common Issues**

**Language not switching immediately:**
- Refresh the page or restart the interface
- Check browser console for JavaScript errors

**Missing translations:**
- Some text remains in English - this is expected fallback behavior
- Report missing translations via GitHub issues

**Performance with many languages:**
- All translations are loaded efficiently in memory
- No performance impact from multiple language support

#### **Getting Help**
- 📖 **Documentation**: Check this guide for configuration details
- 🐛 **Bug Reports**: Report translation issues on GitHub
- 💡 **Feature Requests**: Suggest new languages or improvements
- 🌍 **Community**: Join discussions about localization

---

## 🧮 Token Calculator Guide

### What are Tokens?

**Tokens** are the basic units that AI models use to process text. Understanding tokens is crucial for:
- **Cost Control**: AI services charge based on token usage
- **Performance**: More tokens = longer processing time
- **Limits**: Models have maximum token limits per request

### How Tokenization Works

- **Words aren't tokens**: "Hello world" = 2 tokens, but "artificial intelligence" = 4 tokens
- **Subwords**: Long words are split (e.g., "understanding" = 2-3 tokens)
- **Special characters**: Punctuation and symbols count as tokens
- **Languages vary**: Non-English text may use more tokens

### Using the Token Calculator

#### 1. **Access the Calculator**
- Navigate to **Prompt Management** tab after logging in
- Find the **🧮 Token Calculator** section below the prompt content area

#### 2. **Calculate Token Costs**

1. **Enter your prompt** in the "Prompt Content" field
2. **Select target AI model** from the dropdown:
   - `gpt-4` - Most accurate, higher cost
   - `gpt-3.5-turbo` - Fast and economical
   - `claude-3-opus` - High-quality reasoning
   - `gemini-pro` - Google's model
3. **Set max completion tokens** - Expected response length (500-2000 typical)
4. **Click "🧮 Calculate Tokens"**

#### 3. **Understanding Results**

The calculator provides:
```
🧮 Token Estimate for gpt-4

📝 Prompt Tokens: 45        ← Your input text
💬 Max Completion Tokens: 1,000  ← Expected response
📊 Total Tokens: 1,045     ← Combined usage
⚙️ Tokenizer: gpt-4        ← Method used

💰 Estimated Cost: $0.0615 USD
   • Input: $0.0014         ← Cost for your prompt
   • Output: $0.0600        ← Cost for AI response

⚠️ Suggestions:
   • Large prompt may be expensive
   • Consider breaking into smaller prompts
```

#### 4. **Cost Optimization Tips**

**Reduce Costs:**
- ✅ Use shorter, more focused prompts
- ✅ Choose appropriate models (GPT-3.5 for simple tasks)
- ✅ Set reasonable completion token limits
- ✅ Remove repetitive content

**Performance Tips:**
- ⚡ Shorter prompts = faster responses
- ⚡ Fewer tokens = less processing time
- ⚡ Structure prompts clearly for better results

#### 5. **Model Comparison**

| Model | Best For | Cost | Speed | Quality |
|-------|----------|------|-------|---------|
| `gpt-4` | Complex reasoning, code | $$$ | Slower | Highest |
| `gpt-3.5-turbo` | General tasks, chat | $ | Fast | Good |
| `claude-3-opus` | Analysis, writing | $$$ | Moderate | Excellent |
| `claude-3-haiku` | Simple tasks | $ | Fast | Good |
| `gemini-pro` | Multimodal, research | $$ | Moderate | Very Good |

### Token Calculator Features

- **Real-time Estimation**: Instant cost calculation as you type
- **Multi-Model Support**: Accurate tokenization for all major AI providers
- **Cost Breakdown**: Separate input/output cost analysis
- **Optimization Suggestions**: Automatic recommendations for efficiency
- **Complexity Analysis**: Detects repetitive or overly long content

---

## 📝 Prompt Management

### Creating Prompts

1. **Navigate to Prompt Management** tab
2. **Fill in prompt details:**
   - **Name**: Unique identifier (required)
   - **Title**: Descriptive title
   - **Category**: Organization (e.g., "Writing", "Analysis")
   - **Content**: Your AI prompt text
   - **Tags**: Comma-separated keywords

3. **Estimate costs** using the Token Calculator
4. **Optimize if needed** with LangWatch integration
5. **Save prompt** with "➕ Add Prompt"

### LangWatch Optimization

Improve your prompts with AI-powered suggestions:

1. **Add optimization context** - Describe your prompt's purpose
2. **Select target model** - Choose your intended AI model
3. **Click "🚀 Optimize with LangWatch"**
4. **Review suggestions** - See score, reasoning, and improvements
5. **Accept, retry, or reject** - Choose the best version

### Prompt Library

- **Browse all prompts** in organized tree view
- **Search by keywords** - Name, title, content, or tags
- **Filter by category** - Organize by type or purpose
- **Quick actions** - Load, edit, or delete prompts

---

## 🔑 API Access

### Setting Up API Access

1. **Navigate to Account Settings → API Tokens**
2. **Create new token:**
   - Enter descriptive name
   - Set expiration (optional, 30 days recommended)
   - Click "🔑 Create Token"
3. **Copy token immediately** - You won't see it again!

### Using the API

**Base URL:** `http://localhost:7860/api`

**Authentication:**
```bash
Authorization: Bearer apm_your_token_here
```

**Common Endpoints:**
```bash
# List all prompts
GET /api/prompts

# Get specific prompt
GET /api/prompts/name/my-prompt-name

# Search prompts
GET /api/search?q=creative

# Get categories
GET /api/categories
```

**Example Usage:**
```bash
curl -H "Authorization: Bearer apm_abc123..." \
     http://localhost:7860/api/prompts
```

**Interactive Documentation:**
- Swagger UI: `http://localhost:7860/api/docs`
- ReDoc: `http://localhost:7860/api/redoc`

---

## ⚙️ Configuration

### Environment Setup

Create a `.env` file with your settings:

```env
# Application Mode
MULTITENANT_MODE=true          # Enable multi-tenant mode (default: true)
ENABLE_API=false               # Enable REST API endpoints (default: false)

# Server Configuration  
SERVER_HOST=0.0.0.0           # Server host (default: 0.0.0.0)
SERVER_PORT=7860              # Server port (default: 7860)

# Database Configuration
DB_TYPE=sqlite                # Database type: sqlite or postgres (default: sqlite)
DB_PATH=prompts.db           # SQLite database path (default: prompts.db)
POSTGRES_DSN=postgresql://user:pass@localhost:5432/dbname

# Authentication & Security
SECRET_KEY=your-secure-secret-key    # JWT signing secret (auto-generated if not set)
LOCAL_DEV_MODE=true                 # Enable local development features (default: false)

# SSO/ADFS Integration (optional)
SSO_ENABLED=false
SSO_CLIENT_ID=your-application-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
SSO_REDIRECT_URI=http://localhost:7860/auth/callback

# AI Service Integration (optional)
LANGWATCH_API_KEY=your-langwatch-api-key
LANGWATCH_PROJECT_ID=ai-prompt-manager

# Development & Debugging
DEBUG=false                   # Enable debug mode (default: false)
```

### Complete Environment Variable Reference

| Variable | Description | Default | Command Line Override |
|----------|-------------|---------|----------------------|
| `MULTITENANT_MODE` | Enable multi-tenant architecture | `true` | `--single-user` / `--multi-tenant` |
| `ENABLE_API` | Enable REST API endpoints | `false` | `--with-api` |
| `SERVER_HOST` | Server bind address | `0.0.0.0` | `--host HOST` |
| `SERVER_PORT` | Server port | `7860` | `--port PORT` |
| `DB_TYPE` | Database type (sqlite/postgres) | `sqlite` | - |
| `DB_PATH` | SQLite database file path | `prompts.db` | - |
| `POSTGRES_DSN` | PostgreSQL connection string | - | - |
| `SECRET_KEY` | JWT signing secret | auto-generated | - |
| `LOCAL_DEV_MODE` | Enable development features | `true` | - |
| `SSO_ENABLED` | Enable SSO authentication | `false` | - |
| `SSO_CLIENT_ID` | SSO application ID | - | - |
| `SSO_CLIENT_SECRET` | SSO client secret | - | - |
| `SSO_AUTHORITY` | SSO authority URL | - | - |
| `DEBUG` | Enable debug logging | `false` | `--debug` |
| `GRADIO_SHARE` | Enable public sharing | `false` | `--share` |

### Database Options

**SQLite (Development):**
- Zero setup required
- File-based storage
- Single-user friendly

**PostgreSQL (Production):**
- Better performance
- Multi-user support
- Enterprise features

### AI Service Integration

Supported AI providers:
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **LM Studio** (Local models)
- **Ollama** (Self-hosted)
- **Llama.cpp** (Local inference)

Configure in the application's AI Service Settings.

---

## 🏢 Multi-Tenant Features

### For Organizations

- **Complete Data Isolation** - Each tenant's data is separate
- **User Management** - Add users with different roles
- **Admin Dashboard** - Monitor usage and manage tenants
- **SSO Integration** - Connect with existing authentication

### User Roles

- **Admin**: Full system access, user management
- **User**: Create and manage prompts, API access
- **Readonly**: View prompts only, no modifications

### Default Credentials

For local development:
- **Tenant**: `localhost`
- **Email**: `admin@localhost`
- **Password**: `admin123`

---

## 🚀 Development

### Development Commands

```bash
# Install dependencies
poetry install

# Run application in different modes
python run.py                                # Default: Multi-tenant
python run.py --single-user                  # Single-user mode
python run.py --with-api                     # Multi-tenant + API
python run.py --single-user --with-api       # Single-user + API

# Development options
python run.py --debug                        # Enable debug mode
python run.py --share                        # Enable public sharing
python run.py --port 8080                    # Custom port
python run.py --help                         # Show all options

# Testing
python test_mt_install.py                    # Multi-tenant setup
python test_langwatch_integration.py         # LangWatch features
python test_standalone_api.py                # API integration
```

### Docker Development

```bash
# Build and run
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager

# With environment variables
docker run -p 7860:7860 \
  -e MULTITENANT_MODE=false \
  -e ENABLE_API=true \
  ai-prompt-manager

# With PostgreSQL
docker-compose up -d
```

### Architecture

**Core Components:**
- `prompt_manager.py` - Unified web interface (single-user + multi-tenant)
- `prompt_data_manager.py` - Database abstraction with tenant isolation
- `auth_manager.py` - Authentication and user management
- `token_calculator.py` - Token estimation engine
- `langwatch_optimizer.py` - Prompt optimization
- `api_endpoints.py` - REST API implementation
- `api_token_manager.py` - Secure API token management

### Database Schema

**Multi-Tenant Architecture:**
```
tenants
├── id (UUID)
├── name
├── subdomain  
├── max_users
├── is_active
└── created_at

users
├── id (UUID)
├── tenant_id (FK)
├── email (unique per tenant)
├── password_hash
├── first_name, last_name
├── role (admin|user|readonly)
├── sso_id (optional)
├── is_active
├── created_at
└── last_login

prompts
├── id
├── tenant_id (FK) - ensures tenant isolation
├── user_id (FK) - tracks ownership
├── name (unique per tenant)
├── title, content, category, tags
├── is_enhancement_prompt
├── created_at
└── updated_at

config
├── id
├── tenant_id (FK)
├── user_id (FK)
├── key, value - stores user/tenant settings
└── created_at

api_tokens
├── id (UUID)
├── user_id (FK)
├── tenant_id (FK)
├── name
├── token_hash
├── token_prefix
├── expires_at (optional)
├── last_used
└── created_at
```

### Security Architecture

**Multi-Layer Security:**
- **PBKDF2 Password Hashing**: Secure password storage with salt
- **JWT Session Tokens**: Stateless authentication with expiration
- **Tenant Row-Level Security**: Complete data isolation between organizations
- **Role-Based Access Control**: Granular permission system
- **API Token Management**: Secure programmatic access
- **Session Validation**: Automatic token validation and renewal

**Data Isolation:**
- All database queries include tenant_id filtering
- Users cannot access data outside their tenant
- Admin users can manage their tenant only
- Complete separation of configurations and prompts

---

## 🔒 Production Deployment

### Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Set `LOCAL_DEV_MODE=false`
- [ ] Use PostgreSQL database
- [ ] Configure HTTPS/TLS
- [ ] Set up proper SSO/ADFS
- [ ] Configure firewall rules
- [ ] Implement backup procedures
- [ ] Monitor application logs

### Production Docker

```bash
# Set environment variables
export SECRET_KEY="your-production-secret-key"
export SSO_ENABLED="true"
export MULTITENANT_MODE="true"
export ENABLE_API="true"

# Deploy with published images
docker-compose -f docker-compose.prod.yml up -d

# Single command with all options
docker run -p 7860:7860 \
  -e MULTITENANT_MODE=true \
  -e ENABLE_API=true \
  -e SECRET_KEY="your-production-secret" \
  -e DB_TYPE=postgres \
  -e POSTGRES_DSN="postgresql://user:pass@db:5432/prompts" \
  ghcr.io/makercorn/ai-prompt-manager:latest
```

**Available Images:**
- `ghcr.io/makercorn/ai-prompt-manager:latest` - Latest build
- `ghcr.io/makercorn/ai-prompt-manager:v1.0.0` - Tagged releases

---

## 🚀 Multi-Language Quick Reference

### 🌐 **Language Codes & Commands**

| Language | Code | Environment | URL Parameter | Native Name |
|----------|------|-------------|---------------|-------------|
| English | `en` | `DEFAULT_LANGUAGE=en` | `?lang=en` | English |
| Spanish | `es` | `DEFAULT_LANGUAGE=es` | `?lang=es` | Español |
| French | `fr` | `DEFAULT_LANGUAGE=fr` | `?lang=fr` | Français |
| German | `de` | `DEFAULT_LANGUAGE=de` | `?lang=de` | Deutsch |
| Chinese | `zh` | `DEFAULT_LANGUAGE=zh` | `?lang=zh` | 中文 |
| Japanese | `ja` | `DEFAULT_LANGUAGE=ja` | `?lang=ja` | 日本語 |
| Portuguese | `pt` | `DEFAULT_LANGUAGE=pt` | `?lang=pt` | Português |
| Russian | `ru` | `DEFAULT_LANGUAGE=ru` | `?lang=ru` | Русский |
| Arabic | `ar` | `DEFAULT_LANGUAGE=ar` | `?lang=ar` | العربية |
| Hindi | `hi` | `DEFAULT_LANGUAGE=hi` | `?lang=hi` | हिन्दी |

### ⚡ **Quick Commands**

```bash
# Start with Spanish interface
DEFAULT_LANGUAGE=es python run.py

# Start with Chinese interface  
DEFAULT_LANGUAGE=zh python run.py

# Access with URL parameter
curl "http://localhost:7860/?lang=fr"

# Multi-tenant with French
DEFAULT_LANGUAGE=fr MULTITENANT_MODE=true python run.py

# API with German interface
DEFAULT_LANGUAGE=de ENABLE_API=true python run.py

# Translation service with Spanish UI
DEFAULT_LANGUAGE=es TRANSLATION_SERVICE=openai OPENAI_API_KEY=key python run.py
```

### 🌐 **Translation Configuration**

```bash
# OpenAI translation (best quality)
TRANSLATION_SERVICE=openai
OPENAI_API_KEY=your_openai_key

# Google Translate
TRANSLATION_SERVICE=google
GOOGLE_TRANSLATE_API_KEY=your_google_key

# LibreTranslate (free)
TRANSLATION_SERVICE=libre
LIBRETRANSLATE_URL=https://libretranslate.de/translate

# Mock for testing (default)
TRANSLATION_SERVICE=mock
```

### 🔧 **Developer Integration**

```python
# Quick language switching in code
from i18n import i18n, t

# Available languages
langs = i18n.get_available_languages()

# Switch language
i18n.set_language('es')  # Spanish
print(t('app.title'))    # "Gestor de Prompts IA"

# With parameters
print(t('auth.welcome', name='María'))  # "¡Bienvenido, María!"

# Translation API
from text_translator import text_translator

# Check if translation is needed
if text_translator.is_translation_needed():
    success, translated, error = text_translator.translate_to_english("Hola mundo")
    print(f"Translated: {translated}")
```

---

## 📚 Additional Resources

### Testing

**Comprehensive Test Suite:**
```bash
# Install test dependencies
poetry install --with dev

# Core functionality tests
python test_mt_install.py           # Multi-tenant setup
python test_standalone_api.py       # API integration
python test_langwatch_integration.py # LangWatch features
python test_api_integration.py      # Full API test suite

# Component testing
python -c "
from prompt_data_manager import PromptDataManager
from auth_manager import AuthManager

# Test database initialization  
auth = AuthManager('test.db')
data = PromptDataManager('test.db', tenant_id='test', user_id='test')
print('✅ All components working correctly!')

# Cleanup
import os
os.remove('test.db')
"

# Multi-tenant isolation testing
python -c "
from auth_manager import AuthManager
auth = AuthManager('test_isolation.db')

# Create two tenants
tenant1_id = auth.create_tenant('Company A', 'company-a', 100)[1]
tenant2_id = auth.create_tenant('Company B', 'company-b', 50)[1] 

print('✅ Tenant isolation test passed')
"

# Test different launcher modes
python run.py --help                         # Show all options
MULTITENANT_MODE=false python run.py &       # Start in single-user mode
sleep 2 && pkill -f "python run.py"          # Stop test server
```

**Docker Testing:**
```bash
# Test Docker build
docker build -t ai-prompt-manager-test .
docker run --rm -p 7860:7860 ai-prompt-manager-test

# Test with PostgreSQL
docker-compose -f docker-compose.yml up -d
# Wait for services to start
docker-compose logs ai-prompt-manager
```

### CI/CD Pipeline

- **Automated Testing** - Python tests, Docker builds, integration tests
- **Docker Publishing** - GitHub Container Registry with multi-tag strategy  
- **Release Management** - Automated releases with changelog generation

**📋 Setup Guide:** See [GITHUB_WORKFLOWS_SETUP.md](GITHUB_WORKFLOWS_SETUP.md) for complete workflow configuration instructions.

### Troubleshooting

**Common Issues and Solutions:**

**🔧 Database Connection Issues**
```bash
# SQLite permission errors
chmod 664 prompts.db
chown user:group prompts.db

# PostgreSQL connection errors
psql -h localhost -U username -d dbname  # Test connection
export POSTGRES_DSN="postgresql://user:pass@host:port/db"
```

**🔐 Authentication Problems**
```bash
# Reset admin password (emergency)
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
auth.create_user('tenant-id', 'admin@localhost', 'newpassword', 'Admin', 'User', 'admin')
"

# Check tenant configuration
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
tenants = auth.get_all_tenants()
for t in tenants: print(f'Tenant: {t.name} ({t.subdomain})')
"
```

**🌐 Network and Port Issues**
```bash
# Check if port is in use
lsof -i :7860
netstat -tulpn | grep 7860

# Test application startup
python run.py --single-user --debug
```

**🐳 Docker Issues**
```bash
# Check container logs
docker logs ai-prompt-manager

# Test database connectivity
docker exec -it ai-prompt-manager python -c "
from prompt_data_manager import PromptDataManager
data = PromptDataManager('prompts.db')
print('Database connection successful')
"
```

**🚨 Emergency Recovery**
```bash
# Backup database
cp prompts.db prompts.db.backup

# Reset to clean state (CAUTION: Loses all data)
rm prompts.db
python -c "from auth_manager import AuthManager; AuthManager('prompts.db')"
```

### Support

- 📖 **Documentation**: Comprehensive guides and API reference in this README
- 🐛 **Issues**: Report bugs and request features via GitHub Issues
- 💬 **Community**: Join discussions and share prompts
- 🔧 **Troubleshooting**: See troubleshooting section above for common solutions
- 📋 **Testing**: Use provided test scripts to verify functionality

---

## 📄 License

**Non-Commercial License** - This software is licensed for non-commercial use only.

### Usage Rights
- ✅ **Personal use** - Individual, educational, and research purposes
- ✅ **Non-profit organizations** - For non-commercial activities  
- ✅ **Academic institutions** - Research and educational use
- ❌ **Commercial use** - Business operations, revenue generation, or profit
- ❌ **Selling or licensing** - Without explicit commercial license agreement

### Commercial Licensing
For commercial use, please contact the copyright holder to obtain a separate commercial license agreement.

See the [LICENSE](LICENSE) file for complete details.

---

**🔐 Secure • 🧮 Cost-Aware • 🚀 Optimized • 🤖 AI-Powered • 🔌 API-Ready**