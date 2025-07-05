# 🚀 AI Prompt Manager API Examples

This document provides practical examples for integrating with the AI Prompt Manager API across different programming languages and frameworks.

## 📋 Table of Contents

- [Python Examples](#-python-examples)
- [JavaScript/Node.js Examples](#-javascriptnodejs-examples)
- [cURL Examples](#-curl-examples)
- [PHP Examples](#-php-examples)
- [Go Examples](#-go-examples)
- [Integration Patterns](#-integration-patterns)

## 🐍 Python Examples

### Basic Python Client

Create a simple Python client for the API:

```python
#!/usr/bin/env python3
"""
AI Prompt Manager API Client
Simple Python client for interacting with the API
"""

import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PromptManagerClient:
    base_url: str
    api_token: str
    
    def __post_init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> Dict:
        """Check if the API is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        response = requests.get(f"{self.base_url}/user/info", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_prompts(self, category: Optional[str] = None, 
                    search: Optional[str] = None, 
                    page: int = 1, 
                    page_size: int = 50) -> Dict:
        """List prompts with optional filtering"""
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
            
        response = requests.get(f"{self.base_url}/prompts", 
                              headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_prompt(self, prompt_id: int) -> Dict:
        """Get a specific prompt by ID"""
        response = requests.get(f"{self.base_url}/prompts/{prompt_id}", 
                              headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_prompt_by_name(self, prompt_name: str) -> Dict:
        """Get a specific prompt by name"""
        response = requests.get(f"{self.base_url}/prompts/name/{prompt_name}", 
                              headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_prompts(self, query: str, page: int = 1, page_size: int = 50) -> Dict:
        """Search prompts"""
        params = {"q": query, "page": page, "page_size": page_size}
        response = requests.get(f"{self.base_url}/search", 
                              headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        response = requests.get(f"{self.base_url}/categories", headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]["categories"]

# Usage example
def main():
    # Initialize client
    client = PromptManagerClient(
        base_url="http://localhost:7861/api",
        api_token="apm_your_token_here"
    )
    
    try:
        # Check API health
        health = client.health_check()
        print(f"API Status: {health['status']}")
        
        # Get user info
        user_info = client.get_user_info()
        print(f"User: {user_info['data']['user']['email']}")
        
        # List all prompts
        prompts = client.list_prompts(page_size=10)
        print(f"Total prompts: {prompts['total']}")
        
        # Search for writing prompts
        writing_prompts = client.list_prompts(category="Writing")
        print(f"Writing prompts: {writing_prompts['total']}")
        
        # Search prompts
        search_results = client.search_prompts("blog")
        print(f"Blog-related prompts: {search_results['total']}")
        
        # Get categories
        categories = client.get_categories()
        print(f"Available categories: {categories}")
        
        # Get specific prompt
        if prompts['total'] > 0:
            first_prompt = prompts['prompts'][0]
            detailed_prompt = client.get_prompt(first_prompt['id'])
            print(f"Prompt: {detailed_prompt['data']['prompt']['title']}")
            
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    main()
```

### Async Python Client

For high-performance applications using `aiohttp`:

```python
#!/usr/bin/env python3
"""
Async AI Prompt Manager API Client
High-performance async client using aiohttp
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional

class AsyncPromptManagerClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, 
                           params: Optional[Dict] = None) -> Dict:
        """Make an async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, 
                                     params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def health_check(self) -> Dict:
        """Check API health asynchronously"""
        # Health endpoint doesn't require auth
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json()
    
    async def get_user_info(self) -> Dict:
        """Get user info asynchronously"""
        return await self._make_request("GET", "/user/info")
    
    async def list_prompts(self, category: Optional[str] = None, 
                          search: Optional[str] = None) -> Dict:
        """List prompts asynchronously"""
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return await self._make_request("GET", "/prompts", params)
    
    async def search_prompts(self, query: str) -> Dict:
        """Search prompts asynchronously"""
        return await self._make_request("GET", "/search", {"q": query})

# Usage example
async def main():
    client = AsyncPromptManagerClient(
        base_url="http://localhost:7861/api",
        api_token="apm_your_token_here"
    )
    
    try:
        # Run multiple requests concurrently
        health_task = client.health_check()
        user_task = client.get_user_info()
        prompts_task = client.list_prompts()
        categories_task = client.search_prompts("writing")
        
        health, user_info, prompts, writing_results = await asyncio.gather(
            health_task, user_task, prompts_task, categories_task
        )
        
        print(f"API Status: {health['status']}")
        print(f"User: {user_info['data']['user']['email']}")
        print(f"Total prompts: {prompts['total']}")
        print(f"Writing prompts found: {writing_results['total']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🌐 JavaScript/Node.js Examples

### Node.js Client

```javascript
#!/usr/bin/env node
/**
 * AI Prompt Manager API Client - Node.js
 * Complete client implementation for Node.js applications
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

class PromptManagerClient {
  constructor(baseUrl, apiToken) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    };
  }

  async makeRequest(method, endpoint, params = null) {
    const url = new URL(endpoint, this.baseUrl);
    if (params && method === 'GET') {
      Object.keys(params).forEach(key => 
        url.searchParams.append(key, params[key])
      );
    }

    const isHttps = url.protocol === 'https:';
    const httpModule = isHttps ? https : http;

    return new Promise((resolve, reject) => {
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        headers: this.headers
      };

      const req = httpModule.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(jsonData);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${jsonData.detail || data}`));
            }
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${data}`));
          }
        });
      });

      req.on('error', reject);
      req.end();
    });
  }

  async healthCheck() {
    // Health endpoint doesn't require auth
    const tempHeaders = this.headers;
    this.headers = {};
    try {
      const result = await this.makeRequest('GET', '/health');
      this.headers = tempHeaders;
      return result;
    } catch (error) {
      this.headers = tempHeaders;
      throw error;
    }
  }

  async getUserInfo() {
    return this.makeRequest('GET', '/user/info');
  }

  async listPrompts({ category = null, search = null, page = 1, pageSize = 50 } = {}) {
    const params = { page, page_size: pageSize };
    if (category) params.category = category;
    if (search) params.search = search;
    
    return this.makeRequest('GET', '/prompts', params);
  }

  async getPrompt(promptId) {
    return this.makeRequest('GET', `/prompts/${promptId}`);
  }

  async getPromptByName(promptName) {
    return this.makeRequest('GET', `/prompts/name/${promptName}`);
  }

  async searchPrompts(query, { page = 1, pageSize = 50 } = {}) {
    return this.makeRequest('GET', '/search', { 
      q: query, 
      page, 
      page_size: pageSize 
    });
  }

  async getCategories() {
    const response = await this.makeRequest('GET', '/categories');
    return response.data.categories;
  }
}

// Usage example
async function main() {
  const client = new PromptManagerClient(
    'http://localhost:7861/api',
    'apm_your_token_here'
  );

  try {
    // Check health
    const health = await client.healthCheck();
    console.log(`API Status: ${health.status}`);

    // Get user info
    const userInfo = await client.getUserInfo();
    console.log(`User: ${userInfo.data.user.email}`);

    // List prompts
    const prompts = await client.listPrompts({ pageSize: 10 });
    console.log(`Total prompts: ${prompts.total}`);

    // Search prompts
    const searchResults = await client.searchPrompts('blog');
    console.log(`Blog prompts found: ${searchResults.total}`);

    // Get categories
    const categories = await client.getCategories();
    console.log(`Categories: ${categories.join(', ')}`);

    // Get specific prompt if available
    if (prompts.total > 0) {
      const firstPrompt = prompts.prompts[0];
      const detailedPrompt = await client.getPrompt(firstPrompt.id);
      console.log(`Prompt: ${detailedPrompt.data.prompt.title}`);
    }

  } catch (error) {
    console.error(`API Error: ${error.message}`);
  }
}

if (require.main === module) {
  main();
}

module.exports = PromptManagerClient;
```

### Browser/Frontend Client

```javascript
/**
 * AI Prompt Manager API Client - Browser
 * Client-side implementation for web applications
 */

class PromptManagerClient {
  constructor(baseUrl, apiToken) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    };
  }

  async makeRequest(method, endpoint, params = null) {
    const url = new URL(endpoint, this.baseUrl);
    
    const options = {
      method: method,
      headers: this.headers
    };

    if (params && method === 'GET') {
      Object.keys(params).forEach(key => 
        url.searchParams.append(key, params[key])
      );
    }

    try {
      const response = await fetch(url.toString(), options);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${data.detail || 'Unknown error'}`);
      }
      
      return data;
    } catch (error) {
      throw new Error(`Request failed: ${error.message}`);
    }
  }

  async healthCheck() {
    // Health endpoint doesn't require auth
    const tempHeaders = this.headers;
    this.headers = {};
    try {
      const result = await this.makeRequest('GET', '/health');
      this.headers = tempHeaders;
      return result;
    } catch (error) {
      this.headers = tempHeaders;
      throw error;
    }
  }

  async getUserInfo() {
    return this.makeRequest('GET', '/user/info');
  }

  async listPrompts({ category = null, search = null, page = 1, pageSize = 50 } = {}) {
    const params = { page, page_size: pageSize };
    if (category) params.category = category;
    if (search) params.search = search;
    
    return this.makeRequest('GET', '/prompts', params);
  }

  async searchPrompts(query, { page = 1, pageSize = 50 } = {}) {
    return this.makeRequest('GET', '/search', { 
      q: query, 
      page, 
      page_size: pageSize 
    });
  }

  async getCategories() {
    const response = await this.makeRequest('GET', '/categories');
    return response.data.categories;
  }
}

// Example usage in a web application
class PromptManager {
  constructor() {
    this.client = new PromptManagerClient(
      'http://localhost:7861/api', 
      localStorage.getItem('api_token')
    );
    this.init();
  }

  async init() {
    try {
      await this.loadUserInfo();
      await this.loadPrompts();
      await this.loadCategories();
    } catch (error) {
      console.error('Initialization failed:', error);
      this.showError('Failed to initialize. Please check your API token.');
    }
  }

  async loadUserInfo() {
    const userInfo = await this.client.getUserInfo();
    document.getElementById('user-email').textContent = userInfo.data.user.email;
    document.getElementById('user-role').textContent = userInfo.data.user.role;
  }

  async loadPrompts(category = null, search = null) {
    const promptsContainer = document.getElementById('prompts-container');
    promptsContainer.innerHTML = '<div class="loading">Loading prompts...</div>';

    try {
      const prompts = await this.client.listPrompts({ category, search, pageSize: 20 });
      this.renderPrompts(prompts.prompts);
      document.getElementById('prompt-count').textContent = `${prompts.total} prompts`;
    } catch (error) {
      promptsContainer.innerHTML = '<div class="error">Failed to load prompts</div>';
    }
  }

  async loadCategories() {
    const categories = await this.client.getCategories();
    const categorySelect = document.getElementById('category-filter');
    
    categorySelect.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(category => {
      const option = document.createElement('option');
      option.value = category;
      option.textContent = category;
      categorySelect.appendChild(option);
    });
  }

  renderPrompts(prompts) {
    const container = document.getElementById('prompts-container');
    container.innerHTML = '';

    prompts.forEach(prompt => {
      const promptElement = document.createElement('div');
      promptElement.className = 'prompt-card';
      promptElement.innerHTML = `
        <h3>${prompt.title}</h3>
        <p class="prompt-name">${prompt.name}</p>
        <p class="prompt-category">${prompt.category}</p>
        <p class="prompt-content">${prompt.content.substring(0, 150)}${prompt.content.length > 150 ? '...' : ''}</p>
        <div class="prompt-tags">${prompt.tags || ''}</div>
      `;
      
      promptElement.addEventListener('click', () => this.showPromptDetails(prompt.id));
      container.appendChild(promptElement);
    });
  }

  async showPromptDetails(promptId) {
    try {
      const response = await this.client.getPrompt(promptId);
      const prompt = response.data.prompt;
      
      // Show modal or detailed view
      this.showModal('Prompt Details', `
        <h3>${prompt.title}</h3>
        <p><strong>Name:</strong> ${prompt.name}</p>
        <p><strong>Category:</strong> ${prompt.category}</p>
        <p><strong>Content:</strong></p>
        <pre>${prompt.content}</pre>
        <p><strong>Tags:</strong> ${prompt.tags || 'None'}</p>
      `);
    } catch (error) {
      this.showError('Failed to load prompt details');
    }
  }

  showError(message) {
    // Implement error display
    console.error(message);
  }

  showModal(title, content) {
    // Implement modal display
    console.log(`Modal: ${title}`, content);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('api_token')) {
    new PromptManager();
  } else {
    // Redirect to login or show token input
    console.log('No API token found');
  }
});
```

## 🖥️ cURL Examples

### Complete cURL Script

```bash
#!/bin/bash
# AI Prompt Manager API Examples - cURL
# Comprehensive examples using cURL

# Configuration
API_BASE="http://localhost:7861/api"
TOKEN="apm_your_token_here"
AUTH_HEADER="Authorization: Bearer $TOKEN"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for formatted output
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test API connectivity
print_section "API Health Check"
if health_response=$(curl -s "$API_BASE/health"); then
    print_success "API is healthy"
    echo "$health_response" | jq .
else
    print_error "API health check failed"
    exit 1
fi

# Get user information
print_section "User Information"
if user_response=$(curl -s -H "$AUTH_HEADER" "$API_BASE/user/info"); then
    print_success "User info retrieved"
    echo "$user_response" | jq '.data.user | {email, role, tenant_id}'
else
    print_error "Failed to get user info"
    exit 1
fi

# List all prompts
print_section "List All Prompts"
if prompts_response=$(curl -s -H "$AUTH_HEADER" "$API_BASE/prompts?page_size=5"); then
    total=$(echo "$prompts_response" | jq '.total')
    print_success "Found $total total prompts"
    echo "$prompts_response" | jq '.prompts[] | {id, name, title, category}'
else
    print_error "Failed to list prompts"
fi

# Get categories
print_section "Available Categories"
if categories_response=$(curl -s -H "$AUTH_HEADER" "$API_BASE/categories"); then
    print_success "Categories retrieved"
    echo "$categories_response" | jq '.data.categories[]'
else
    print_error "Failed to get categories"
fi

# Filter prompts by category
print_section "Writing Prompts"
if writing_prompts=$(curl -s -H "$AUTH_HEADER" "$API_BASE/prompts?category=Writing&page_size=3"); then
    count=$(echo "$writing_prompts" | jq '.total')
    print_success "Found $count writing prompts"
    echo "$writing_prompts" | jq '.prompts[] | {name, title}'
else
    print_error "Failed to get writing prompts"
fi

# Search prompts
print_section "Search Results for 'blog'"
if search_results=$(curl -s -H "$AUTH_HEADER" "$API_BASE/search?q=blog&page_size=3"); then
    count=$(echo "$search_results" | jq '.total')
    print_success "Found $count prompts matching 'blog'"
    echo "$search_results" | jq '.prompts[] | {name, title, category}'
else
    print_error "Failed to search prompts"
fi

# Get specific prompt
print_section "Specific Prompt Details"
# Get the first prompt ID from the earlier response
first_prompt_id=$(echo "$prompts_response" | jq '.prompts[0].id // 1')
if prompt_details=$(curl -s -H "$AUTH_HEADER" "$API_BASE/prompts/$first_prompt_id"); then
    print_success "Prompt details retrieved"
    echo "$prompt_details" | jq '.data.prompt | {name, title, content, category, tags}'
else
    print_error "Failed to get prompt details"
fi

# Get prompt by name
print_section "Get Prompt by Name"
# Get the first prompt name from the earlier response
first_prompt_name=$(echo "$prompts_response" | jq -r '.prompts[0].name // "unknown"')
if [ "$first_prompt_name" != "unknown" ]; then
    if prompt_by_name=$(curl -s -H "$AUTH_HEADER" "$API_BASE/prompts/name/$first_prompt_name"); then
        print_success "Prompt retrieved by name: $first_prompt_name"
        echo "$prompt_by_name" | jq '.data.prompt.title'
    else
        print_error "Failed to get prompt by name"
    fi
else
    print_info "No prompts available to test get-by-name"
fi

# Pagination example
print_section "Pagination Example"
if page2_response=$(curl -s -H "$AUTH_HEADER" "$API_BASE/prompts?page=2&page_size=3"); then
    page2_count=$(echo "$page2_response" | jq '.prompts | length')
    print_success "Page 2 contains $page2_count prompts"
    echo "$page2_response" | jq '.prompts[] | .name'
else
    print_error "Failed to get page 2"
fi

# Error handling example
print_section "Error Handling Test"
print_info "Testing with invalid prompt ID (should return 404)"
if error_response=$(curl -s -w "%{http_code}" -H "$AUTH_HEADER" "$API_BASE/prompts/99999"); then
    http_code="${error_response: -3}"
    response_body="${error_response%???}"
    if [ "$http_code" = "404" ]; then
        print_success "Error handling works correctly (HTTP $http_code)"
        echo "$response_body" | jq .
    else
        print_error "Unexpected response code: $http_code"
    fi
fi

print_section "API Testing Complete"
print_success "All API endpoints tested successfully!"
```

### Advanced cURL Examples

```bash
#!/bin/bash
# Advanced cURL examples with error handling and performance testing

API_BASE="http://localhost:7861/api"
TOKEN="apm_your_token_here"

# Function to make authenticated requests with error handling
api_request() {
    local method="$1"
    local endpoint="$2"
    local params="$3"
    
    local url="$API_BASE$endpoint"
    if [ -n "$params" ]; then
        url="$url?$params"
    fi
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" \
                   -X "$method" \
                   -H "Authorization: Bearer $TOKEN" \
                   -H "Content-Type: application/json" \
                   "$url")
    
    # Extract HTTP status and response time
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    time_total=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
    body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*;TIME:[0-9.]*$//')
    
    echo "HTTP $http_code (${time_total}s): $body"
    
    # Return status code for error handling
    return "$http_code"
}

# Performance testing
echo "=== Performance Testing ==="

# Test multiple concurrent requests
echo "Testing concurrent requests..."
for i in {1..5}; do
    (api_request "GET" "/prompts" "page_size=10" | head -1) &
done
wait

# Test pagination performance
echo "Testing pagination performance..."
for page in {1..3}; do
    echo "Page $page:"
    api_request "GET" "/prompts" "page=$page&page_size=5" | head -1
done

# Test search performance
echo "Testing search performance..."
for query in "blog" "code" "analysis"; do
    echo "Searching for '$query':"
    api_request "GET" "/search" "q=$query&page_size=5" | head -1
done

# Comprehensive error testing
echo "=== Error Testing ==="

# Test invalid token
echo "Testing invalid token:"
curl -s -w "HTTP %{http_code}\n" \
     -H "Authorization: Bearer invalid_token" \
     "$API_BASE/user/info" -o /dev/null

# Test missing token
echo "Testing missing token:"
curl -s -w "HTTP %{http_code}\n" \
     "$API_BASE/user/info" -o /dev/null

# Test invalid endpoint
echo "Testing invalid endpoint:"
curl -s -w "HTTP %{http_code}\n" \
     -H "Authorization: Bearer $TOKEN" \
     "$API_BASE/invalid_endpoint" -o /dev/null

# Test parameter validation
echo "Testing parameter validation:"
curl -s -w "HTTP %{http_code}\n" \
     -H "Authorization: Bearer $TOKEN" \
     "$API_BASE/prompts?page=0" -o /dev/null

# Test rate limiting (if implemented)
echo "Testing rate limiting:"
for i in {1..10}; do
    response=$(curl -s -w "%{http_code}" \
                   -H "Authorization: Bearer $TOKEN" \
                   "$API_BASE/health" -o /dev/null)
    echo "Request $i: HTTP $response"
    if [ "$response" = "429" ]; then
        echo "Rate limit reached at request $i"
        break
    fi
done
```

## 🐘 PHP Examples

### PHP Client Class

```php
<?php
/**
 * AI Prompt Manager API Client - PHP
 * Complete PHP client for API integration
 */

class PromptManagerClient {
    private $baseUrl;
    private $apiToken;
    private $headers;

    public function __construct($baseUrl, $apiToken) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiToken = $apiToken;
        $this->headers = [
            'Authorization: Bearer ' . $apiToken,
            'Content-Type: application/json'
        ];
    }

    private function makeRequest($method, $endpoint, $params = null) {
        $url = $this->baseUrl . $endpoint;
        
        if ($params && $method === 'GET') {
            $url .= '?' . http_build_query($params);
        }

        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $this->headers,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_FOLLOWLOCATION => true
        ]);

        if ($method === 'POST' && $params) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($params));
        }

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            throw new Exception("cURL Error: " . $error);
        }

        $data = json_decode($response, true);
        
        if ($httpCode >= 400) {
            $errorMsg = isset($data['detail']) ? $data['detail'] : 'HTTP Error ' . $httpCode;
            throw new Exception($errorMsg, $httpCode);
        }

        return $data;
    }

    public function healthCheck() {
        // Health endpoint doesn't require authentication
        $tempHeaders = $this->headers;
        $this->headers = [];
        
        try {
            $result = $this->makeRequest('GET', '/health');
            $this->headers = $tempHeaders;
            return $result;
        } catch (Exception $e) {
            $this->headers = $tempHeaders;
            throw $e;
        }
    }

    public function getUserInfo() {
        return $this->makeRequest('GET', '/user/info');
    }

    public function listPrompts($category = null, $search = null, $page = 1, $pageSize = 50) {
        $params = [
            'page' => $page,
            'page_size' => $pageSize
        ];
        
        if ($category) $params['category'] = $category;
        if ($search) $params['search'] = $search;

        return $this->makeRequest('GET', '/prompts', $params);
    }

    public function getPrompt($promptId) {
        return $this->makeRequest('GET', '/prompts/' . $promptId);
    }

    public function getPromptByName($promptName) {
        return $this->makeRequest('GET', '/prompts/name/' . urlencode($promptName));
    }

    public function searchPrompts($query, $page = 1, $pageSize = 50) {
        $params = [
            'q' => $query,
            'page' => $page,
            'page_size' => $pageSize
        ];
        
        return $this->makeRequest('GET', '/search', $params);
    }

    public function getCategories() {
        $response = $this->makeRequest('GET', '/categories');
        return $response['data']['categories'];
    }

    public function getPromptsByCategory($category, $page = 1, $pageSize = 50) {
        $params = [
            'page' => $page,
            'page_size' => $pageSize
        ];
        
        return $this->makeRequest('GET', '/prompts/category/' . urlencode($category), $params);
    }
}

// Usage example
try {
    $client = new PromptManagerClient(
        'http://localhost:7861/api',
        'apm_your_token_here'
    );

    // Check API health
    $health = $client->healthCheck();
    echo "API Status: " . $health['status'] . "\n";

    // Get user info
    $userInfo = $client->getUserInfo();
    echo "User: " . $userInfo['data']['user']['email'] . "\n";

    // List prompts
    $prompts = $client->listPrompts(null, null, 1, 10);
    echo "Total prompts: " . $prompts['total'] . "\n";

    // Search prompts
    $searchResults = $client->searchPrompts('blog');
    echo "Blog prompts found: " . $searchResults['total'] . "\n";

    // Get categories
    $categories = $client->getCategories();
    echo "Categories: " . implode(', ', $categories) . "\n";

    // Get writing prompts
    $writingPrompts = $client->getPromptsByCategory('Writing');
    echo "Writing prompts: " . $writingPrompts['total'] . "\n";

    // Get specific prompt
    if ($prompts['total'] > 0) {
        $firstPrompt = $prompts['prompts'][0];
        $detailedPrompt = $client->getPrompt($firstPrompt['id']);
        echo "First prompt: " . $detailedPrompt['data']['prompt']['title'] . "\n";
    }

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

## 🔷 Go Examples

### Go Client Implementation

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strconv"
    "time"
)

// PromptManagerClient represents the API client
type PromptManagerClient struct {
    BaseURL    string
    APIToken   string
    HTTPClient *http.Client
}

// NewPromptManagerClient creates a new API client
func NewPromptManagerClient(baseURL, apiToken string) *PromptManagerClient {
    return &PromptManagerClient{
        BaseURL:  baseURL,
        APIToken: apiToken,
        HTTPClient: &http.Client{
            Timeout: 30 * time.Second,
        },
    }
}

// APIResponse represents a standard API response
type APIResponse struct {
    Success bool                   `json:"success"`
    Message string                 `json:"message"`
    Data    map[string]interface{} `json:"data"`
}

// Prompt represents a prompt object
type Prompt struct {
    ID                   int    `json:"id"`
    Name                 string `json:"name"`
    Title                string `json:"title"`
    Content              string `json:"content"`
    Category             string `json:"category"`
    Tags                 string `json:"tags"`
    IsEnhancementPrompt  bool   `json:"is_enhancement_prompt"`
    UserID               string `json:"user_id"`
    CreatedAt            string `json:"created_at"`
    UpdatedAt            string `json:"updated_at"`
}

// PromptListResponse represents a paginated list of prompts
type PromptListResponse struct {
    Prompts  []Prompt `json:"prompts"`
    Total    int      `json:"total"`
    Page     int      `json:"page"`
    PageSize int      `json:"page_size"`
}

// makeRequest performs an HTTP request
func (c *PromptManagerClient) makeRequest(method, endpoint string, params map[string]string) ([]byte, error) {
    requestURL := c.BaseURL + endpoint
    
    // Add query parameters for GET requests
    if method == "GET" && params != nil {
        u, _ := url.Parse(requestURL)
        q := u.Query()
        for k, v := range params {
            q.Set(k, v)
        }
        u.RawQuery = q.Encode()
        requestURL = u.String()
    }

    req, err := http.NewRequest(method, requestURL, nil)
    if err != nil {
        return nil, err
    }

    // Add authentication header
    req.Header.Set("Authorization", "Bearer "+c.APIToken)
    req.Header.Set("Content-Type", "application/json")

    resp, err := c.HTTPClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    if resp.StatusCode >= 400 {
        return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(body))
    }

    return body, nil
}

// HealthCheck checks if the API is healthy
func (c *PromptManagerClient) HealthCheck() (map[string]interface{}, error) {
    // Health endpoint doesn't require authentication
    req, err := http.NewRequest("GET", c.BaseURL+"/health", nil)
    if err != nil {
        return nil, err
    }

    resp, err := c.HTTPClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var result map[string]interface{}
    err = json.Unmarshal(body, &result)
    return result, err
}

// GetUserInfo retrieves current user information
func (c *PromptManagerClient) GetUserInfo() (*APIResponse, error) {
    body, err := c.makeRequest("GET", "/user/info", nil)
    if err != nil {
        return nil, err
    }

    var response APIResponse
    err = json.Unmarshal(body, &response)
    return &response, err
}

// ListPrompts retrieves a list of prompts with optional filtering
func (c *PromptManagerClient) ListPrompts(category, search string, page, pageSize int) (*PromptListResponse, error) {
    params := map[string]string{
        "page":      strconv.Itoa(page),
        "page_size": strconv.Itoa(pageSize),
    }
    
    if category != "" {
        params["category"] = category
    }
    if search != "" {
        params["search"] = search
    }

    body, err := c.makeRequest("GET", "/prompts", params)
    if err != nil {
        return nil, err
    }

    var response PromptListResponse
    err = json.Unmarshal(body, &response)
    return &response, err
}

// GetPrompt retrieves a specific prompt by ID
func (c *PromptManagerClient) GetPrompt(promptID int) (*APIResponse, error) {
    endpoint := fmt.Sprintf("/prompts/%d", promptID)
    body, err := c.makeRequest("GET", endpoint, nil)
    if err != nil {
        return nil, err
    }

    var response APIResponse
    err = json.Unmarshal(body, &response)
    return &response, err
}

// SearchPrompts searches for prompts
func (c *PromptManagerClient) SearchPrompts(query string, page, pageSize int) (*PromptListResponse, error) {
    params := map[string]string{
        "q":         query,
        "page":      strconv.Itoa(page),
        "page_size": strconv.Itoa(pageSize),
    }

    body, err := c.makeRequest("GET", "/search", params)
    if err != nil {
        return nil, err
    }

    var response PromptListResponse
    err = json.Unmarshal(body, &response)
    return &response, err
}

// GetCategories retrieves all available categories
func (c *PromptManagerClient) GetCategories() ([]string, error) {
    body, err := c.makeRequest("GET", "/categories", nil)
    if err != nil {
        return nil, err
    }

    var response APIResponse
    err = json.Unmarshal(body, &response)
    if err != nil {
        return nil, err
    }

    // Extract categories from response
    if categoriesData, ok := response.Data["categories"].([]interface{}); ok {
        categories := make([]string, len(categoriesData))
        for i, cat := range categoriesData {
            categories[i] = cat.(string)
        }
        return categories, nil
    }

    return nil, fmt.Errorf("failed to parse categories")
}

// Example usage
func main() {
    client := NewPromptManagerClient(
        "http://localhost:7861/api",
        "apm_your_token_here",
    )

    // Check health
    health, err := client.HealthCheck()
    if err != nil {
        fmt.Printf("Health check failed: %v\n", err)
        return
    }
    fmt.Printf("API Status: %v\n", health["status"])

    // Get user info
    userInfo, err := client.GetUserInfo()
    if err != nil {
        fmt.Printf("Failed to get user info: %v\n", err)
        return
    }
    
    if user, ok := userInfo.Data["user"].(map[string]interface{}); ok {
        fmt.Printf("User: %v\n", user["email"])
    }

    // List prompts
    prompts, err := client.ListPrompts("", "", 1, 10)
    if err != nil {
        fmt.Printf("Failed to list prompts: %v\n", err)
        return
    }
    fmt.Printf("Total prompts: %d\n", prompts.Total)

    // Search prompts
    searchResults, err := client.SearchPrompts("blog", 1, 10)
    if err != nil {
        fmt.Printf("Failed to search prompts: %v\n", err)
        return
    }
    fmt.Printf("Blog prompts found: %d\n", searchResults.Total)

    // Get categories
    categories, err := client.GetCategories()
    if err != nil {
        fmt.Printf("Failed to get categories: %v\n", err)
        return
    }
    fmt.Printf("Categories: %v\n", categories)

    // Get specific prompt
    if len(prompts.Prompts) > 0 {
        firstPrompt := prompts.Prompts[0]
        promptDetails, err := client.GetPrompt(firstPrompt.ID)
        if err != nil {
            fmt.Printf("Failed to get prompt details: %v\n", err)
            return
        }
        
        if prompt, ok := promptDetails.Data["prompt"].(map[string]interface{}); ok {
            fmt.Printf("Prompt: %v\n", prompt["title"])
        }
    }
}
```

## 🔄 Integration Patterns

### Webhook Integration Pattern

```python
#!/usr/bin/env python3
"""
Webhook Integration Example
Demonstrates how to integrate the API with webhook systems
"""

from flask import Flask, request, jsonify
import requests
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class WebhookHandler:
    api_base_url: str
    api_token: str
    
    def __post_init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def process_prompt_request(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook for prompt requests"""
        try:
            # Extract prompt name or search query from webhook
            prompt_name = webhook_data.get('prompt_name')
            search_query = webhook_data.get('search_query')
            
            if prompt_name:
                # Get specific prompt by name
                response = requests.get(
                    f"{self.api_base_url}/prompts/name/{prompt_name}",
                    headers=self.headers
                )
                response.raise_for_status()
                prompt_data = response.json()
                
                return {
                    "success": True,
                    "prompt": prompt_data['data']['prompt'],
                    "message": f"Retrieved prompt: {prompt_name}"
                }
                
            elif search_query:
                # Search for prompts
                response = requests.get(
                    f"{self.api_base_url}/search",
                    headers=self.headers,
                    params={"q": search_query, "page_size": 5}
                )
                response.raise_for_status()
                search_results = response.json()
                
                return {
                    "success": True,
                    "prompts": search_results['prompts'],
                    "total": search_results['total'],
                    "message": f"Found {search_results['total']} prompts for '{search_query}'"
                }
            
            else:
                return {
                    "success": False,
                    "message": "No prompt_name or search_query provided"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"API request failed: {str(e)}"
            }

# Flask webhook endpoint
app = Flask(__name__)
webhook_handler = WebhookHandler(
    api_base_url="http://localhost:7861/api",
    api_token="apm_your_token_here"
)

@app.route('/webhook/prompt-request', methods=['POST'])
def handle_prompt_request():
    """Handle incoming webhook for prompt requests"""
    try:
        webhook_data = request.get_json()
        result = webhook_handler.process_prompt_request(webhook_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Webhook processing failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Background Job Integration

```python
#!/usr/bin/env python3
"""
Background Job Integration Example
Using Celery for async prompt processing
"""

from celery import Celery
import requests
from typing import Dict, List
import logging

# Configure Celery
app = Celery('prompt_processor', broker='redis://localhost:6379/0')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def process_prompt_batch(prompt_ids: List[int], api_token: str) -> Dict:
    """Process a batch of prompts asynchronously"""
    api_base = "http://localhost:7861/api"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    results = []
    errors = []
    
    for prompt_id in prompt_ids:
        try:
            # Get prompt details
            response = requests.get(
                f"{api_base}/prompts/{prompt_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            prompt_data = response.json()['data']['prompt']
            
            # Process prompt (example: word count analysis)
            word_count = len(prompt_data['content'].split())
            
            results.append({
                "prompt_id": prompt_id,
                "name": prompt_data['name'],
                "word_count": word_count,
                "category": prompt_data['category'],
                "processed_at": "2025-01-08T10:30:00Z"
            })
            
            logger.info(f"Processed prompt {prompt_id}: {word_count} words")
            
        except Exception as e:
            error_msg = f"Failed to process prompt {prompt_id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    return {
        "success": len(errors) == 0,
        "processed": len(results),
        "errors": len(errors),
        "results": results,
        "error_messages": errors
    }

@app.task
def sync_prompts_to_external_system(category: str, api_token: str) -> Dict:
    """Sync prompts to an external system"""
    api_base = "http://localhost:7861/api"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    try:
        # Get prompts by category
        response = requests.get(
            f"{api_base}/prompts/category/{category}",
            headers=headers,
            params={"page_size": 100}
        )
        response.raise_for_status()
        
        prompts_data = response.json()
        prompts = prompts_data['prompts']
        
        # Simulate external system sync
        synced_count = 0
        for prompt in prompts:
            # Here you would sync to your external system
            # For example: upload to S3, send to CRM, etc.
            logger.info(f"Syncing prompt: {prompt['name']}")
            synced_count += 1
        
        return {
            "success": True,
            "category": category,
            "total_prompts": prompts_data['total'],
            "synced_count": synced_count,
            "message": f"Successfully synced {synced_count} {category} prompts"
        }
        
    except Exception as e:
        error_msg = f"Sync failed for category {category}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg
        }

# Usage example
if __name__ == '__main__':
    # Start Celery worker with:
    # celery -A background_jobs worker --loglevel=info
    
    # Schedule tasks
    result = process_prompt_batch.delay([1, 2, 3, 4, 5], "apm_your_token_here")
    print(f"Task scheduled: {result.id}")
    
    sync_result = sync_prompts_to_external_system.delay("Writing", "amp_your_token_here")
    print(f"Sync task scheduled: {sync_result.id}")
```

### Real-time Dashboard Integration

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Prompt Manager Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        .metrics { display: flex; justify-content: space-between; }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .loading { color: #666; font-style: italic; }
        .error { color: #dc3545; }
        #prompt-list { max-height: 300px; overflow-y: auto; }
        .prompt-item { padding: 10px; border-bottom: 1px solid #eee; }
        .prompt-item:hover { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <h1>AI Prompt Manager Dashboard</h1>
    
    <div class="dashboard">
        <!-- Metrics Card -->
        <div class="card">
            <h3>Key Metrics</h3>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="total-prompts">-</div>
                    <div>Total Prompts</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="categories-count">-</div>
                    <div>Categories</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="user-role">-</div>
                    <div>User Role</div>
                </div>
            </div>
        </div>

        <!-- Category Distribution Chart -->
        <div class="card">
            <h3>Category Distribution</h3>
            <canvas id="category-chart"></canvas>
        </div>

        <!-- Recent Prompts -->
        <div class="card">
            <h3>Recent Prompts</h3>
            <div id="prompt-list" class="loading">Loading prompts...</div>
        </div>

        <!-- Search Results -->
        <div class="card">
            <h3>Search</h3>
            <input type="text" id="search-input" placeholder="Search prompts..." 
                   style="width: 100%; padding: 8px; margin-bottom: 10px;">
            <div id="search-results"></div>
        </div>
    </div>

    <script>
        class PromptDashboard {
            constructor(apiBaseUrl, apiToken) {
                this.apiBaseUrl = apiBaseUrl;
                this.headers = {
                    'Authorization': `Bearer ${apiToken}`,
                    'Content-Type': 'application/json'
                };
                this.categoryChart = null;
                this.init();
            }

            async makeRequest(endpoint, params = {}) {
                const url = new URL(endpoint, this.apiBaseUrl);
                Object.keys(params).forEach(key => 
                    url.searchParams.append(key, params[key])
                );

                const response = await fetch(url, { headers: this.headers });
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            }

            async init() {
                try {
                    await this.loadUserInfo();
                    await this.loadMetrics();
                    await this.loadRecentPrompts();
                    await this.setupSearch();
                    this.startAutoRefresh();
                } catch (error) {
                    console.error('Dashboard initialization failed:', error);
                    this.showError('Failed to initialize dashboard');
                }
            }

            async loadUserInfo() {
                const userInfo = await this.makeRequest('/user/info');
                document.getElementById('user-role').textContent = 
                    userInfo.data.user.role.toUpperCase();
            }

            async loadMetrics() {
                const [prompts, categories] = await Promise.all([
                    this.makeRequest('/prompts', { page_size: 1 }),
                    this.makeRequest('/categories')
                ]);

                document.getElementById('total-prompts').textContent = prompts.total;
                document.getElementById('categories-count').textContent = 
                    categories.data.categories.length;

                await this.loadCategoryChart(categories.data.categories);
            }

            async loadCategoryChart(categories) {
                // Get prompt count for each category
                const categoryData = await Promise.all(
                    categories.map(async category => {
                        const prompts = await this.makeRequest(`/prompts/category/${category}`, 
                                                             { page_size: 1 });
                        return { category, count: prompts.total };
                    })
                );

                const ctx = document.getElementById('category-chart').getContext('2d');
                
                if (this.categoryChart) {
                    this.categoryChart.destroy();
                }

                this.categoryChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: categoryData.map(d => d.category),
                        datasets: [{
                            data: categoryData.map(d => d.count),
                            backgroundColor: [
                                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }

            async loadRecentPrompts() {
                try {
                    const prompts = await this.makeRequest('/prompts', { page_size: 10 });
                    const promptList = document.getElementById('prompt-list');
                    
                    if (prompts.prompts.length === 0) {
                        promptList.innerHTML = '<div class="loading">No prompts found</div>';
                        return;
                    }

                    promptList.innerHTML = prompts.prompts.map(prompt => `
                        <div class="prompt-item">
                            <strong>${prompt.title}</strong><br>
                            <small>${prompt.category} • ${prompt.name}</small><br>
                            <small>${prompt.content.substring(0, 100)}${prompt.content.length > 100 ? '...' : ''}</small>
                        </div>
                    `).join('');
                } catch (error) {
                    document.getElementById('prompt-list').innerHTML = 
                        '<div class="error">Failed to load prompts</div>';
                }
            }

            async setupSearch() {
                const searchInput = document.getElementById('search-input');
                const searchResults = document.getElementById('search-results');
                
                let searchTimeout;
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(async () => {
                        const query = e.target.value.trim();
                        if (query.length < 2) {
                            searchResults.innerHTML = '';
                            return;
                        }

                        try {
                            searchResults.innerHTML = '<div class="loading">Searching...</div>';
                            const results = await this.makeRequest('/search', { 
                                q: query, 
                                page_size: 5 
                            });

                            if (results.total === 0) {
                                searchResults.innerHTML = '<div>No results found</div>';
                                return;
                            }

                            searchResults.innerHTML = results.prompts.map(prompt => `
                                <div class="prompt-item">
                                    <strong>${prompt.title}</strong><br>
                                    <small>${prompt.category} • ${prompt.name}</small>
                                </div>
                            `).join('');
                        } catch (error) {
                            searchResults.innerHTML = '<div class="error">Search failed</div>';
                        }
                    }, 300);
                });
            }

            startAutoRefresh() {
                // Refresh metrics every 30 seconds
                setInterval(() => {
                    this.loadMetrics();
                }, 30000);

                // Refresh recent prompts every 60 seconds
                setInterval(() => {
                    this.loadRecentPrompts();
                }, 60000);
            }

            showError(message) {
                document.body.innerHTML = `
                    <div class="error" style="text-align: center; padding: 50px;">
                        <h2>Dashboard Error</h2>
                        <p>${message}</p>
                        <button onclick="location.reload()">Retry</button>
                    </div>
                `;
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', () => {
            // Get API token from localStorage or prompt user
            const apiToken = localStorage.getItem('api_token') || 
                             prompt('Please enter your API token:');
            
            if (!apiToken) {
                alert('API token is required');
                return;
            }

            localStorage.setItem('api_token', apiToken);
            
            new PromptDashboard('http://localhost:7861/api', apiToken);
        });
    </script>
</body>
</html>
```

This comprehensive API documentation and examples should provide everything developers need to integrate with the AI Prompt Manager API across different programming languages and use cases.

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**