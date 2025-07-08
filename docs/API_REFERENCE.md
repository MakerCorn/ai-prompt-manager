# 🔌 API Reference

A comprehensive guide to the AI Prompt Manager REST API, including authentication, endpoints, and examples.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Code Examples](#code-examples)
6. [Error Handling](#error-handling)

---

## Overview

The AI Prompt Manager provides a comprehensive REST API for programmatic access to prompt management functionality. The API features secure token-based authentication, multi-tenant isolation, and comprehensive CRUD operations.

### Key Features

- **🔐 Secure Authentication**: Bearer token-based authentication with API tokens
- **🏢 Multi-Tenant Support**: Complete tenant isolation for enterprise deployments
- **📝 Full CRUD Operations**: Create, read, update, delete prompts and templates
- **🏷️ Advanced Tagging**: Tag management with search and analytics
- **🔍 Visibility Controls**: Public/private prompt sharing
- **🌐 Multi-Language**: Full internationalization support
- **📊 Real-time Analytics**: Usage statistics and performance metrics

## Architecture

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

## Authentication

### API Token Authentication

The API uses Bearer token authentication with secure API tokens.

#### Getting an API Token

1. **Via Web Interface**:
   - Login to the web interface
   - Navigate to Settings → API Tokens
   - Click "Generate New Token"
   - Copy and securely store the token

2. **Token Format**:
   - Prefix: `apm_` (AI Prompt Manager)
   - Length: 32 characters
   - Example: `apm_1234567890abcdef1234567890abcdef`

#### Using API Tokens

Include the token in the Authorization header:

```http
Authorization: Bearer apm_1234567890abcdef1234567890abcdef
```

#### Token Management

**Security Features:**
- **Cryptographically Secure**: Generated using secure random algorithms
- **Expiration Support**: Configurable token expiration for enhanced security
- **Usage Tracking**: Last-used timestamps and comprehensive statistics
- **Tenant Isolation**: Multi-tenant security with complete data separation

**Token Operations:**
- **Create**: Generate new API tokens
- **List**: View all tokens with metadata
- **Revoke**: Immediately invalidate tokens
- **Update**: Modify token descriptions

## API Endpoints

### Core Endpoints

#### Health Check
```http
GET /health
```
**Description**: Check API server health status
**Authentication**: Not required
**Response**: `{"status": "healthy", "timestamp": "2025-01-01T12:00:00Z"}`

#### Server Information
```http
GET /info
```
**Description**: Get API server information and capabilities
**Authentication**: Not required

### Prompt Management

#### List Prompts
```http
GET /api/prompts
```

**Query Parameters:**
- `category` (optional): Filter by category
- `tags` (optional): Comma-separated list of tags
- `visibility` (optional): `public`, `private`, or `all`
- `search` (optional): Search term for prompt content
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "example-prompt",
      "content": "Write a professional email about...",
      "category": "Business",
      "tags": ["email", "professional"],
      "visibility": "private",
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### Get Prompt
```http
GET /api/prompts/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "example-prompt",
  "content": "Write a professional email about...",
  "category": "Business",
  "tags": ["email", "professional"],
  "visibility": "private",
  "token_count": 25,
  "estimated_cost": 0.0015,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### Create Prompt
```http
POST /api/prompts
```

**Request Body:**
```json
{
  "name": "new-prompt",
  "content": "Write a professional email about...",
  "category": "Business",
  "tags": ["email", "professional"],
  "visibility": "private"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "new-prompt",
  "content": "Write a professional email about...",
  "category": "Business",
  "tags": ["email", "professional"],
  "visibility": "private",
  "token_count": 25,
  "estimated_cost": 0.0015,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### Update Prompt
```http
PUT /api/prompts/{id}
```

**Request Body:**
```json
{
  "name": "updated-prompt",
  "content": "Write an updated professional email about...",
  "category": "Business",
  "tags": ["email", "professional", "updated"],
  "visibility": "public"
}
```

#### Delete Prompt
```http
DELETE /api/prompts/{id}
```

**Response:**
```json
{
  "message": "Prompt deleted successfully",
  "id": 1
}
```

### Template Management

#### List Templates
```http
GET /api/templates
```

#### Get Template
```http
GET /api/templates/{id}
```

#### Create Template
```http
POST /api/templates
```

#### Update Template
```http
PUT /api/templates/{id}
```

#### Delete Template
```http
DELETE /api/templates/{id}
```

### Tag Management

#### List Tags
```http
GET /api/tags
```

**Response:**
```json
{
  "tags": [
    {
      "name": "email",
      "usage_count": 15,
      "color": "#3b82f6"
    },
    {
      "name": "professional",
      "usage_count": 12,
      "color": "#10b981"
    }
  ],
  "total": 2
}
```

#### Get Tag Analytics
```http
GET /api/tags/analytics
```

### Optimization Services

#### Optimize Prompt
```http
POST /api/optimize
```

**Request Body:**
```json
{
  "prompt": "Write email to customer",
  "service": "langwatch"
}
```

#### Calculate Tokens
```http
POST /api/calculate-tokens
```

**Request Body:**
```json
{
  "text": "Write a professional email about project updates",
  "model": "gpt-4"
}
```

#### Translate Text
```http
POST /api/translate
```

**Request Body:**
```json
{
  "text": "Hello world",
  "target_language": "es",
  "source_language": "en"
}
```

## Code Examples

### Python

```python
import requests
import json

class PromptManagerAPI:
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def list_prompts(self, category=None, tags=None, limit=50):
        """List prompts with optional filtering"""
        params = {'limit': limit}
        if category:
            params['category'] = category
        if tags:
            params['tags'] = ','.join(tags)
        
        response = requests.get(
            f'{self.base_url}/api/prompts',
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def create_prompt(self, name, content, category=None, tags=None, visibility='private'):
        """Create a new prompt"""
        data = {
            'name': name,
            'content': content,
            'visibility': visibility
        }
        if category:
            data['category'] = category
        if tags:
            data['tags'] = tags
        
        response = requests.post(
            f'{self.base_url}/api/prompts',
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def optimize_prompt(self, prompt):
        """Optimize a prompt using AI services"""
        response = requests.post(
            f'{self.base_url}/api/optimize',
            headers=self.headers,
            json={'prompt': prompt}
        )
        return response.json()

# Usage example
api = PromptManagerAPI('http://localhost:7861', 'apm_your_token_here')

# List all prompts
prompts = api.list_prompts()
print(f"Found {len(prompts['prompts'])} prompts")

# Create a new prompt
new_prompt = api.create_prompt(
    name='api-test-prompt',
    content='Write a summary of the key features',
    category='Documentation',
    tags=['api', 'documentation'],
    visibility='private'
)
print(f"Created prompt with ID: {new_prompt['id']}")

# Optimize the prompt
optimized = api.optimize_prompt(new_prompt['content'])
if optimized['success']:
    print(f"Optimized prompt: {optimized['optimized_prompt']}")
```

### JavaScript/Node.js

```javascript
class PromptManagerAPI {
    constructor(baseUrl, apiToken) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }

    async listPrompts(options = {}) {
        const params = new URLSearchParams();
        if (options.category) params.append('category', options.category);
        if (options.tags) params.append('tags', options.tags.join(','));
        if (options.limit) params.append('limit', options.limit);

        const response = await fetch(`${this.baseUrl}/api/prompts?${params}`, {
            headers: this.headers
        });
        return response.json();
    }

    async createPrompt(promptData) {
        const response = await fetch(`${this.baseUrl}/api/prompts`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(promptData)
        });
        return response.json();
    }

    async optimizePrompt(prompt) {
        const response = await fetch(`${this.baseUrl}/api/optimize`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ prompt })
        });
        return response.json();
    }
}

// Usage example
const api = new PromptManagerAPI('http://localhost:7861', 'apm_your_token_here');

// List prompts
api.listPrompts({ category: 'Business', limit: 10 })
    .then(data => console.log(`Found ${data.prompts.length} prompts`));

// Create prompt
api.createPrompt({
    name: 'js-test-prompt',
    content: 'Generate a project roadmap for Q1',
    category: 'Planning',
    tags: ['planning', 'roadmap'],
    visibility: 'private'
}).then(data => console.log(`Created prompt: ${data.id}`));
```

### cURL

```bash
# Set your API token
API_TOKEN="apm_your_token_here"
BASE_URL="http://localhost:7861"

# List prompts
curl -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     "$BASE_URL/api/prompts"

# Create a new prompt
curl -X POST \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "curl-test-prompt",
       "content": "Write a technical specification for...",
       "category": "Technical",
       "tags": ["specification", "technical"],
       "visibility": "private"
     }' \
     "$BASE_URL/api/prompts"

# Get specific prompt
curl -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     "$BASE_URL/api/prompts/1"

# Optimize a prompt
curl -X POST \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Write email"}' \
     "$BASE_URL/api/optimize"

# Calculate token count
curl -X POST \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Write a comprehensive project plan",
       "model": "gpt-4"
     }' \
     "$BASE_URL/api/calculate-tokens"
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type PromptManagerAPI struct {
    BaseURL  string
    APIToken string
    Client   *http.Client
}

type Prompt struct {
    ID         int      `json:"id,omitempty"`
    Name       string   `json:"name"`
    Content    string   `json:"content"`
    Category   string   `json:"category,omitempty"`
    Tags       []string `json:"tags,omitempty"`
    Visibility string   `json:"visibility"`
}

func NewPromptManagerAPI(baseURL, apiToken string) *PromptManagerAPI {
    return &PromptManagerAPI{
        BaseURL:  baseURL,
        APIToken: apiToken,
        Client:   &http.Client{},
    }
}

func (api *PromptManagerAPI) makeRequest(method, endpoint string, body interface{}) (*http.Response, error) {
    var reqBody bytes.Buffer
    if body != nil {
        json.NewEncoder(&reqBody).Encode(body)
    }

    req, err := http.NewRequest(method, api.BaseURL+endpoint, &reqBody)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+api.APIToken)
    req.Header.Set("Content-Type", "application/json")

    return api.Client.Do(req)
}

func (api *PromptManagerAPI) CreatePrompt(prompt Prompt) (*Prompt, error) {
    resp, err := api.makeRequest("POST", "/api/prompts", prompt)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result Prompt
    err = json.NewDecoder(resp.Body).Decode(&result)
    return &result, err
}

// Usage example
func main() {
    api := NewPromptManagerAPI("http://localhost:7861", "apm_your_token_here")
    
    prompt := Prompt{
        Name:       "go-test-prompt",
        Content:    "Create a Go microservice architecture",
        Category:   "Development",
        Tags:       []string{"go", "microservices"},
        Visibility: "private",
    }
    
    created, err := api.CreatePrompt(prompt)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    
    fmt.Printf("Created prompt with ID: %d\n", created.ID)
}
```

## Error Handling

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Invalid or missing API token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid prompt data",
    "details": {
      "name": ["Name is required"],
      "content": ["Content cannot be empty"]
    }
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Scenarios

#### Authentication Errors
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API token"
  }
}
```

#### Validation Errors
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "name": ["Name must be unique"],
      "visibility": ["Must be 'public' or 'private'"]
    }
  }
}
```

#### Rate Limiting
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

### Best Practices

1. **Always check HTTP status codes** before processing response data
2. **Implement exponential backoff** for rate-limited requests
3. **Store API tokens securely** and rotate them regularly
4. **Use pagination** for large result sets
5. **Handle network timeouts** gracefully
6. **Log API requests** for debugging and monitoring
7. **Validate data** before sending requests
8. **Use HTTPS** in production environments

### Support

For API support and questions:
- **Documentation**: Check this API reference and user guide
- **Issues**: Report bugs via GitHub issues
- **Community**: Join discussions in the project repository

---

*This API reference covers the core functionality of the AI Prompt Manager API. For specific implementation details and advanced use cases, refer to the source code and integration tests.*