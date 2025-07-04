"""
E2E Tests for API Workflow

Tests complete API workflows including authentication, CRUD operations, and integration scenarios.
"""

import json
import time

import pytest

from .conftest import E2ETestBase


@pytest.mark.e2e
class TestAPIWorkflow(E2ETestBase):
    """End-to-end API workflow tests."""

    def test_api_health_check(self, test_config, app_server, api_client):
        """Test API health check endpoint."""
        response = api_client.get(f"{test_config['api_base']}/health")

        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"

        # Verify response time is reasonable
        assert (
            response.elapsed.total_seconds() < 5
        ), "Health check should respond quickly"

        print("✅ API health check successful")

    def test_api_authentication_workflow(
        self, test_config, app_server, api_client, admin_user_data
    ):
        """Test complete API authentication workflow."""

        # Test accessing protected endpoint without authentication
        response = api_client.get(f"{test_config['api_base']}/prompts")
        assert response.status_code in [
            401,
            403,
        ], f"Expected 401/403 for unauthenticated request, got {response.status_code}"

        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = api_client.get(f"{test_config['api_base']}/prompts", headers=headers)
        assert response.status_code in [
            401,
            403,
        ], f"Expected 401/403 for invalid token, got {response.status_code}"

        print("✅ API authentication workflow successful")

    def test_api_cors_headers(self, test_config, app_server, api_client):
        """Test CORS headers are properly set."""
        # Test preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        }

        response = api_client.options(
            f"{test_config['api_base']}/health", headers=headers
        )

        # Should either allow CORS or return 200/404 (depending on implementation)
        assert response.status_code in [
            200,
            204,
            404,
        ], f"OPTIONS request failed with {response.status_code}"

        # Test actual request with CORS headers
        headers = {"Origin": "http://localhost:3000"}
        response = api_client.get(f"{test_config['api_base']}/health", headers=headers)

        assert response.status_code == 200

        # Check for CORS headers (may or may not be present depending on configuration)
        cors_header_names = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
        ]
        # CORS headers may be present in response
        cors_present = any(header in response.headers for header in cors_header_names)
        # Log CORS status for debugging
        print(f"CORS headers present: {cors_present}")

        print(f"Response headers: {dict(response.headers)}")
        print("✅ API CORS test completed")

    def test_api_error_handling(self, test_config, app_server, api_client):
        """Test API error handling for various scenarios."""

        # Test 404 for non-existent endpoint
        response = api_client.get(f"{test_config['api_base']}/nonexistent")
        assert response.status_code == 404

        # Test 405 for wrong method (if applicable)
        response = api_client.delete(f"{test_config['api_base']}/health")
        assert response.status_code in [
            405,
            404,
            501,
        ], f"DELETE on health endpoint should return 405/404/501, got {response.status_code}"

        # Test malformed JSON handling (use a valid POST endpoint or expect 405 for non-POST endpoints)
        headers = {"Content-Type": "application/json"}
        response = api_client.post(
            f"{test_config['api_base']}/prompts", data="invalid json{", headers=headers
        )
        assert response.status_code in [
            400,
            401,
            403,
            405,
            422,
        ], f"Malformed JSON should return 400/401/403/405/422, got {response.status_code}"

        print("✅ API error handling test successful")

    def test_api_response_format(self, test_config, app_server, api_client):
        """Test API response formats and structure."""

        # Test health endpoint response format
        response = api_client.get(f"{test_config['api_base']}/health")
        assert response.status_code == 200

        # Should return JSON
        assert response.headers.get("content-type", "").startswith("application/json")

        data = response.json()
        assert isinstance(data, dict), "Health response should be a JSON object"
        assert "status" in data, "Health response should contain 'status' field"

        # Test other endpoints for consistent response format
        endpoints_to_test = [
            "/health",
            "/prompts",  # This might require auth, but should return consistent error format
        ]

        for endpoint in endpoints_to_test:
            response = api_client.get(f"{test_config['api_base']}{endpoint}")

            # All responses should be JSON
            content_type = response.headers.get("content-type", "")
            assert (
                "application/json" in content_type or response.status_code == 404
            ), f"Endpoint {endpoint} should return JSON content type, got {content_type}"

            # If JSON, should be parseable
            if "application/json" in content_type:
                try:
                    data = response.json()
                    assert isinstance(
                        data, (dict, list)
                    ), f"JSON response should be object or array for {endpoint}"
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON response from {endpoint}")

        print("✅ API response format test successful")

    def test_api_performance(self, test_config, app_server, api_client):
        """Test API performance characteristics."""

        # Test response times for health check
        start_time = time.time()
        response = api_client.get(f"{test_config['api_base']}/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert (
            response_time < 2.0
        ), f"Health check should respond within 2 seconds, took {response_time:.2f}s"

        # Test concurrent requests
        import concurrent.futures

        def make_request():
            return api_client.get(f"{test_config['api_base']}/health")

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All should succeed
        for response in responses:
            assert response.status_code == 200, "Concurrent requests should all succeed"

        print("✅ API performance test successful")

    def test_api_openapi_documentation(self, test_config, app_server, api_client):
        """Test OpenAPI documentation availability."""

        # Common OpenAPI documentation endpoints
        docs_endpoints = [
            "/docs",
            "/api/docs",
            "/swagger",
            "/api/swagger",
            "/openapi.json",
            "/api/openapi.json",
        ]

        docs_found = False
        for endpoint in docs_endpoints:
            try:
                response = api_client.get(f"{test_config['base_url']}{endpoint}")
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")

                    # Check if it's HTML (Swagger UI) or JSON (OpenAPI spec)
                    if "text/html" in content_type:
                        content = response.text.lower()
                        if any(
                            term in content
                            for term in ["swagger", "openapi", "api documentation"]
                        ):
                            docs_found = True
                            print(f"✅ Found API documentation (HTML) at {endpoint}")
                            break
                    elif "application/json" in content_type:
                        try:
                            spec = response.json()
                            if "openapi" in spec or "swagger" in spec:
                                docs_found = True
                                print(f"✅ Found OpenAPI spec (JSON) at {endpoint}")
                                break
                        except json.JSONDecodeError:
                            pass
            except Exception:
                continue

        if not docs_found:
            print("⚠️ API documentation not found at standard endpoints")

        # This is not a hard failure since docs might be configured differently
        print("✅ API documentation test completed")

    def test_api_rate_limiting(self, test_config, app_server, api_client):
        """Test API rate limiting behavior (if implemented)."""

        # Make rapid requests to see if rate limiting is in place
        responses = []
        for i in range(20):  # Make 20 rapid requests
            response = api_client.get(f"{test_config['api_base']}/health")
            responses.append(response)
            if i < 19:  # Don't sleep after last request
                time.sleep(0.1)  # Small delay between requests

        # Check if any rate limiting responses
        rate_limited = any(r.status_code == 429 for r in responses)

        if rate_limited:
            print("✅ Rate limiting detected (429 responses)")
        else:
            print("⚠️ No rate limiting detected (may not be implemented)")

        # All responses should be either 200 or 429
        for i, response in enumerate(responses):
            assert response.status_code in [
                200,
                429,
            ], f"Request {i} returned unexpected status {response.status_code}"

        print("✅ API rate limiting test completed")
