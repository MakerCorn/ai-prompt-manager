# 🔌 AI Prompt Manager API Documentation

## Overview

The AI Prompt Manager provides a comprehensive REST API for programmatic access to prompt management functionality. The API features secure token-based authentication, multi-tenant isolation, and comprehensive CRUD operations.

## 🏗️ Architecture

### Dual-Server Architecture

The API system uses a **dual-server architecture** for optimal performance and separation of concerns:

- **Web UI Server**: Runs on main port (e.g., 7860) - Handles web interface
- **API Server**: Runs on main port + 1 (e.g., 7861) - Handles API requests
- **Unified Management**: Both servers managed by single `run.py --with-api` command

```bash
# Start with API enabled
poetry run python run.py --with-api --port 7860

# Access points:
# Web UI: http://localhost:7860
# API: http://localhost:7861
# API Docs: http://localhost:7861/docs
```

### Base URL

```
http://localhost:7861/api
```

### Content Type

All API endpoints accept and return JSON data:

```
Content-Type: application/json
```

## 🔐 Authentication

### API Token Authentication

The API uses Bearer token authentication with secure API tokens.

#### Getting an API Token

1. **Via Web Interface**:
   - Login to the web interface
   - Navigate to **Settings → API Tokens**
   - Click **Create New Token**
   - Copy the generated token (shown only once)

2. **Token Format**:
   ```
   apm_1234567890abcdef...
   ```

#### Using the Token

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/health
```

### Multi-Tenant Security

- Each API token is scoped to a specific tenant
- Users can only access data within their tenant
- Complete data isolation between tenants

## 📚 Core Endpoints

### Health Check

Check if the API server is running.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T10:30:00.000Z"
}
```

**Example:**
```bash
curl http://localhost:7861/api/health
```

---

### User Information

Get current authenticated user information.

```http
GET /api/user/info
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "user": {
      "user_id": "user-123",
      "tenant_id": "tenant-456",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user"
    },
    "token_stats": {
      "active_tokens": 2,
      "last_used": "2025-01-08T10:25:00.000Z"
    }
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/user/info
```

---

## 📝 Prompt Management

### List Prompts

Get a paginated list of prompts with optional filtering.

```http
GET /api/prompts
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `category` (string, optional): Filter by category
- `search` (string, optional): Search in name, title, content
- `include_enhancement` (boolean, default: true): Include enhancement prompts
- `visibility` (string, optional): Filter by visibility ('private', 'public', or 'all')
- `include_public` (boolean, default: true): Include public prompts from other users

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "blog-intro",
      "title": "Blog Introduction Generator",
      "content": "Write an engaging introduction for a blog post about {topic}...",
      "category": "Writing",
      "tags": "blog, introduction, content",
      "visibility": "public",
      "is_enhancement_prompt": false,
      "user_id": "user-123",
      "created_at": "2025-01-08T09:00:00.000Z",
      "updated_at": "2025-01-08T09:00:00.000Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 50
}
```

**Examples:**
```bash
# List all prompts
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts

# List prompts with pagination
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?page=2&page_size=10"

# Filter by category
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?category=Writing"

# Search prompts
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?search=blog"

# Filter by visibility
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?visibility=public"

# Show only your own prompts (private + public)
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?include_public=false"
```

---

### Get Prompt by ID

Retrieve a specific prompt by its ID.

```http
GET /api/prompts/{prompt_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Prompt retrieved successfully",
  "data": {
    "prompt": {
      "id": 1,
      "name": "blog-intro",
      "title": "Blog Introduction Generator",
      "content": "Write an engaging introduction for a blog post about {topic}...",
      "category": "Writing",
      "tags": "blog, introduction, content",
      "visibility": "public",
      "is_enhancement_prompt": false,
      "user_id": "user-123",
      "created_at": "2025-01-08T09:00:00.000Z",
      "updated_at": "2025-01-08T09:00:00.000Z"
    }
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/1
```

---

### Get Prompt by Name

Retrieve a specific prompt by its name.

