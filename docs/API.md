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
async function listPrompts(category = null, search = null) {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (search) params.append('search', search);
  
  const response = await fetch(`${API_BASE}/prompts?${params}`, { headers });
  const data = await response.json();
  console.log(`Found ${data.total} prompts`);
  return data.prompts;
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