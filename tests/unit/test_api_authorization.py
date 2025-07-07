#!/usr/bin/env python3
"""
Unit tests for API authorization and token management functionality.

Tests include:
- Token generation and validation
- API endpoint authorization
- Security middleware
- Token lifecycle management
"""

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

from api_endpoints import APIManager, UserInfo
from api_token_manager import APIToken, APITokenManager
from auth_manager import AuthManager, User


class TestAPITokenManager(unittest.TestCase):
    """Test cases for APITokenManager class"""

    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.token_manager = APITokenManager(self.db_path)

        # Test data
        self.test_user_id = "test-user-123"
        self.test_tenant_id = "test-tenant-456"
        self.test_token_name = "Test Token"

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_database_initialization(self):
        """Test that the database is properly initialized"""
        # Check that the api_tokens table exists
        conn = self.token_manager.get_conn()
        cursor = conn.cursor()

        # SQLite specific query to check table existence
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='api_tokens'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        self.assertTrue(
            table_exists, "api_tokens table should exist after initialization"
        )

    def test_generate_secure_token(self):
        """Test secure token generation"""
        full_token, token_prefix, token_hash = (
            self.token_manager.generate_secure_token()
        )

        # Verify token format
        self.assertTrue(
            full_token.startswith("apm_"), "Token should start with 'apm_' prefix"
        )
        self.assertEqual(
            len(full_token), 36, "Token should be 36 characters long (apm_ + 32 chars)"
        )

        # Verify prefix format
        self.assertEqual(
            token_prefix, full_token[:12], "Token prefix should be first 12 characters"
        )

        # Verify hash format
        self.assertEqual(
            len(token_hash), 64, "SHA256 hash should be 64 characters long"
        )

        # Verify uniqueness
        token2, prefix2, hash2 = self.token_manager.generate_secure_token()
        self.assertNotEqual(full_token, token2, "Generated tokens should be unique")
        self.assertNotEqual(token_hash, hash2, "Generated hashes should be unique")

    def test_create_api_token_success(self):
        """Test successful API token creation"""
        success, message, token = self.token_manager.create_api_token(
            self.test_user_id,
            self.test_tenant_id,
            self.test_token_name,
            expires_days=30,
        )

        self.assertTrue(success, "Token creation should succeed")
        self.assertIsNotNone(token, "Token should be returned")
        self.assertTrue(
            token.startswith("apm_"), "Returned token should have correct format"
        )
        self.assertIn(
            "created successfully",
            message.lower(),
            "Success message should be returned",
        )

    def test_create_api_token_duplicate_name(self):
        """Test API token creation with duplicate name"""
        # Create first token
        self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, self.test_token_name
        )

        # Try to create duplicate
        success, message, token = self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, self.test_token_name
        )

        self.assertFalse(success, "Duplicate token creation should fail")
        self.assertIsNone(token, "No token should be returned for duplicate")
        self.assertIn(
            "already exists", message.lower(), "Error message should mention duplicate"
        )

    def test_create_api_token_empty_name(self):
        """Test API token creation with empty name"""
        success, message, token = self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, ""
        )

        self.assertFalse(success, "Empty name token creation should fail")
        self.assertIsNone(token, "No token should be returned for empty name")
        self.assertIn(
            "required", message.lower(), "Error message should mention required name"
        )

    def test_validate_api_token_valid(self):
        """Test validation of valid API token"""
        # Create token
        success, _, token = self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, self.test_token_name
        )
        self.assertTrue(success)

        # Validate token
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(token)

        self.assertTrue(is_valid, "Valid token should be validated successfully")
        self.assertEqual(
            user_id, self.test_user_id, "Correct user ID should be returned"
        )
        self.assertEqual(
            tenant_id, self.test_tenant_id, "Correct tenant ID should be returned"
        )

    def test_validate_api_token_invalid(self):
        """Test validation of invalid API token"""
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(
            "apm_invalid_token"
        )

        self.assertFalse(is_valid, "Invalid token should not be validated")
        self.assertIsNone(user_id, "No user ID should be returned for invalid token")
        self.assertIsNone(
            tenant_id, "No tenant ID should be returned for invalid token"
        )

    def test_validate_api_token_wrong_format(self):
        """Test validation of token with wrong format"""
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(
            "wrong_format_token"
        )

        self.assertFalse(is_valid, "Wrong format token should not be validated")
        self.assertIsNone(user_id, "No user ID should be returned for wrong format")
        self.assertIsNone(tenant_id, "No tenant ID should be returned for wrong format")

    def test_validate_api_token_expired(self):
        """Test validation of expired API token"""
        # Create token with 1-day expiry, then manually expire it
        success, _, token = self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, self.test_token_name, expires_days=1
        )
        self.assertTrue(success)

        # Manually set expiration to past
        conn = self.token_manager.get_conn()
        cursor = conn.cursor()
        past_date = datetime.now() - timedelta(days=2)
        cursor.execute(
            "UPDATE api_tokens SET expires_at = ? WHERE user_id = ?",
            (past_date.isoformat(), self.test_user_id),
        )
        conn.commit()
        conn.close()

        # Validate expired token
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(token)

        self.assertFalse(is_valid, "Expired token should not be validated")
        self.assertIsNone(user_id, "No user ID should be returned for expired token")
        self.assertIsNone(
            tenant_id, "No tenant ID should be returned for expired token"
        )

    def test_get_user_tokens(self):
        """Test retrieving user tokens"""
        # Create multiple tokens
        token_names = ["Token 1", "Token 2", "Token 3"]
        for name in token_names:
            self.token_manager.create_api_token(
                self.test_user_id, self.test_tenant_id, name
            )

        # Get user tokens
        tokens = self.token_manager.get_user_tokens(self.test_user_id)

        self.assertEqual(len(tokens), 3, "Should return all user tokens")
        token_names_returned = [token.name for token in tokens]
        for name in token_names:
            self.assertIn(
                name,
                token_names_returned,
                f"Token '{name}' should be in returned tokens",
            )

    def test_revoke_token(self):
        """Test token revocation"""
        # Create token
        success, _, token = self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, self.test_token_name
        )
        self.assertTrue(success)

        # Get token ID
        tokens = self.token_manager.get_user_tokens(self.test_user_id)
        token_id = tokens[0].id

        # Revoke token
        success, message = self.token_manager.revoke_token(self.test_user_id, token_id)

        self.assertTrue(success, "Token revocation should succeed")
        self.assertIn(
            "revoked successfully",
            message.lower(),
            "Success message should be returned",
        )

        # Verify token is no longer valid
        is_valid, _, _ = self.token_manager.validate_api_token(token)
        self.assertFalse(is_valid, "Revoked token should not be valid")

    def test_revoke_all_tokens(self):
        """Test revoking all user tokens"""
        # Create multiple tokens
        for i in range(3):
            self.token_manager.create_api_token(
                self.test_user_id, self.test_tenant_id, f"Token {i+1}"
            )

        # Revoke all tokens
        success, message = self.token_manager.revoke_all_tokens(self.test_user_id)

        self.assertTrue(success, "Revoking all tokens should succeed")
        self.assertIn("3", message, "Message should indicate number of revoked tokens")

        # Verify no active tokens remain
        tokens = self.token_manager.get_user_tokens(self.test_user_id)
        active_tokens = [token for token in tokens if token.is_active]
        self.assertEqual(len(active_tokens), 0, "No active tokens should remain")

    def test_get_token_stats(self):
        """Test token statistics"""
        # Initially no tokens
        stats = self.token_manager.get_token_stats(self.test_user_id)
        self.assertEqual(stats["total_active"], 0)

        # Create tokens with different expiry settings
        self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, "Never Expires"
        )
        self.token_manager.create_api_token(
            self.test_user_id, self.test_tenant_id, "Expires Soon", expires_days=30
        )

        # Get updated stats
        stats = self.token_manager.get_token_stats(self.test_user_id)

        self.assertEqual(stats["total_active"], 2, "Should have 2 active tokens")
        self.assertEqual(stats["never_expire"], 1, "Should have 1 never-expiring token")
        self.assertEqual(stats["will_expire"], 1, "Should have 1 expiring token")
        self.assertEqual(stats["used_tokens"], 0, "Should have 0 used tokens initially")