```http
GET /api/prompts/name/{prompt_name}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Prompt retrieved successfully",
  "data": {
    "prompt": {
      "name": "blog-intro",
      "title": "Blog Introduction Generator",
      "content": "Write an engaging introduction for a blog post about {topic}...",
      "category": "Writing",
      "tags": "blog, introduction, content"
    }
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/name/blog-intro
```

---

### Search Prompts

Search prompts across name, title, and content.

```http
GET /api/search?q={search_query}
Authorization: Bearer {token}
```

**Query Parameters:**
- `q` (string, required): Search query
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `include_enhancement` (boolean, default: true): Include enhancement prompts
- `visibility` (string, optional): Filter by visibility ('private', 'public', or 'all')
- `include_public` (boolean, default: true): Include public prompts from other users

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "blog-intro",
      "title": "Blog Introduction Generator",
      "content": "Write an engaging introduction for a blog post...",
      "category": "Writing",
      "tags": "blog, introduction, content",
      "visibility": "public",
      "is_enhancement_prompt": false,
      "user_id": "user-123",
      "created_at": "2025-01-08T09:00:00.000Z",
      "updated_at": "2025-01-08T09:00:00.000Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 50
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/search?q=blog"
```

---

## 👁️ Prompt Visibility

The AI Prompt Manager supports a comprehensive visibility system that allows users to control who can see and access their prompts within a tenant. This feature is only available in multi-tenant mode.

### Visibility Levels

- **Private**: Only visible to the prompt creator
- **Public**: Visible to all users within the same tenant

### Get Prompts by Visibility

Filter prompts by their visibility level.

```http
GET /api/prompts/visibility/{visibility_level}
Authorization: Bearer {token}
```

**Path Parameters:**
- `visibility_level` (string): 'private' or 'public'

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `include_enhancement` (boolean, default: true): Include enhancement prompts

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "public-prompt",
      "title": "Public Prompt Example",
      "content": "This is a public prompt visible to all users in the tenant...",
      "category": "Public",
      "tags": "public, shared",
      "visibility": "public",
      "is_enhancement_prompt": false,
      "user_id": "user-456",
      "created_at": "2025-01-08T09:00:00.000Z",
      "updated_at": "2025-01-08T09:00:00.000Z"
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 50
}
```

**Examples:**
```bash
# Get all public prompts in tenant
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/visibility/public

# Get all private prompts (user's own only)
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/visibility/private
```

---

### Get Public Prompts

Get all public prompts within the current tenant.

