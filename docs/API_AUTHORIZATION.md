# API Authorization Guide

## Overview

The AI Prompt Manager provides a comprehensive RESTful API with robust token-based authentication. This guide covers everything you need to know about API authorization, token management, and secure API usage.

## Table of Contents

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Token Management](#token-management)
- [API Endpoints](#api-endpoints)
- [Security Best Practices](#security-best-practices)
- [Code Examples](#code-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Testing](#testing)

## Quick Start

### 1. Create an API Token

1. Log into the web interface
2. Navigate to **Settings** → **API Tokens**
3. Click **Generate Token**
4. Provide a descriptive name and set expiration
5. Copy the generated token (shown only once)

### 2. Make Your First API Call

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     "https://your-domain.com/api/user/info"
```

## Authentication

### Bearer Token Authentication

All API endpoints (except `/api/health`) require authentication using Bearer tokens in the Authorization header:

```
Authorization: Bearer apm_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Token Format

API tokens follow the format: `apm_` followed by 32 characters of base64url-encoded random data.

Example: `apm_Dk8sF2mN9pL3qR7tY4vB6zX8uI1oE5wA`

### Security Features

- **Secure Generation**: Tokens use cryptographically secure random generation
- **Hashed Storage**: Only SHA256 hashes are stored in the database
- **Expiration Support**: Configurable expiration dates
- **Usage Tracking**: Last-used timestamps for security monitoring
- **Tenant Isolation**: Tokens are isolated by tenant for multi-tenant security

## Token Management

### Creating Tokens

#### Web Interface
Navigate to **Settings** → **API Tokens** → **Generate Token**

#### API Endpoint
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_EXISTING_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Token",
    "expires_days": 30
  }' \
  "https://your-domain.com/api/tokens"
```

Response:
```json
{
  "success": true,
  "message": "API token 'My New Token' created successfully (expires in 30 days)",
  "token": "apm_Dk8sF2mN9pL3qR7tY4vB6zX8uI1oE5wA",
  "token_info": {
    "id": "uuid-here",
    "name": "My New Token",
    "token_prefix": "apm_Dk8sF2mN",
    "expires_at": "2025-02-06T10:30:00Z",
    "created_at": "2025-01-07T10:30:00Z",
    "is_active": true
  }
}
```

### Listing Tokens

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/tokens"
```

Response:
```json
{
  "success": true,
  "message": "API tokens retrieved successfully",
  "data": {
    "tokens": [
      {
        "id": "uuid-here",
        "name": "Production API",
        "token_prefix": "apm_Dk8sF2mN",
        "expires_at": "2025-02-06T10:30:00Z",
        "last_used": "2025-01-07T09:15:00Z",
        "created_at": "2025-01-07T10:30:00Z",
        "is_active": true
      }
    ],
    "stats": {
      "total_active": 3,
      "never_expire": 1,
      "will_expire": 2,
      "used_tokens": 2
    }
  }
}
```

### Revoking Tokens

#### Single Token
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://your-domain.com/api/tokens/TOKEN_ID"
```

#### All Tokens
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://your-domain.com/api/tokens"
```

## API Endpoints

### Authentication Required

All endpoints except `/api/health` require authentication:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/info` | Get current user information |
| GET | `/api/prompts` | List prompts with pagination |
| GET | `/api/prompts/{id}` | Get specific prompt by ID |
| GET | `/api/prompts/name/{name}` | Get specific prompt by name |
| GET | `/api/categories` | List prompt categories |
| GET | `/api/search?q={query}` | Search prompts |
| GET | `/api/stats` | Get user statistics |
| GET | `/api/tokens` | List API tokens |
| POST | `/api/tokens` | Create new API token |
| GET | `/api/tokens/{id}` | Get specific token details |
| DELETE | `/api/tokens/{id}` | Revoke specific token |
| DELETE | `/api/tokens` | Revoke all tokens |
| GET | `/api/tokens/stats` | Get token statistics |

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check (no auth required) |
| GET | `/api/docs` | API documentation (Swagger UI) |
| GET | `/api/redoc` | API documentation (ReDoc) |

## Security Best Practices

### Token Management
- **Use descriptive names** for tokens to identify their purpose
- **Set appropriate expiration** dates (30-90 days recommended)
- **Rotate tokens regularly** for enhanced security
- **Revoke unused tokens** immediately
- **Use different tokens** for different applications/environments

### Storage and Transmission
- **Never log tokens** in application logs
- **Use environment variables** or secure vaults for token storage
- **Always use HTTPS** in production
- **Don't include tokens** in URLs or query parameters
- **Implement proper error handling** to avoid token leakage

### Monitoring
- **Monitor token usage** through the dashboard
- **Review last-used timestamps** regularly
- **Set up alerts** for unusual API activity
- **Audit token access** patterns

## Code Examples

### Python with requests

```python
import requests
import os

# Store token securely
API_TOKEN = os.getenv('PROMPTMAN_API_TOKEN')
BASE_URL = 'https://your-domain.com/api'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Get user info
response = requests.get(f'{BASE_URL}/user/info', headers=headers)
if response.status_code == 200:
    user_data = response.json()
    print(f"Logged in as: {user_data['data']['user']['email']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# List prompts
response = requests.get(f'{BASE_URL}/prompts', headers=headers)
if response.status_code == 200:
    prompts = response.json()
    print(f"Total prompts: {prompts['total']}")
    for prompt in prompts['prompts']:
        print(f"- {prompt['name']}: {prompt['title']}")

# Search prompts
params = {'q': 'email', 'page': 1, 'page_size': 10}
response = requests.get(f'{BASE_URL}/search', headers=headers, params=params)
if response.status_code == 200:
    results = response.json()
    print(f"Found {results['total']} prompts matching 'email'")

# Create new token
token_data = {
    'name': 'Python Client Token',
    'expires_days': 30
}
response = requests.post(f'{BASE_URL}/tokens', headers=headers, json=token_data)
if response.status_code == 200:
    new_token = response.json()
    print(f"Created token: {new_token['token']}")
    # IMPORTANT: Store this token securely, it won't be shown again
```

### JavaScript/Node.js with axios

```javascript
const axios = require('axios');

const apiClient = axios.create({
  baseURL: 'https://your-domain.com/api',
  headers: {
    'Authorization': `Bearer ${process.env.PROMPTMAN_API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('Authentication failed - check your API token');
    }
    return Promise.reject(error);
  }
);

async function getUserInfo() {
  try {
    const response = await apiClient.get('/user/info');
    console.log('User:', response.data.data.user.email);
    return response.data;
  } catch (error) {
    console.error('Failed to get user info:', error.message);
  }
}

async function listPrompts(page = 1, pageSize = 50) {
  try {
    const response = await apiClient.get('/prompts', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to list prompts:', error.message);
  }
}

async function searchPrompts(query) {
  try {
    const response = await apiClient.get('/search', {
      params: { q: query }
    });
    return response.data;
  } catch (error) {
    console.error('Search failed:', error.message);
  }
}

async function createToken(name, expiryDays = 30) {
  try {
    const response = await apiClient.post('/tokens', {
      name,
      expires_days: expiryDays
    });
    console.log('New token created:', response.data.token);
    return response.data;
  } catch (error) {
    console.error('Token creation failed:', error.message);
  }
}

// Usage examples
(async () => {
  await getUserInfo();
  const prompts = await listPrompts();
  console.log(`Found ${prompts?.total || 0} prompts`);
  
  const searchResults = await searchPrompts('business email');
  console.log(`Search found ${searchResults?.total || 0} results`);
})();
```

### PHP with cURL

```php
<?php

class PromptManagerAPI {
    private $baseUrl;
    private $token;
    
    public function __construct($baseUrl, $token) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->token = $token;
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $curl = curl_init();
        
        $headers = [
            'Authorization: Bearer ' . $this->token,
            'Content-Type: application/json'
        ];
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->baseUrl . $endpoint,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_SSL_VERIFYPEER => true,
        ]);
        
        if ($data && in_array($method, ['POST', 'PUT', 'PATCH'])) {
            curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($curl);
        $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($httpCode >= 200 && $httpCode < 300) {
            return json_decode($response, true);
        } else {
            throw new Exception("API Error: HTTP $httpCode - $response");
        }
    }
    
    public function getUserInfo() {
        return $this->makeRequest('GET', '/api/user/info');
    }
    
    public function listPrompts($page = 1, $pageSize = 50) {
        $endpoint = "/api/prompts?page=$page&page_size=$pageSize";
        return $this->makeRequest('GET', $endpoint);
    }
    
    public function searchPrompts($query, $page = 1) {
        $endpoint = "/api/search?q=" . urlencode($query) . "&page=$page";
        return $this->makeRequest('GET', $endpoint);
    }
    
    public function getPromptByName($name) {
        $endpoint = "/api/prompts/name/" . urlencode($name);
        return $this->makeRequest('GET', $endpoint);
    }
    
    public function createToken($name, $expiryDays = 30) {
        return $this->makeRequest('POST', '/api/tokens', [
            'name' => $name,
            'expires_days' => $expiryDays
        ]);
    }
    
    public function listTokens() {
        return $this->makeRequest('GET', '/api/tokens');
    }
    
    public function revokeToken($tokenId) {
        return $this->makeRequest('DELETE', "/api/tokens/$tokenId");
    }
}

// Usage example
try {
    $api = new PromptManagerAPI(
        'https://your-domain.com',
        $_ENV['PROMPTMAN_API_TOKEN']
    );
    
    $userInfo = $api->getUserInfo();
    echo "Logged in as: " . $userInfo['data']['user']['email'] . "\n";
    
    $prompts = $api->listPrompts();
    echo "Total prompts: " . $prompts['total'] . "\n";
    
    $searchResults = $api->searchPrompts('email template');
    echo "Search results: " . $searchResults['total'] . "\n";
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "time"
)

type APIClient struct {
    BaseURL string
    Token   string
    Client  *http.Client
}

type APIResponse struct {
    Success bool        `json:"success"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func NewAPIClient(baseURL, token string) *APIClient {
    return &APIClient{
        BaseURL: baseURL,
        Token:   token,
        Client: &http.Client{
            Timeout: 30 * time.Second,
        },
    }
}

func (c *APIClient) makeRequest(method, endpoint string, body interface{}) (*APIResponse, error) {
    var reqBody io.Reader
    if body != nil {
        jsonData, err := json.Marshal(body)
        if err != nil {
            return nil, err
        }
        reqBody = bytes.NewBuffer(jsonData)
    }
    
    req, err := http.NewRequest(method, c.BaseURL+endpoint, reqBody)
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("Authorization", "Bearer "+c.Token)
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := c.Client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var apiResp APIResponse
    if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
        return nil, err
    }
    
    if resp.StatusCode >= 400 {
        return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, apiResp.Message)
    }
    
    return &apiResp, nil
}

func (c *APIClient) GetUserInfo() (*APIResponse, error) {
    return c.makeRequest("GET", "/api/user/info", nil)
}

func (c *APIClient) ListPrompts(page, pageSize int) (*APIResponse, error) {
    endpoint := fmt.Sprintf("/api/prompts?page=%d&page_size=%d", page, pageSize)
    return c.makeRequest("GET", endpoint, nil)
}

func (c *APIClient) SearchPrompts(query string) (*APIResponse, error) {
    endpoint := "/api/search?q=" + url.QueryEscape(query)
    return c.makeRequest("GET", endpoint, nil)
}

func (c *APIClient) CreateToken(name string, expiryDays int) (*APIResponse, error) {
    body := map[string]interface{}{
        "name":        name,
        "expires_days": expiryDays,
    }
    return c.makeRequest("POST", "/api/tokens", body)
}

func main() {
    token := os.Getenv("PROMPTMAN_API_TOKEN")
    if token == "" {
        fmt.Println("Please set PROMPTMAN_API_TOKEN environment variable")
        return
    }
    
    client := NewAPIClient("https://your-domain.com", token)
    
    // Get user info
    userInfo, err := client.GetUserInfo()
    if err != nil {
        fmt.Printf("Error getting user info: %v\n", err)
        return
    }
    fmt.Printf("API client initialized successfully\n")
    
    // List prompts
    prompts, err := client.ListPrompts(1, 10)
    if err != nil {
        fmt.Printf("Error listing prompts: %v\n", err)
        return
    }
    fmt.Printf("Retrieved prompts successfully\n")
    
    // Search prompts
    searchResults, err := client.SearchPrompts("business email")
    if err != nil {
        fmt.Printf("Error searching prompts: %v\n", err)
        return
    }
    fmt.Printf("Search completed successfully\n")
}
```

## Error Handling

### HTTP Status Codes

| Code | Description | Meaning |
|------|-------------|---------|
| 200 | OK | Request successful |
| 401 | Unauthorized | Invalid or missing token |
| 403 | Forbidden | Token valid but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Invalid request data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "success": false,
  "message": "Detailed error description",
  "detail": "Additional technical details (if available)"
}
```

### Common Error Scenarios

#### Invalid Token
```bash
# Request
curl -H "Authorization: Bearer invalid_token" \
     "https://your-domain.com/api/user/info"

# Response (401)
{
  "detail": "Invalid or expired API token"
}
```

#### Missing Authorization Header
```bash
# Request
curl "https://your-domain.com/api/user/info"

# Response (401)
{
  "detail": "Missing authorization header"
}
```

#### Token Expired
```bash
# Response (401)
{
  "detail": "Invalid or expired API token"
}
```

## Rate Limiting

Currently, the API doesn't implement rate limiting, but it's recommended to:

- **Respect the service** with reasonable request rates
- **Implement client-side throttling** for bulk operations
- **Use pagination** for large data sets
- **Cache responses** when appropriate

Future versions may implement rate limiting with the following headers:
- `X-RateLimit-Limit`: Request limit per time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Testing

### Using curl for Quick Tests

```bash
# Test authentication
curl -w "%{http_code}\n" -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/user/info"

# Test health endpoint (no auth)
curl -w "%{http_code}\n" "https://your-domain.com/api/health"

# Test token creation
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test Token","expires_days":1}' \
     "https://your-domain.com/api/tokens"
```

### Automated Testing

```python
import requests
import pytest

class TestAPIAuthorization:
    def setup_method(self):
        self.base_url = "https://your-domain.com/api"
        self.token = "your-test-token"
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_health_endpoint_no_auth(self):
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
    
    def test_protected_endpoint_no_auth(self):
        response = requests.get(f"{self.base_url}/user/info")
        assert response.status_code == 401
    
    def test_protected_endpoint_invalid_token(self):
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{self.base_url}/user/info", headers=headers)
        assert response.status_code == 401
    
    def test_protected_endpoint_valid_token(self):
        response = requests.get(f"{self.base_url}/user/info", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check token is correctly formatted
   - Verify token hasn't expired
   - Ensure proper Authorization header format

2. **Token not working after creation**
   - Copy the full token including `apm_` prefix
   - Check for trailing spaces or hidden characters
   - Verify the token wasn't revoked

3. **SSL/TLS Errors**
   - Ensure you're using HTTPS in production
   - Check certificate validity
   - Update CA certificates if needed

4. **Network timeouts**
   - Increase client timeout settings
   - Check firewall rules
   - Verify DNS resolution

### Debug Checklist

- [ ] Token includes `apm_` prefix
- [ ] Authorization header format: `Bearer {token}`
- [ ] Using HTTPS in production
- [ ] Token hasn't expired
- [ ] User has appropriate permissions
- [ ] API endpoint URL is correct
- [ ] Content-Type header set for POST requests

## Conclusion

The AI Prompt Manager API provides a secure, comprehensive interface for programmatic access to prompt management functionality. By following the security best practices and using the provided examples, you can integrate the API into your applications safely and effectively.

For additional support or questions, please refer to the main documentation or contact the development team.