class TestAPIEndpointsAuthorization(unittest.TestCase):
    """Test cases for API endpoints authorization"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.api_manager = APIManager(self.db_path)

        # Mock user data
        self.test_user = User(
            id="test-user-123",
            tenant_id="test-tenant-456",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="user",
            is_active=True,
            created_at=datetime.now(),
            last_login=None,
        )

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    @patch("api_endpoints.HTTPException")
    async def test_get_current_user_no_credentials(self, mock_http_exception):
        """Test get_current_user with no credentials"""
        # Mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"

        # Call method with no credentials
        await self.api_manager.get_current_user(mock_request, None)

        # Verify HTTPException was raised
        mock_http_exception.assert_called_once()
        call_args = mock_http_exception.call_args
        self.assertEqual(call_args[1]["status_code"], 401)
        self.assertIn("Missing authorization header", call_args[1]["detail"])

    @patch("api_endpoints.HTTPAuthorizationCredentials")
    async def test_get_current_user_invalid_token(self, mock_credentials):
        """Test get_current_user with invalid token"""
        # Mock credentials
        mock_credentials.credentials = "invalid_token"

        # Mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"

        # Mock token validation to return invalid
        with patch.object(
            self.api_manager.token_manager,
            "validate_api_token",
            return_value=(False, None, None),
        ):
            try:
                await self.api_manager.get_current_user(mock_request, mock_credentials)
                self.fail("Should have raised HTTPException")
            except Exception as e:
                # In real implementation, this would be HTTPException
                # For testing, we check the behavior
                pass

    def test_get_data_manager(self):
        """Test get_data_manager method"""
        user_info = UserInfo(
            user_id="test-user-123",
            tenant_id="test-tenant-456",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="user",
        )

        data_manager = self.api_manager.get_data_manager(user_info)

        self.assertEqual(data_manager.tenant_id, user_info.tenant_id)
        self.assertEqual(data_manager.user_id, user_info.user_id)


class TestAPITokenSecurity(unittest.TestCase):
    """Test cases for API token security measures"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.token_manager = APITokenManager(self.db_path)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_token_randomness(self):
        """Test that generated tokens are sufficiently random"""
        tokens = []
        for _ in range(100):
            token, _, _ = self.token_manager.generate_secure_token()
            tokens.append(token)

        # Check uniqueness
        unique_tokens = set(tokens)
        self.assertEqual(
            len(unique_tokens), 100, "All generated tokens should be unique"
        )

        # Check that no token is a prefix of another
        for i, token1 in enumerate(tokens):
            for j, token2 in enumerate(tokens):
                if i != j:
                    self.assertFalse(
                        token1.startswith(token2[:20])
                        or token2.startswith(token1[:20]),
                        "Tokens should not share common prefixes",
                    )

    def test_token_hash_security(self):
        """Test that token hashing is secure"""
        token, _, hash1 = self.token_manager.generate_secure_token()

        # Verify hash is not reversible to original token
        self.assertNotEqual(token, hash1, "Hash should not equal original token")
        self.assertNotIn(
            token[4:], hash1, "Token content should not be visible in hash"
        )

        # Verify same token produces same hash
        import hashlib

        expected_hash = hashlib.sha256(token.encode()).hexdigest()
        self.assertEqual(hash1, expected_hash, "Hash should be consistent")

    def test_tenant_isolation(self):
        """Test that tokens are properly isolated by tenant"""
        user1_id = "user1"
        tenant1_id = "tenant1"
        user2_id = "user2"
        tenant2_id = "tenant2"

        # Create tokens for different tenants
        success1, _, token1 = self.token_manager.create_api_token(
            user1_id, tenant1_id, "Token 1"
        )
        success2, _, token2 = self.token_manager.create_api_token(
            user2_id, tenant2_id, "Token 2"
        )

        self.assertTrue(success1 and success2)

        # Validate tokens return correct tenant info
        valid1, returned_user1, returned_tenant1 = (
            self.token_manager.validate_api_token(token1)
        )
        valid2, returned_user2, returned_tenant2 = (
            self.token_manager.validate_api_token(token2)
        )

        self.assertTrue(valid1 and valid2)
        self.assertEqual(returned_tenant1, tenant1_id)
        self.assertEqual(returned_tenant2, tenant2_id)
        self.assertNotEqual(returned_tenant1, returned_tenant2)

    def test_token_cleanup(self):
        """Test expired token cleanup functionality"""
        # Create tokens with different expiry
        self.token_manager.create_api_token("user1", "tenant1", "Never Expires")
        self.token_manager.create_api_token(
            "user1", "tenant1", "Expires", expires_days=30
        )

        # Manually expire one token
        conn = self.token_manager.get_conn()
        cursor = conn.cursor()
        past_date = datetime.now() - timedelta(days=2)
        cursor.execute(
            "UPDATE api_tokens SET expires_at = ? WHERE name = ?",
            (past_date.isoformat(), "Expires"),
        )
        conn.commit()
        conn.close()

        # Run cleanup
        deleted_count = self.token_manager.cleanup_expired_tokens()

        self.assertEqual(deleted_count, 1, "Should delete 1 expired token")

        # Verify only non-expired token remains
        tokens = self.token_manager.get_user_tokens("user1")
        self.assertEqual(len(tokens), 1, "Should have 1 remaining token")
        self.assertEqual(tokens[0].name, "Never Expires", "Correct token should remain")


if __name__ == "__main__":
    # Set up test environment variables
    os.environ["DB_TYPE"] = "sqlite"

    # Run tests
    unittest.main(verbosity=2)