```http
GET /api/prompts/public
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `category` (string, optional): Filter by category
- `include_enhancement` (boolean, default: true): Include enhancement prompts

**Response:**
```json
{
  "prompts": [
    {
      "id": 2,
      "name": "shared-template",
      "title": "Shared Template for Team",
      "content": "This template is shared with the entire team...",
      "category": "Templates",
      "tags": "team, shared, template",
      "visibility": "public",
      "is_enhancement_prompt": false,
      "user_id": "user-789",
      "created_at": "2025-01-08T08:30:00.000Z",
      "updated_at": "2025-01-08T08:30:00.000Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 50
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/public
```

---

### Get Visibility Statistics

Get statistics about prompt visibility within the current tenant.

```http
GET /api/prompts/visibility-stats
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Visibility statistics retrieved successfully",
  "data": {
    "total_prompts": 50,
    "private_prompts": 32,
    "public_prompts": 18,
    "private_percentage": 64.0,
    "public_percentage": 36.0
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts/visibility-stats
```

---

### Visibility Filtering Examples

The visibility system affects all prompt listing and search endpoints:

```bash
# Get all prompts (user's own + public from others) - DEFAULT
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts"

# Get only user's own prompts (private + public)
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?include_public=false"

# Get only public prompts from other users
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts/public"

# Filter by specific visibility level
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts?visibility=private"

# Search with visibility filtering
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/search?q=template&visibility=public"
```

### Visibility Behavior

1. **Default Behavior**: By default, users see their own prompts (both private and public) plus public prompts from other users in their tenant
2. **Privacy Protection**: Private prompts are never visible to other users
3. **Tenant Isolation**: Public prompts are only visible within the same tenant
4. **Single-User Mode**: In single-user mode, all prompts are treated as accessible (visibility filtering is disabled)

---

## 📂 Categories

### List Categories

Get all available categories for the current tenant.

```http
GET /api/categories
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "data": {
    "categories": [
      "Writing",
      "Code",
      "Analysis",
      "Creative",
      "Business",
      "Technical"
    ]
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/categories
```

---

### Get Prompts by Category

Get all prompts in a specific category.

```http
GET /api/prompts/category/{category_name}
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `include_enhancement` (boolean, default: true): Include enhancement prompts

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "blog-intro",
      "title": "Blog Introduction Generator",
      "content": "Write an engaging introduction...",
      "category": "Writing",
      "tags": "blog, introduction, content",
      "is_enhancement_prompt": false,
      "user_id": "user-123",
      "created_at": "2025-01-08T09:00:00.000Z",
      "updated_at": "2025-01-08T09:00:00.000Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 50
}
```

**Example:**
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     "http://localhost:7861/api/prompts/category/Writing"
```

---

## 🎤 Speech Dictation

AI-powered speech-to-text functionality with text enhancement and translation capabilities.

### Text Enhancement

Enhance dictated text by removing filler words, correcting grammar, and improving structure.

```http
POST /enhance-text
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded

text=dictated_content&type=dictation
```

**Parameters:**
- `text` (required): The dictated text to enhance
- `type` (optional): Type of enhancement, defaults to "dictation"

**Response:**
```json
{
  "success": true,
  "enhanced_text": "Clean, enhanced version of the dictated text.",
  "original_text": "um hello world this is a test you know"
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer apm_your_token_here" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=um hello world this is a test you know&type=dictation" \
  "http://localhost:7861/enhance-text"
```

### Text Translation

Translate dictated text from any supported language to English.

```http
POST /translate
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded

text=content_to_translate&target_lang=en
```

**Parameters:**
- `text` (required): The text to translate
- `target_lang` (optional): Target language code, defaults to "en" (English)

**Response:**
```json
{
  "success": true,
  "translated_text": "Hello world, this is a test",
  "original_text": "Bonjour le monde, ceci est un test",
  "error": null
}
```

**Supported Languages:**
- English (en), Spanish (es), French (fr), German (de)
- Italian (it), Portuguese (pt), Dutch (nl), Russian (ru)
- Chinese (zh), Japanese (ja), Korean (ko), Arabic (ar)

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer apm_your_token_here" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Bonjour le monde&target_lang=en" \
  "http://localhost:7861/translate"
```

### Speech Dictation Features

**🎤 Text Enhancement Capabilities:**
- **Filler Word Removal**: Removes "um", "uh", "you know", "basically", etc.
- **Grammar Correction**: Fixes punctuation, capitalization, sentence structure
- **AI Optimization**: Uses configured AI services for advanced enhancement
- **Fallback Processing**: Regex-based enhancement when AI services unavailable

**🌐 Translation Features:**
- **Multi-Language Support**: 12+ languages supported
- **Context Awareness**: Preserves technical terminology and meaning
- **Automatic Detection**: Detects source language automatically
- **Batch Processing**: Handle multiple text segments efficiently

**🔒 Security & Privacy:**
- **Authentication Required**: All endpoints require valid Bearer token
- **Session Validation**: Ensures user session is active and valid
- **Local Processing**: Speech recognition happens in browser
- **Secure Transmission**: All API calls use HTTPS encryption

**⚡ Performance:**
- **Fast Processing**: Optimized text enhancement algorithms
- **Graceful Degradation**: Fallback when AI services unavailable
- **Error Handling**: Comprehensive error responses and logging
- **Browser Compatibility**: Works with Chrome, Edge, Safari, Firefox

---

## 📊 Response Format

### Standard API Response

All API endpoints (except health check) return responses in this format:

```json
{
  "success": boolean,
  "message": string,
  "data": object | null
}
```

### Paginated Response

List endpoints return paginated responses:

```json
{
  "prompts": [/* array of prompts */],
  "total": number,
  "page": number,
  "page_size": number
}
```

### Error Response

Error responses include detailed information:

```json
{
  "success": false,
  "message": "Error description",
  "data": {
    "error_code": "ERROR_CODE",
    "details": "Additional error details"
  }
}
```

## 🚨 Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing API token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Authentication Errors

```json
{
  "detail": "Invalid or expired API token"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

## 🛠️ Integration Examples

### Python Example

Using the `requests` library:

```python
import requests

# Configuration
API_BASE = "http://localhost:7861/api"
API_TOKEN = "apm_your_token_here"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# Get user information
response = requests.get(f"{API_BASE}/user/info", headers=HEADERS)
user_info = response.json()
print(f"User: {user_info['data']['user']['email']}")

# List prompts
response = requests.get(
    f"{API_BASE}/prompts",
    headers=HEADERS,
    params={"category": "Writing", "page_size": 10}
)
prompts = response.json()
print(f"Found {prompts['total']} writing prompts")

# List only public prompts
response = requests.get(
    f"{API_BASE}/prompts/public",
    headers=HEADERS,
    params={"page_size": 20}
)
public_prompts = response.json()
print(f"Found {public_prompts['total']} public prompts")

# Get visibility statistics
response = requests.get(f"{API_BASE}/prompts/visibility-stats", headers=HEADERS)
stats = response.json()
if stats["success"]:
    data = stats["data"]
    print(f"Visibility Stats: {data['private_prompts']} private, {data['public_prompts']} public")

# Search prompts
response = requests.get(
    f"{API_BASE}/search",
    headers=HEADERS,
    params={"q": "blog", "page": 1}
)
search_results = response.json()
for prompt in search_results['prompts']:
    print(f"- {prompt['title']}: {prompt['name']}")

# Get specific prompt
response = requests.get(f"{API_BASE}/prompts/1", headers=HEADERS)
prompt = response.json()
print(f"Prompt content: {prompt['data']['prompt']['content']}")
```

### JavaScript Example

Using `fetch` API:

```javascript
const API_BASE = 'http://localhost:7861/api';
const API_TOKEN = 'apm_your_token_here';
const headers = {
  'Authorization': `Bearer ${API_TOKEN}`,
  'Content-Type': 'application/json'
};

// Get user information
async function getUserInfo() {
  const response = await fetch(`${API_BASE}/user/info`, { headers });
  const data = await response.json();
  console.log('User:', data.data.user.email);
  return data;
}

// List prompts with filtering
async function listPrompts(category = null, search = null, visibility = null) {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (search) params.append('search', search);
  if (visibility) params.append('visibility', visibility);
  
  const response = await fetch(`${API_BASE}/prompts?${params}`, { headers });
  const data = await response.json();
  console.log(`Found ${data.total} prompts`);
  return data.prompts;
}

// Get public prompts only
async function getPublicPrompts() {
  const response = await fetch(`${API_BASE}/prompts/public`, { headers });
  const data = await response.json();
  console.log(`Found ${data.total} public prompts`);
  return data.prompts;
}

// Get visibility statistics
async function getVisibilityStats() {
  const response = await fetch(`${API_BASE}/prompts/visibility-stats`, { headers });
  const data = await response.json();
  if (data.success) {
    const stats = data.data;
    console.log(`Visibility: ${stats.private_prompts} private, ${stats.public_prompts} public`);
    return stats;
  }
  return null;
}

// Get specific prompt
async function getPrompt(promptId) {
  const response = await fetch(`${API_BASE}/prompts/${promptId}`, { headers });
  const data = await response.json();
  return data.data.prompt;
}

// Usage
getUserInfo().then(() => {
  listPrompts('Writing').then(prompts => {
    prompts.forEach(prompt => {
      console.log(`- ${prompt.title}: ${prompt.name}`);
    });
  });
});
```

### cURL Examples

```bash
#!/bin/bash

# Configuration
API_BASE="http://localhost:7861/api"
TOKEN="apm_your_token_here"
AUTH_HEADER="Authorization: Bearer $TOKEN"

# Health check
echo "=== Health Check ==="
curl -s "$API_BASE/health" | jq .

# User information
echo "=== User Info ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/user/info" | jq .

# List all prompts
echo "=== All Prompts ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts" | jq '.prompts[] | {name, title, category}'

# Filter by category
echo "=== Writing Prompts ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts?category=Writing" | jq '.prompts[] | .name'

# Search prompts
echo "=== Search Results ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/search?q=blog" | jq '.prompts[] | {name, title}'

# Get specific prompt
echo "=== Specific Prompt ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts/1" | jq '.data.prompt | {name, content}'

# List categories
echo "=== Categories ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/categories" | jq '.data.categories'

# Get public prompts
echo "=== Public Prompts ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts/public" | jq '.prompts[] | {name, title, visibility}'

# Get visibility statistics
echo "=== Visibility Statistics ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts/visibility-stats" | jq '.data'

# Filter by visibility
echo "=== Private Prompts Only ==="
curl -s -H "$AUTH_HEADER" "$API_BASE/prompts?visibility=private" | jq '.prompts[] | .name'
```

## 🔧 Configuration

### Environment Variables

```bash
# Enable API
ENABLE_API=true

# API Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=7860

# Security
SECRET_KEY=your-secure-secret-key

# Multi-tenant mode
MULTITENANT_MODE=true
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  app:
    image: ghcr.io/makercorn/ai-prompt-manager:latest
    ports:
      - "7860:7860"  # Web UI
      - "7861:7861"  # API Server
    environment:
      ENABLE_API: "true"
      MULTITENANT_MODE: "true"
```

## 📖 Interactive Documentation

### Swagger UI

Access interactive API documentation at:
```
http://localhost:7861/docs
```

### ReDoc

Alternative documentation format at:
```
http://localhost:7861/redoc
```

### OpenAPI Schema

Raw OpenAPI schema available at:
```
http://localhost:7861/openapi.json
```

## 🔒 Security Best Practices

### API Token Management

1. **Store tokens securely**: Never commit tokens to version control
2. **Use environment variables**: Store tokens in environment variables or secure vaults
3. **Rotate tokens regularly**: Create new tokens and revoke old ones periodically
4. **Monitor token usage**: Check token usage statistics regularly
5. **Use appropriate expiration**: Set reasonable expiration times for tokens

### Network Security

1. **Use HTTPS in production**: Always use HTTPS for production deployments
2. **Configure CORS properly**: Restrict CORS origins in production
3. **Rate limiting**: Implement rate limiting for API endpoints
4. **Firewall rules**: Restrict API access to authorized networks

### Multi-Tenant Security

1. **Data isolation**: API automatically enforces tenant isolation
2. **User permissions**: Tokens inherit user role permissions
3. **Audit logging**: Monitor API access for security auditing

## 🚨 Troubleshooting

### Common Issues

**API Server Not Starting:**
```bash
# Check if API is enabled
poetry run python run.py --with-api --debug

# Verify port availability
lsof -i :7861
```

**Authentication Errors:**
```bash
# Verify token format
echo "apm_your_token_here" | grep "^apm_"

# Test health endpoint (no auth required)
curl http://localhost:7861/api/health
```

**Connection Refused:**
```bash
# Check if both ports are exposed
docker run -p 7860:7860 -p 7861:7861 -e ENABLE_API=true your-image

# Verify API server is running
curl -v http://localhost:7861/api/health
```

**Token Validation Issues:**
```bash
# Test with curl verbose output
curl -v -H "Authorization: Bearer apm_your_token" \
     http://localhost:7861/api/user/info
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
poetry run python run.py --with-api --debug
```

## 📈 Rate Limits

Current rate limits (subject to change):

- **General endpoints**: 100 requests per minute per token
- **Search endpoints**: 30 requests per minute per token
- **Health check**: No rate limit

## 🔄 API Versioning

- **Current version**: v1.0.0
- **Backward compatibility**: Maintained for major versions
- **Deprecation policy**: 6 months notice for breaking changes

## 📞 Support

For API support and questions:

- **Documentation**: Check this guide and interactive docs
- **Issues**: Report API bugs on GitHub Issues
- **Discussions**: Join community discussions for API questions

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**