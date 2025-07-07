#!/usr/bin/env python3
"""
Integration tests for API token management and authorization.

Tests include:
- End-to-end API token workflows
- Multi-tenant token isolation
- API endpoint security
- Token lifecycle management
- Performance and scalability
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from fastapi import HTTPException
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from api_endpoints import APIManager, get_api_app
from api_token_manager import APITokenManager
from auth_manager import AuthManager, User
from prompt_data_manager import PromptDataManager


class TestAPITokenIntegration(unittest.TestCase):
    """Integration tests for API token functionality"""

    def setUp(self):
        """Set up test environment with database and API manager"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize managers
        self.token_manager = APITokenManager(self.db_path)
        self.auth_manager = AuthManager(self.db_path)
        self.api_manager = APIManager(self.db_path)

        # Create test tenant and user
        tenant_success, tenant_result = self.auth_manager.create_tenant(
            "Test Tenant", "test-tenant"
        )
        self.assertTrue(
            tenant_success, f"Tenant creation should succeed: {tenant_result}"
        )
        # Extract tenant ID from the result (the method returns the ID string in the success message)
        # We need to get the actual tenant ID from the database
        conn = self.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test-tenant",))
        result = cursor.fetchone()
        self.tenant_id = result[0]
        conn.close()

        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
        }
        success, user_message = self.auth_manager.create_user(
            tenant_id=self.tenant_id, **self.user_data
        )
        self.assertTrue(success, "Test user creation should succeed")
        
        # Get the user_id after creation
        user = self.auth_manager.get_user_by_email(
            self.user_data["email"], self.tenant_id
        )
        self.assertIsNotNone(user, "Created user should be retrievable")
        self.user_id = user.id

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_complete_token_lifecycle(self):
        """Test complete token lifecycle: create, use, update, revoke"""
        # Step 1: Create token
        success, message, token = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Integration Test Token", expires_days=30
        )
        self.assertTrue(success, "Token creation should succeed")
        self.assertIsNotNone(token, "Token should be returned")

        # Step 2: Validate token works
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(token)
        self.assertTrue(is_valid, "New token should be valid")
        self.assertEqual(user_id, self.user_id, "Correct user ID should be returned")
        self.assertEqual(
            tenant_id, self.tenant_id, "Correct tenant ID should be returned"
        )

        # Step 3: Use token (simulate API call)
        # This updates the last_used timestamp
        self.token_manager.validate_api_token(token)

        # Step 4: Verify token appears in user's token list
        tokens = self.token_manager.get_user_tokens(self.user_id)
        self.assertEqual(len(tokens), 1, "Should have one token")
        created_token = tokens[0]
        self.assertEqual(created_token.name, "Integration Test Token")
        self.assertTrue(created_token.is_active, "Token should be active")
        self.assertIsNotNone(
            created_token.last_used, "Token should show last used time"
        )

        # Step 5: Revoke token
        success, message = self.token_manager.revoke_token(
            self.user_id, created_token.id
        )
        self.assertTrue(success, "Token revocation should succeed")

        # Step 6: Verify token is no longer valid
        is_valid, _, _ = self.token_manager.validate_api_token(token)
        self.assertFalse(is_valid, "Revoked token should not be valid")

    def test_multi_tenant_isolation(self):
        """Test that tokens are properly isolated between tenants"""
        # Create second tenant and user
        tenant2_success, tenant2_result = self.auth_manager.create_tenant(
            "Test Tenant 2", "test-tenant-2"
        )
        self.assertTrue(
            tenant2_success, f"Second tenant creation should succeed: {tenant2_result}"
        )
        # Extract tenant ID from the result
        conn = self.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test-tenant-2",))
        result = cursor.fetchone()
        tenant2_id = result[0]
        conn.close()

        success, user2_message = self.auth_manager.create_user(
            tenant_id=tenant2_id,
            email="test2@example.com",
            password="password123",
            first_name="Test2",
            last_name="User2",
            role="user",
        )
        self.assertTrue(success)
        
        # Get user2_id after creation
        user2 = self.auth_manager.get_user_by_email("test2@example.com", tenant2_id)
        self.assertIsNotNone(user2)
        user2_id = user2.id

        # Create tokens for both users
        success1, _, token1 = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Tenant 1 Token"
        )
        success2, _, token2 = self.token_manager.create_api_token(
            user2_id, tenant2_id, "Tenant 2 Token"
        )
        self.assertTrue(success1 and success2)

        # Verify token validation returns correct tenant info
        valid1, returned_user1, returned_tenant1 = (
            self.token_manager.validate_api_token(token1)
        )
        valid2, returned_user2, returned_tenant2 = (
            self.token_manager.validate_api_token(token2)
        )

        self.assertTrue(valid1 and valid2)
        self.assertEqual(returned_tenant1, self.tenant_id)
        self.assertEqual(returned_tenant2, tenant2_id)
        self.assertNotEqual(returned_tenant1, returned_tenant2)

        # Verify users only see their own tokens
        user1_tokens = self.token_manager.get_user_tokens(self.user_id)
        user2_tokens = self.token_manager.get_user_tokens(user2_id)

        self.assertEqual(len(user1_tokens), 1)
        self.assertEqual(len(user2_tokens), 1)
        self.assertEqual(user1_tokens[0].name, "Tenant 1 Token")
        self.assertEqual(user2_tokens[0].name, "Tenant 2 Token")

    def test_token_expiration_handling(self):
        """Test token expiration scenarios"""
        # Create token with short expiry
        success, _, token = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Short Lived Token", expires_days=1
        )
        self.assertTrue(success)

        # Verify token is initially valid
        is_valid, _, _ = self.token_manager.validate_api_token(token)
        self.assertTrue(is_valid, "New token should be valid")

        # Manually expire the token by updating database
        conn = self.token_manager.get_conn()
        cursor = conn.cursor()
        past_date = datetime.now() - timedelta(hours=1)
        cursor.execute(
            "UPDATE api_tokens SET expires_at = ? WHERE user_id = ?",
            (past_date.isoformat(), self.user_id),
        )
        conn.commit()
        conn.close()

        # Verify expired token is no longer valid
        is_valid, _, _ = self.token_manager.validate_api_token(token)
        self.assertFalse(is_valid, "Expired token should not be valid")

        # Test cleanup of expired tokens
        deleted_count = self.token_manager.cleanup_expired_tokens()
        self.assertEqual(deleted_count, 1, "Should delete 1 expired token")

    def test_token_statistics_accuracy(self):
        """Test token statistics calculation"""
        # Initially no tokens
        stats = self.token_manager.get_token_stats(self.user_id)
        self.assertEqual(stats["total_active"], 0)

        # Create various types of tokens
        tokens_created = []

        # Never expiring token
        success, _, token1 = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Never Expires"
        )
        tokens_created.append(token1)

        # Expiring token
        success, _, token2 = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Expires Soon", expires_days=30
        )
        tokens_created.append(token2)

        # Another expiring token
        success, _, token3 = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Expires Later", expires_days=365
        )
        tokens_created.append(token3)

        # Use one token
        self.token_manager.validate_api_token(token1)

        # Get updated statistics
        stats = self.token_manager.get_token_stats(self.user_id)

        self.assertEqual(stats["total_active"], 3, "Should have 3 active tokens")
        self.assertEqual(stats["never_expire"], 1, "Should have 1 never-expiring token")
        self.assertEqual(stats["will_expire"], 2, "Should have 2 expiring tokens")
        self.assertEqual(stats["used_tokens"], 1, "Should have 1 used token")

    def test_bulk_token_operations(self):
        """Test performance with multiple tokens"""
        # Create multiple tokens
        token_count = 50
        created_tokens = []

        for i in range(token_count):
            success, _, token = self.token_manager.create_api_token(
                self.user_id,
                self.tenant_id,
                f"Bulk Token {i+1}",
                expires_days=(
                    30 if i % 2 == 0 else None
                ),  # Mix of expiring and non-expiring
            )
            self.assertTrue(success, f"Token {i+1} creation should succeed")
            created_tokens.append(token)

        # Validate all tokens
        for i, token in enumerate(created_tokens):
            is_valid, user_id, tenant_id = self.token_manager.validate_api_token(token)
            self.assertTrue(is_valid, f"Token {i+1} should be valid")
            self.assertEqual(user_id, self.user_id)
            self.assertEqual(tenant_id, self.tenant_id)

        # Get all user tokens
        user_tokens = self.token_manager.get_user_tokens(self.user_id)
        self.assertEqual(
            len(user_tokens), token_count, f"Should return all {token_count} tokens"
        )

        # Test bulk revocation
        success, message = self.token_manager.revoke_all_tokens(self.user_id)
        self.assertTrue(success, "Bulk revocation should succeed")
        self.assertIn(
            str(token_count),
            message,
            "Message should indicate number of revoked tokens",
        )

        # Verify all tokens are revoked
        for token in created_tokens:
            is_valid, _, _ = self.token_manager.validate_api_token(token)
            self.assertFalse(is_valid, "All tokens should be revoked")

    def test_concurrent_token_operations(self):
        """Test thread safety of token operations"""
        import threading
        import time

        results = []
        errors = []

        def create_tokens(thread_id):
            try:
                for i in range(5):
                    success, _, token = self.token_manager.create_api_token(
                        self.user_id, self.tenant_id, f"Thread{thread_id}_Token{i+1}"
                    )
                    if success:
                        results.append(token)
                    time.sleep(0.01)  # Small delay to increase chance of conflicts
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_tokens, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        self.assertEqual(len(errors), 0, f"No errors should occur: {errors}")
        self.assertEqual(len(results), 25, "Should create 25 tokens total")

        # Verify all tokens are unique
        unique_tokens = set(results)
        self.assertEqual(len(unique_tokens), 25, "All tokens should be unique")

    def test_database_constraints(self):
        """Test database constraints and error handling"""
        # Test unique constraint on (user_id, name)
        success1, _, _ = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Duplicate Name"
        )
        success2, message2, _ = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Duplicate Name"
        )

        self.assertTrue(success1, "First token creation should succeed")
        self.assertFalse(success2, "Duplicate name should fail")
        self.assertIn("already exists", message2.lower())

        # Test invalid user/tenant IDs
        success, message, _ = self.token_manager.create_api_token(
            "nonexistent_user", self.tenant_id, "Test Token"
        )
        # This should still succeed at the token level, but would fail at API level
        self.assertTrue(
            success, "Token creation with invalid user should succeed at DB level"
        )


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestAPIEndpointsIntegration(unittest.TestCase):
    """Integration tests for API endpoints with authentication"""

    def setUp(self):
        """Set up test client and test data"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Create FastAPI app
        self.app = get_api_app(self.db_path)
        self.client = TestClient(self.app)

        # Initialize managers
        self.auth_manager = AuthManager(self.db_path)
        self.token_manager = APITokenManager(self.db_path)

        # Create test tenant and user
        tenant_success, tenant_result = self.auth_manager.create_tenant(
            "Test Tenant", "test-tenant"
        )
        self.assertTrue(
            tenant_success, f"Tenant creation should succeed: {tenant_result}"
        )
        # Extract tenant ID from the result
        conn = self.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test-tenant",))
        result = cursor.fetchone()
        self.tenant_id = result[0]
        conn.close()

        success, user_message = self.auth_manager.create_user(
            tenant_id=self.tenant_id,
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="user",
        )
        self.assertTrue(success)
        
        # Get the user_id after creation
        user = self.auth_manager.get_user_by_email("test@example.com", self.tenant_id)
        self.assertIsNotNone(user)
        self.user_id = user.id

        # Create API token for testing
        success, _, self.test_token = self.token_manager.create_api_token(
            self.user_id, self.tenant_id, "Test API Token"
        )
        self.assertTrue(success)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_health_endpoint_no_auth(self):
        """Test health endpoint doesn't require authentication"""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_protected_endpoint_no_token(self):
        """Test protected endpoint without token"""
        response = self.client.get("/api/user/info")
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_invalid_token(self):
        """Test protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/user/info", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_valid_token(self):
        """Test protected endpoint with valid token"""
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = self.client.get("/api/user/info", headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("user", data["data"])
        self.assertEqual(data["data"]["user"]["user_id"], self.user_id)

    def test_token_management_endpoints(self):
        """Test token management through API endpoints"""
        headers = {"Authorization": f"Bearer {self.test_token}"}

        # Test listing tokens
        response = self.client.get("/api/tokens", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("tokens", data["data"])
        self.assertEqual(len(data["data"]["tokens"]), 1)

        # Test creating new token
        new_token_data = {"name": "API Created Token", "expires_days": 30}
        response = self.client.post("/api/tokens", headers=headers, json=new_token_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        new_token = data["token"]

        # Test listing tokens again (should have 2 now)
        response = self.client.get("/api/tokens", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"]["tokens"]), 2)

        # Find the new token's ID
        new_token_id = None
        for token_info in data["data"]["tokens"]:
            if token_info["name"] == "API Created Token":
                new_token_id = token_info["id"]
                break
        self.assertIsNotNone(new_token_id)

        # Test revoking the new token
        response = self.client.delete(f"/api/tokens/{new_token_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Verify the new token is no longer valid
        new_headers = {"Authorization": f"Bearer {new_token}"}
        response = self.client.get("/api/user/info", headers=new_headers)
        self.assertEqual(response.status_code, 401)

    def test_token_stats_endpoint(self):
        """Test token statistics endpoint"""
        headers = {"Authorization": f"Bearer {self.test_token}"}

        response = self.client.get("/api/tokens/stats", headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("stats", data["data"])

        stats = data["data"]["stats"]
        self.assertEqual(stats["total_active"], 1)
        self.assertEqual(stats["never_expire"], 1)  # Our test token never expires

    def test_prompts_api_with_authorization(self):
        """Test prompts API with proper authorization"""
        headers = {"Authorization": f"Bearer {self.test_token}"}

        # Test listing prompts (should work even with empty database)
        response = self.client.get("/api/prompts", headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("prompts", data)
        self.assertIn("total", data)
        self.assertIn("page", data)


class TestPerformanceAndScalability(unittest.TestCase):
    """Performance and scalability tests for API token system"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.token_manager = APITokenManager(self.db_path)
        self.auth_manager = AuthManager(self.db_path)

        # Create test tenant and user
        tenant_success, tenant_result = self.auth_manager.create_tenant(
            "Perf Test Tenant", "perf-test"
        )
        self.assertTrue(
            tenant_success, f"Tenant creation should succeed: {tenant_result}"
        )
        # Extract tenant ID from the result
        conn = self.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("perf-test",))
        result = cursor.fetchone()
        self.tenant_id = result[0]
        conn.close()

        success, user_message = self.auth_manager.create_user(
            tenant_id=self.tenant_id,
            email="perf@example.com",
            password="password123",
            first_name="Perf",
            last_name="User",
            role="user",
        )
        self.assertTrue(success)
        
        # Get the user_id after creation
        user = self.auth_manager.get_user_by_email("perf@example.com", self.tenant_id)
        self.assertIsNotNone(user)
        self.user_id = user.id

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_token_validation_performance(self):
        """Test token validation performance with many tokens"""
        import time

        # Create multiple tokens
        tokens = []
        for i in range(100):
            success, _, token = self.token_manager.create_api_token(
                self.user_id, self.tenant_id, f"Perf Token {i+1}"
            )
            self.assertTrue(success)
            tokens.append(token)

        # Measure validation performance
        start_time = time.time()

        for token in tokens:
            is_valid, _, _ = self.token_manager.validate_api_token(token)
            self.assertTrue(is_valid)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(tokens)

        # Should be able to validate tokens quickly
        self.assertLess(
            avg_time,
            0.01,
            f"Token validation should be fast, got {avg_time:.4f}s per token",
        )

    def test_large_token_list_performance(self):
        """Test performance of retrieving large token lists"""
        import time

        # Create many tokens
        token_count = 1000
        for i in range(token_count):
            success, _, _ = self.token_manager.create_api_token(
                self.user_id, self.tenant_id, f"Large List Token {i+1}"
            )
            self.assertTrue(success)

        # Measure retrieval performance
        start_time = time.time()
        tokens = self.token_manager.get_user_tokens(self.user_id)
        end_time = time.time()

        self.assertEqual(len(tokens), token_count)
        retrieval_time = end_time - start_time

        # Should be able to retrieve large lists quickly
        self.assertLess(
            retrieval_time,
            1.0,
            f"Token list retrieval should be fast, got {retrieval_time:.4f}s",
        )


if __name__ == "__main__":
    # Set up test environment variables
    os.environ["DB_TYPE"] = "sqlite"

    # Run tests
    unittest.main(verbosity=2)
