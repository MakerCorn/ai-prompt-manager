# AI Prompt Manager

A comprehensive AI prompt management system with multi-tenant architecture, featuring authentication, token cost estimation, prompt optimization, and secure API access.

## 🌟 Key Features

- 🔐 **Multi-Tenant Security** - Complete data isolation between organizations
- 🧮 **Token Calculator** - Real-time cost estimation for AI model usage
- 🚀 **LangWatch Integration** - AI-powered prompt optimization
- 🔑 **Secure API** - RESTful endpoints with token-based authentication
- 🛡️ **SSO/ADFS Support** - Enterprise authentication integration
- 📊 **Admin Dashboard** - Comprehensive tenant and user management

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
```

2. **Launch Application**
```bash
# Multi-tenant version with API (recommended)
poetry run python run_mt_with_api.py

# Single-user version
poetry run python prompt_manager.py
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

Create `.env` file with your settings:

```env
# Database
DB_TYPE=sqlite              # or postgres
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

# LangWatch (optional)
LANGWATCH_API_KEY=your-langwatch-api-key
LANGWATCH_PROJECT_ID=ai-prompt-manager
```

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

# Run applications
poetry run python prompt_manager.py          # Single-user
poetry run python run_mt.py                  # Multi-tenant
poetry run python run_mt_with_api.py         # Multi-tenant + API

# Testing
poetry run python test_mt_install.py         # Multi-tenant setup
poetry run python test_langwatch_integration.py  # LangWatch
```

### Docker Development

```bash
# Build and run
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager

# With PostgreSQL
docker-compose up -d
```

### Architecture

**Core Components:**
- `prompt_manager_mt.py` - Multi-tenant web interface
- `prompt_data_manager.py` - Database abstraction
- `auth_manager.py` - Authentication and user management
- `token_calculator.py` - Token estimation engine
- `langwatch_optimizer.py` - Prompt optimization
- `api_endpoints.py` - REST API implementation

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

# Deploy with published images
docker-compose -f docker-compose.prod.yml up -d
```

**Available Images:**
- `ghcr.io/makercorn/ai-prompt-manager:latest` - Latest build
- `ghcr.io/makercorn/ai-prompt-manager:v1.0.0` - Tagged releases

---

## 📚 Additional Resources

### Testing

```bash
# API integration
poetry run python test_standalone_api.py

# Multi-tenant setup
poetry run python test_mt_install.py

# LangWatch features
poetry run python test_langwatch_integration.py
```

### CI/CD Pipeline

- **Automated Testing** - Python tests, Docker builds, integration tests
- **Docker Publishing** - GitHub Container Registry with multi-tag strategy  
- **Release Management** - Automated releases with changelog generation

**📋 Setup Guide:** See [GITHUB_WORKFLOWS_SETUP.md](GITHUB_WORKFLOWS_SETUP.md) for complete workflow configuration instructions.

### Support

- 📖 **Documentation**: Comprehensive guides and API reference
- 🐛 **Issues**: Report bugs and request features
- 💬 **Community**: Join discussions and share prompts

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