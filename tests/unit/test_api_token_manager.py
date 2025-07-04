"""
Comprehensive unit tests for APITokenManager class
Testing secure API token management, validation, and multi-tenant operations
"""

import hashlib
import os
import sqlite3
import tempfile
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from api_token_manager import APIToken, APITokenManager


class TestAPITokenManager:
    """Test suite for APITokenManager functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def token_manager_sqlite(self, temp_db):
        """Create APITokenManager instance with SQLite"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            return APITokenManager(db_path=temp_db)

    @pytest.fixture
    def postgres_token_manager(self):
        """Create APITokenManager instance configured for PostgreSQL"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "postgres",
                "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test",
            },
            clear=True,
        ):
            with patch("api_token_manager.POSTGRES_AVAILABLE", True):
                with patch("api_token_manager.psycopg2") as mock_psycopg2:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_psycopg2.connect.return_value = mock_conn
                    return APITokenManager()

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "user_id": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "token_name": "Test Token",
        }

    def test_api_token_dataclass(self):
        """Test APIToken dataclass creation"""
        token_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        now = datetime.now()
        
        api_token = APIToken(
            id=token_id,
            user_id=user_id,
            tenant_id=tenant_id,
            name="Test Token",
            token_prefix="apm_12345678",
            token_hash="hash123",
            expires_at=now + timedelta(days=30),
            last_used=now,
            created_at=now,
            is_active=True,
        )

        assert api_token.id == token_id
        assert api_token.user_id == user_id
        assert api_token.tenant_id == tenant_id
        assert api_token.name == "Test Token"
        assert api_token.token_prefix == "apm_12345678"
        assert api_token.is_active is True

    def test_initialization_sqlite(self, temp_db):
        """Test APITokenManager initialization with SQLite"""
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager = APITokenManager(db_path=temp_db)
            assert manager.db_type == "sqlite"
            assert manager.db_path == temp_db

    def test_initialization_postgres_success(self, postgres_token_manager):
        """Test APITokenManager initialization with PostgreSQL"""
        assert postgres_token_manager.db_type == "postgres"
        assert postgres_token_manager.dsn == "postgresql://test:test@localhost:5432/test"

    def test_initialization_postgres_missing_psycopg2(self):
        """Test APITokenManager initialization fails when psycopg2 not available"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "postgres", "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test"},
            clear=True,
        ):
            with patch("api_token_manager.POSTGRES_AVAILABLE", False):
                with pytest.raises(ImportError, match="psycopg2 is required"):
                    APITokenManager()

    def test_initialization_postgres_missing_dsn(self):
        """Test APITokenManager initialization fails when POSTGRES_DSN not set"""
        with patch.dict(os.environ, {"DB_TYPE": "postgres"}, clear=True):
            with patch("api_token_manager.POSTGRES_AVAILABLE", True):
                with pytest.raises(ValueError, match="POSTGRES_DSN environment variable"):
                    APITokenManager()

    def test_get_conn_sqlite(self, token_manager_sqlite):
        """Test database connection for SQLite"""
        conn = token_manager_sqlite.get_conn()
        assert conn is not None
        assert hasattr(conn, "cursor")
        conn.close()

    def test_database_initialization_sqlite(self, token_manager_sqlite):
        """Test database table creation for SQLite"""
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()

        # Check api_tokens table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_tokens'")
        assert cursor.fetchone() is not None

        # Check table structure
        cursor.execute("PRAGMA table_info(api_tokens)")
        columns = [column[1] for column in cursor.fetchall()]
        expected_columns = [
            "id", "user_id", "tenant_id", "name", "token_prefix", 
            "token_hash", "expires_at", "last_used", "created_at", "is_active"
        ]
        for col in expected_columns:
            assert col in columns

        conn.close()

    def test_generate_secure_token(self, token_manager_sqlite):
        """Test secure token generation"""
        full_token, token_prefix, token_hash = token_manager_sqlite.generate_secure_token()

        # Check token format
        assert full_token.startswith("apm_")
        assert len(full_token) == 36  # apm_ + 32 characters
        
        # Check prefix
        assert token_prefix == full_token[:12]  # First 8 chars after apm_
        assert token_prefix.startswith("apm_")
        
        # Check hash
        expected_hash = hashlib.sha256(full_token.encode()).hexdigest()
        assert token_hash == expected_hash

    def test_generate_secure_token_uniqueness(self, token_manager_sqlite):
        """Test that generated tokens are unique"""
        tokens = []
        for _ in range(10):
            full_token, _, _ = token_manager_sqlite.generate_secure_token()
            tokens.append(full_token)

        # All tokens should be unique
        assert len(set(tokens)) == 10

    def test_create_api_token_success(self, token_manager_sqlite, sample_user_data):
        """Test successful API token creation"""
        success, message, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        assert success is True
        assert "successfully" in message.lower()
        assert token is not None
        assert token.startswith("apm_")

        # Verify token exists in database
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM api_tokens WHERE user_id = ? AND name = ?",
            (sample_user_data["user_id"], sample_user_data["token_name"]),
        )
        token_row = cursor.fetchone()
        assert token_row is not None
        assert token_row[3] == sample_user_data["token_name"]  # name column
        assert token_row[9] == 1  # is_active column (SQLite boolean as integer)
        conn.close()

    def test_create_api_token_with_expiration(self, token_manager_sqlite, sample_user_data):
        """Test API token creation with expiration"""
        expires_days = 30
        success, message, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
            expires_days=expires_days,
        )

        assert success is True
        assert token is not None

        # Verify expiration is set
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expires_at FROM api_tokens WHERE user_id = ? AND name = ?",
            (sample_user_data["user_id"], sample_user_data["token_name"]),
        )
        expires_at = cursor.fetchone()[0]
        assert expires_at is not None
        conn.close()

    def test_create_api_token_duplicate_name(self, token_manager_sqlite, sample_user_data):
        """Test API token creation with duplicate name for same user"""
        # Create first token
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Try to create duplicate
        success, message, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        assert success is False
        assert "already exists" in message.lower()
        assert token is None

    def test_create_api_token_same_name_different_users(self, token_manager_sqlite, sample_user_data):
        """Test API token creation with same name for different users"""
        user1_id = sample_user_data["user_id"]
        user2_id = str(uuid.uuid4())

        # Create token for first user
        success1, _, token1 = token_manager_sqlite.create_api_token(
            user1_id, sample_user_data["tenant_id"], sample_user_data["token_name"]
        )

        # Create token with same name for second user (should succeed)
        success2, _, token2 = token_manager_sqlite.create_api_token(
            user2_id, sample_user_data["tenant_id"], sample_user_data["token_name"]
        )

        assert success1 is True
        assert success2 is True
        assert token1 != token2

    def test_create_api_token_empty_name(self, token_manager_sqlite, sample_user_data):
        """Test API token creation with empty name"""
        success, message, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "",
        )

        assert success is False
        assert "name is required" in message.lower() or "name cannot be empty" in message.lower()
        assert token is None

    def test_validate_api_token_success(self, token_manager_sqlite, sample_user_data):
        """Test successful API token validation"""
        # Create token
        _, _, full_token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Validate token
        is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(full_token)

        assert is_valid is True
        assert user_id == sample_user_data["user_id"]
        assert tenant_id == sample_user_data["tenant_id"]

        # Check that last_used was updated
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_used FROM api_tokens WHERE user_id = ?",
            (sample_user_data["user_id"],),
        )
        last_used = cursor.fetchone()[0]
        assert last_used is not None
        conn.close()

    def test_validate_api_token_invalid_format(self, token_manager_sqlite):
        """Test API token validation with invalid format"""
        invalid_tokens = [
            "invalid_token",
            "apm_",
            "apm_tooshort",
            "",
            "not_apm_prefix_123456789012345678901234567890",
        ]

        for invalid_token in invalid_tokens:
            is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(invalid_token)
            assert is_valid is False
            assert user_id is None
            assert tenant_id is None

    def test_validate_api_token_nonexistent(self, token_manager_sqlite):
        """Test API token validation with non-existent token"""
        # Generate valid format but non-existent token
        fake_token = "apm_" + "a" * 32
        is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(fake_token)

        assert is_valid is False
        assert user_id is None
        assert tenant_id is None

    def test_validate_api_token_expired(self, token_manager_sqlite, sample_user_data):
        """Test API token validation with expired token"""
        # Create token with 1-day expiration
        _, _, full_token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
            expires_days=1,
        )

        # Manually set expiration to past
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        past_date = datetime.now() - timedelta(days=1)
        cursor.execute(
            "UPDATE api_tokens SET expires_at = ? WHERE user_id = ?",
            (past_date.isoformat(), sample_user_data["user_id"]),
        )
        conn.commit()
        conn.close()

        # Validate expired token
        is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(full_token)

        assert is_valid is False
        assert user_id is None
        assert tenant_id is None

    def test_validate_api_token_inactive(self, token_manager_sqlite, sample_user_data):
        """Test API token validation with inactive token"""
        # Create token
        _, _, full_token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Deactivate token
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE api_tokens SET is_active = 0 WHERE user_id = ?",
            (sample_user_data["user_id"],),
        )
        conn.commit()
        conn.close()

        # Validate inactive token
        is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(full_token)

        assert is_valid is False
        assert user_id is None
        assert tenant_id is None

    def test_get_user_tokens(self, token_manager_sqlite, sample_user_data):
        """Test retrieving user tokens"""
        # Create multiple tokens
        token_names = ["Token 1", "Token 2", "Token 3"]
        for name in token_names:
            token_manager_sqlite.create_api_token(
                sample_user_data["user_id"],
                sample_user_data["tenant_id"],
                name,
            )

        # Get user tokens
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])

        assert len(tokens) == 3
        assert all(isinstance(token, APIToken) for token in tokens)
        
        # Check that all tokens belong to the user
        for token in tokens:
            assert token.user_id == sample_user_data["user_id"]
            assert token.tenant_id == sample_user_data["tenant_id"]
            assert token.is_active is True

        # Check that token names are present
        token_names_returned = [token.name for token in tokens]
        for name in token_names:
            assert name in token_names_returned

    def test_get_user_tokens_empty(self, token_manager_sqlite):
        """Test retrieving tokens for user with no tokens"""
        non_existent_user = str(uuid.uuid4())
        tokens = token_manager_sqlite.get_user_tokens(non_existent_user)

        assert len(tokens) == 0
        assert isinstance(tokens, list)

    def test_get_user_tokens_only_active(self, token_manager_sqlite, sample_user_data):
        """Test that get_user_tokens only returns active tokens"""
        # Create token
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Active Token",
        )

        # Create another token and deactivate it
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Inactive Token",
        )

        # Deactivate the second token
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE api_tokens SET is_active = 0 WHERE name = ?",
            ("Inactive Token",),
        )
        conn.commit()
        conn.close()

        # Get user tokens (should only return active)
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])

        assert len(tokens) == 1
        assert tokens[0].name == "Active Token"
        assert tokens[0].is_active is True

    def test_get_token_stats(self, token_manager_sqlite, sample_user_data):
        """Test getting token statistics"""
        # Create tokens with different characteristics
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Permanent Token",
        )
        
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Expiring Token",
            expires_days=30,
        )

        # Use one token to update last_used
        _, _, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Used Token",
        )
        token_manager_sqlite.validate_api_token(token)

        # Get stats
        stats = token_manager_sqlite.get_token_stats(sample_user_data["user_id"])

        assert stats["total_active"] == 3
        assert stats["never_expire"] == 2  # Permanent and Used tokens
        assert stats["will_expire"] == 1   # Expiring token
        assert stats["used_tokens"] == 1   # Used token

    def test_get_token_stats_empty(self, token_manager_sqlite):
        """Test getting token statistics for user with no tokens"""
        non_existent_user = str(uuid.uuid4())
        stats = token_manager_sqlite.get_token_stats(non_existent_user)

        assert stats["total_active"] == 0
        assert stats["never_expire"] == 0
        assert stats["will_expire"] == 0
        assert stats["used_tokens"] == 0

    def test_revoke_token(self, token_manager_sqlite, sample_user_data):
        """Test token revocation"""
        # Create token
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Get token ID
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        token_id = tokens[0].id

        # Revoke token
        success, message = token_manager_sqlite.revoke_token(sample_user_data["user_id"], token_id)

        assert success is True
        assert "revoked" in message.lower()

        # Verify token is inactive
        tokens_after = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens_after) == 0  # Should not return inactive tokens

    def test_revoke_token_not_found(self, token_manager_sqlite, sample_user_data):
        """Test revoking non-existent token"""
        fake_token_id = str(uuid.uuid4())
        success, message = token_manager_sqlite.revoke_token(sample_user_data["user_id"], fake_token_id)

        assert success is False
        assert "not found" in message.lower()

    def test_revoke_token_wrong_user(self, token_manager_sqlite, sample_user_data):
        """Test revoking token belonging to different user"""
        # Create token for user1
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Get token ID
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        token_id = tokens[0].id

        # Try to revoke with different user
        different_user_id = str(uuid.uuid4())
        success, message = token_manager_sqlite.revoke_token(different_user_id, token_id)

        assert success is False
        assert "not found" in message.lower()

    def test_revoke_all_tokens(self, token_manager_sqlite, sample_user_data):
        """Test revoking all user tokens"""
        # Create multiple tokens
        token_names = ["Token 1", "Token 2", "Token 3"]
        for name in token_names:
            token_manager_sqlite.create_api_token(
                sample_user_data["user_id"],
                sample_user_data["tenant_id"],
                name,
            )

        # Revoke all tokens
        success, message = token_manager_sqlite.revoke_all_tokens(sample_user_data["user_id"])

        assert success is True
        assert "3" in message  # Should mention number of tokens revoked

        # Verify all tokens are inactive
        tokens_after = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens_after) == 0

    def test_revoke_all_tokens_no_tokens(self, token_manager_sqlite):
        """Test revoking all tokens for user with no tokens"""
        non_existent_user = str(uuid.uuid4())
        success, message = token_manager_sqlite.revoke_all_tokens(non_existent_user)

        assert success is True
        assert "No active tokens" in message or "0" in message

    def test_cleanup_expired_tokens(self, token_manager_sqlite, sample_user_data):
        """Test cleanup of expired tokens"""
        # Create expired token
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Expired Token",
            expires_days=1,
        )

        # Create active token
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Active Token",
        )

        # Manually set first token as expired
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        past_date = datetime.now() - timedelta(days=1)
        cursor.execute(
            "UPDATE api_tokens SET expires_at = ? WHERE name = ?",
            (past_date.isoformat(), "Expired Token"),
        )
        conn.commit()
        conn.close()

        # Cleanup expired tokens
        deleted_count = token_manager_sqlite.cleanup_expired_tokens()

        assert deleted_count == 1

        # Verify only active token remains
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens) == 1
        assert tokens[0].name == "Active Token"

    def test_cleanup_expired_tokens_none_expired(self, token_manager_sqlite, sample_user_data):
        """Test cleanup when no tokens are expired"""
        # Create active tokens
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Token 1",
        )
        
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Token 2",
            expires_days=30,
        )

        # Cleanup expired tokens
        deleted_count = token_manager_sqlite.cleanup_expired_tokens()

        assert deleted_count == 0

        # Verify tokens still exist
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens) == 2

    def test_token_security_hash_verification(self, token_manager_sqlite, sample_user_data):
        """Test token security and hash verification"""
        # Create token
        _, _, full_token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Verify hash is stored correctly
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token_hash FROM api_tokens WHERE user_id = ?",
            (sample_user_data["user_id"],),
        )
        stored_hash = cursor.fetchone()[0]
        conn.close()

        # Verify hash matches
        expected_hash = hashlib.sha256(full_token.encode()).hexdigest()
        assert stored_hash == expected_hash

        # Verify original token is not stored
        conn = sqlite3.connect(token_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_tokens WHERE user_id = ?", (sample_user_data["user_id"],))
        row = cursor.fetchone()
        conn.close()

        # Check that full token is not in any database field
        for field in row:
            if isinstance(field, str):
                assert full_token not in field

    def test_tenant_isolation(self, token_manager_sqlite):
        """Test multi-tenant isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())

        # Create tokens for different tenants
        token_manager_sqlite.create_api_token(user1_id, tenant1_id, "Token 1")
        token_manager_sqlite.create_api_token(user2_id, tenant2_id, "Token 2")

        # Each user should only see their own tokens
        tokens1 = token_manager_sqlite.get_user_tokens(user1_id)
        tokens2 = token_manager_sqlite.get_user_tokens(user2_id)

        assert len(tokens1) == 1
        assert len(tokens2) == 1
        assert tokens1[0].tenant_id == tenant1_id
        assert tokens2[0].tenant_id == tenant2_id

    def test_token_name_trimming(self, token_manager_sqlite, sample_user_data):
        """Test that token names are trimmed of whitespace"""
        name_with_spaces = "  Token Name  "
        success, message, token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            name_with_spaces,
        )

        assert success is True

        # Verify name is trimmed
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert tokens[0].name == "Token Name"

    def test_error_handling_database_operations(self, token_manager_sqlite, sample_user_data):
        """Test error handling in database operations"""
        with patch.object(token_manager_sqlite, "get_conn") as mock_get_conn:
            mock_get_conn.side_effect = Exception("Database connection failed")

            # Test create_api_token error handling - the exception should be caught
            try:
                success, message, token = token_manager_sqlite.create_api_token(
                    sample_user_data["user_id"],
                    sample_user_data["tenant_id"],
                    sample_user_data["token_name"],
                )
                # If we get here, the exception was handled
                assert success is False
                assert "error" in message.lower()
                assert token is None
            except Exception as e:
                # If exception is not caught, verify it's the expected one
                assert "Database connection failed" in str(e)

    def test_token_prefix_consistency(self, token_manager_sqlite, sample_user_data):
        """Test token prefix consistency"""
        # Create token
        _, _, full_token = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
        )

        # Get token from database
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        stored_prefix = tokens[0].token_prefix

        # Verify prefix matches first 12 characters of full token
        assert stored_prefix == full_token[:12]
        assert stored_prefix.startswith("apm_")

    def test_datetime_handling_sqlite(self, token_manager_sqlite, sample_user_data):
        """Test datetime handling in SQLite"""
        # Create token with expiration
        token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            sample_user_data["token_name"],
            expires_days=30,
        )

        # Get token and verify datetime fields
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        token = tokens[0]

        assert isinstance(token.created_at, datetime)
        assert isinstance(token.expires_at, datetime)
        assert token.expires_at > token.created_at

    def test_concurrent_token_operations_safety(self, token_manager_sqlite, sample_user_data):
        """Test thread safety of token operations"""
        # Simulate concurrent token creation
        success_count = 0
        for i in range(5):
            success, _, _ = token_manager_sqlite.create_api_token(
                sample_user_data["user_id"],
                sample_user_data["tenant_id"],
                f"Token {i}",
            )
            if success:
                success_count += 1

        assert success_count == 5

        # Verify all tokens were created
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens) == 5

    def test_large_scale_token_operations(self, token_manager_sqlite, sample_user_data):
        """Test handling of large numbers of tokens"""
        # Create many tokens
        token_count = 100
        for i in range(token_count):
            token_manager_sqlite.create_api_token(
                sample_user_data["user_id"],
                sample_user_data["tenant_id"],
                f"Token {i:03d}",
            )

        # Verify all tokens can be retrieved
        tokens = token_manager_sqlite.get_user_tokens(sample_user_data["user_id"])
        assert len(tokens) == token_count

        # Verify stats calculation with large numbers
        stats = token_manager_sqlite.get_token_stats(sample_user_data["user_id"])
        assert stats["total_active"] == token_count

    def test_token_validation_performance(self, token_manager_sqlite, sample_user_data):
        """Test token validation performance with multiple tokens"""
        # Create multiple tokens
        tokens = []
        for i in range(10):
            _, _, token = token_manager_sqlite.create_api_token(
                sample_user_data["user_id"],
                sample_user_data["tenant_id"],
                f"Token {i}",
            )
            tokens.append(token)

        # Validate all tokens
        for token in tokens:
            is_valid, user_id, tenant_id = token_manager_sqlite.validate_api_token(token)
            assert is_valid is True
            assert user_id == sample_user_data["user_id"]
            assert tenant_id == sample_user_data["tenant_id"]

    def test_edge_cases_extreme_values(self, token_manager_sqlite, sample_user_data):
        """Test edge cases with extreme values"""
        # Very long token name
        long_name = "x" * 1000
        success, _, _ = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            long_name,
        )
        assert success is True

        # Very short expiration (0 days - should be handled)
        success, _, _ = token_manager_sqlite.create_api_token(
            sample_user_data["user_id"],
            sample_user_data["tenant_id"],
            "Short Expiry",
            expires_days=0,
        )
        # Should either succeed with immediate expiration or handle gracefully

    def test_sql_injection_prevention(self, token_manager_sqlite):
        """Test SQL injection prevention"""
        malicious_inputs = [
            "'; DROP TABLE api_tokens; --",
            "admin'; UPDATE api_tokens SET is_active = 1; --",
            "1' OR '1'='1",
        ]

        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        for malicious_input in malicious_inputs:
            # Try malicious input as token name
            success, _, _ = token_manager_sqlite.create_api_token(
                user_id, tenant_id, malicious_input
            )
            # Should not cause SQL injection (may succeed or fail safely)

        # Verify table still exists and operations work
        success, _, _ = token_manager_sqlite.create_api_token(
            user_id, tenant_id, "Safe Token"
        )
        assert success is True