"""
Comprehensive unit tests for AuthManager class
Testing authentication, user management, tenant operations, and SSO functionality
"""

import hashlib
import os
import sqlite3
import tempfile
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest
import requests

from auth_manager import AuthManager, Tenant, User


class TestAuthManager:
    """Test suite for AuthManager functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def auth_manager(self, temp_db):
        """Create AuthManager instance with temporary database"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "sqlite",
                "DB_PATH": temp_db,
                "LOCAL_DEV_MODE": "false",
                "SECRET_KEY": "test_secret_key_for_jwt_signing",
            },
            clear=True,
        ):
            return AuthManager(db_path=temp_db)

    @pytest.fixture
    def auth_manager_dev_mode(self, temp_db):
        """Create AuthManager instance in local dev mode"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "sqlite",
                "DB_PATH": temp_db,
                "LOCAL_DEV_MODE": "true",
                "SECRET_KEY": "test_secret_key_for_jwt_signing",
            },
            clear=True,
        ):
            return AuthManager(db_path=temp_db)

    @pytest.fixture
    def postgres_auth_manager(self):
        """Create AuthManager instance configured for PostgreSQL"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "postgres",
                "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test",
                "LOCAL_DEV_MODE": "false",
                "SECRET_KEY": "test_secret_key_for_jwt_signing",
            },
            clear=True,
        ):
            with patch("auth_manager.POSTGRES_AVAILABLE", True):
                with patch("auth_manager.psycopg2") as mock_psycopg2:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_psycopg2.connect.return_value = mock_conn
                    return AuthManager()

    @pytest.fixture
    def sample_tenant_data(self):
        """Sample tenant data for testing"""
        return {
            "id": str(uuid.uuid4()),
            "name": "Test Company",
            "subdomain": "testco",
            "max_users": 50,
        }

    @pytest.fixture
    def sample_user_data(self, sample_tenant_data):
        """Sample user data for testing"""
        return {
            "tenant_id": sample_tenant_data["id"],
            "email": "test@testco.com",
            "password": "secure_password123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user",
        }

    def test_initialization_sqlite(self, temp_db):
        """Test AuthManager initialization with SQLite"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db, "LOCAL_DEV_MODE": "false"},
            clear=True,
        ):
            auth_manager = AuthManager(db_path=temp_db)
            assert auth_manager.db_type == "sqlite"
            assert auth_manager.db_path == temp_db
            assert not auth_manager.local_dev_mode

    def test_initialization_postgres_success(self, postgres_auth_manager):
        """Test AuthManager initialization with PostgreSQL"""
        assert postgres_auth_manager.db_type == "postgres"
        assert postgres_auth_manager.dsn == "postgresql://test:test@localhost:5432/test"

    def test_initialization_postgres_missing_psycopg2(self, temp_db):
        """Test AuthManager initialization fails when psycopg2 not available"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "postgres",
                "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test",
            },
            clear=True,
        ):
            with patch("auth_manager.POSTGRES_AVAILABLE", False):
                with pytest.raises(ImportError, match="psycopg2 is required"):
                    AuthManager()

    def test_initialization_postgres_missing_dsn(self, temp_db):
        """Test AuthManager initialization fails when POSTGRES_DSN not set"""
        with patch.dict(os.environ, {"DB_TYPE": "postgres"}, clear=True):
            with patch("auth_manager.POSTGRES_AVAILABLE", True):
                with pytest.raises(
                    ValueError, match="POSTGRES_DSN environment variable"
                ):
                    AuthManager()

    def test_password_hashing(self, auth_manager):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = auth_manager._hash_password(password)

        # Check format
        assert ":" in hashed
        salt, hash_part = hashed.split(":")
        assert len(salt) == 64  # 32 bytes hex encoded
        assert len(hash_part) == 64  # SHA256 hex encoded

        # Verify password
        assert auth_manager._verify_password(password, hashed)
        assert not auth_manager._verify_password("wrong_password", hashed)

    def test_password_verification_invalid_format(self, auth_manager):
        """Test password verification with invalid hash format"""
        assert not auth_manager._verify_password("password", "invalid_hash")
        assert not auth_manager._verify_password("password", "no_colon_separator")

    def test_database_initialization(self, auth_manager):
        """Test database tables are created correctly"""
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()

        # Check tenants table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tenants'"
        )
        assert cursor.fetchone() is not None

        # Check users table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cursor.fetchone() is not None

        # Check user_sessions table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_ensure_default_tenant_dev_mode(self, auth_manager_dev_mode):
        """Test default tenant creation in dev mode"""
        conn = sqlite3.connect(auth_manager_dev_mode.db_path)
        cursor = conn.cursor()

        # Check default tenant exists
        cursor.execute("SELECT * FROM tenants WHERE subdomain = 'localhost'")
        tenant = cursor.fetchone()
        assert tenant is not None
        assert tenant[1] == "Local Development"  # name
        assert tenant[2] == "localhost"  # subdomain

        # Check default admin user exists
        cursor.execute("SELECT * FROM users WHERE email = 'admin@localhost'")
        user = cursor.fetchone()
        assert user is not None
        assert user[4] == "Admin"  # first_name
        assert user[6] == "admin"  # role

        conn.close()

    def test_create_tenant_success(self, auth_manager, sample_tenant_data):
        """Test successful tenant creation"""
        success, message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        assert success
        assert "created successfully" in message

        # Verify tenant exists in database
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tenants WHERE subdomain = ?",
            (sample_tenant_data["subdomain"],),
        )
        tenant = cursor.fetchone()
        assert tenant is not None
        assert tenant[1] == sample_tenant_data["name"]
        conn.close()

    def test_create_tenant_duplicate_subdomain(self, auth_manager, sample_tenant_data):
        """Test tenant creation fails with duplicate subdomain"""
        # Create first tenant
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Try to create duplicate
        success, message = auth_manager.create_tenant(
            "Another Company", sample_tenant_data["subdomain"], 100
        )

        assert not success
        assert "already exists" in message

    def test_create_tenant_database_error(self, auth_manager):
        """Test tenant creation handles database errors"""
        with patch.object(auth_manager, "get_conn") as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            success, message = auth_manager.create_tenant("Test", "test", 100)

            assert not success
            assert "Error creating tenant" in message

    def test_create_user_success(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test successful user creation"""
        # Create tenant first
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        success, message = auth_manager.create_user(
            sample_user_data["tenant_id"],
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
            sample_user_data["role"],
        )

        assert success
        assert "created successfully" in message

        # Verify user exists and password is hashed
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ?", (sample_user_data["email"],)
        )
        user = cursor.fetchone()
        assert user is not None
        assert user[3] is not None  # password_hash
        assert ":" in user[3]  # hashed format
        conn.close()

    def test_create_user_duplicate_email(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test user creation fails with duplicate email"""
        # Create tenant first
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Create first user
        auth_manager.create_user(
            sample_user_data["tenant_id"],
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )

        # Try to create duplicate
        success, message = auth_manager.create_user(
            sample_user_data["tenant_id"],
            sample_user_data["email"],
            "different_password",
            "Jane",
            "Smith",
        )

        assert not success
        assert "already exists" in message

    def test_create_user_max_limit_reached(self, auth_manager):
        """Test user creation fails when tenant max limit reached"""
        # Create tenant with limit of 1
        tenant_id = str(uuid.uuid4())
        auth_manager.create_tenant("Limited Company", "limited", 1)

        # Update tenant ID in database
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tenants SET id = ? WHERE subdomain = 'limited'", (tenant_id,)
        )
        conn.commit()

        # Create first user
        success1, _ = auth_manager.create_user(
            tenant_id, "user1@limited.com", "pass", "User", "One"
        )
        assert success1

        # Try to create second user (should fail)
        success2, message = auth_manager.create_user(
            tenant_id, "user2@limited.com", "pass", "User", "Two"
        )

        assert not success2
        assert "maximum user limit" in message

        conn.close()

    def test_create_user_sso_without_password(self, auth_manager, sample_tenant_data):
        """Test creating SSO user without password"""
        # Create tenant first
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        success, message = auth_manager.create_user(
            sample_tenant_data["id"],
            "sso@testco.com",
            "",  # No password for SSO
            "SSO",
            "User",
            "user",
            "sso_external_id_123",
        )

        assert success
        assert "created successfully" in message

        # Verify user has SSO ID but no password hash
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash, sso_id FROM users WHERE email = 'sso@testco.com'"
        )
        user_data = cursor.fetchone()
        assert user_data[0] is None  # No password hash
        assert user_data[1] == "sso_external_id_123"  # Has SSO ID
        conn.close()

    def test_authenticate_user_success(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test successful user authentication"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation by finding it in all tenants
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,  # Use the tenant ID from the retrieved tenant
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        success, user, message = auth_manager.authenticate_user(
            sample_user_data["email"], sample_user_data["password"]
        )

        assert success
        assert user is not None
        assert isinstance(user, User)
        assert user.email == sample_user_data["email"]
        assert user.first_name == sample_user_data["first_name"]
        assert "successful" in message

        # Check last_login was updated
        assert user.last_login is not None

    def test_authenticate_user_with_subdomain(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test user authentication with tenant subdomain filtering"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Authenticate with correct subdomain
        success, user, message = auth_manager.authenticate_user(
            sample_user_data["email"],
            sample_user_data["password"],
            sample_tenant_data["subdomain"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        assert success
        assert user is not None

        # Authenticate with wrong subdomain
        success, user, message = auth_manager.authenticate_user(
            sample_user_data["email"], sample_user_data["password"], "wrong_subdomain"
        )

        assert not success
        assert user is None

    def test_authenticate_user_invalid_credentials(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test authentication with invalid credentials"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Wrong email
        success, user, message = auth_manager.authenticate_user(
            "wrong@email.com", sample_user_data["password"]
        )
        assert not success
        assert user is None
        assert "Invalid email or password" in message

        # Wrong password
        success, user, message = auth_manager.authenticate_user(
            sample_user_data["email"], "wrong_password"
        )
        assert not success
        assert user is None
        assert "Invalid email or password" in message

    def test_authenticate_user_inactive_user(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test authentication fails for inactive user"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Deactivate user
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET is_active = 0 WHERE email = ?",
            (sample_user_data["email"],),
        )
        conn.commit()
        conn.close()

        success, user, message = auth_manager.authenticate_user(
            sample_user_data["email"], sample_user_data["password"]
        )

        assert not success
        assert user is None

    def test_create_session(self, auth_manager, sample_tenant_data, sample_user_data):
        """Test session creation and JWT token generation"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Get user ID
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ?", (sample_user_data["email"],)
        )
        user_id = cursor.fetchone()[0]
        conn.close()

        # Create session
        token = auth_manager.create_session(user_id, "127.0.0.1", "Mozilla/5.0")

        assert token is not None
        assert isinstance(token, str)

        # Verify JWT token structure
        payload = jwt.decode(token, auth_manager.secret_key, algorithms=["HS256"])
        assert "session_id" in payload
        assert "user_id" in payload
        assert payload["user_id"] == user_id

        # Verify session stored in database
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_sessions WHERE user_id = ?", (user_id,))
        session = cursor.fetchone()
        assert session is not None
        assert session[1] == user_id  # user_id
        assert session[5] == "127.0.0.1"  # ip_address
        assert session[6] == "Mozilla/5.0"  # user_agent
        conn.close()

    def test_validate_session_success(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test successful session validation"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Get user ID
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ?", (sample_user_data["email"],)
        )
        user_id = cursor.fetchone()[0]
        conn.close()

        # Create and validate session
        token = auth_manager.create_session(user_id)
        valid, user = auth_manager.validate_session(token)

        assert valid
        assert user is not None
        assert isinstance(user, User)
        assert user.id == user_id
        assert user.email == sample_user_data["email"]

    def test_validate_session_invalid_token(self, auth_manager):
        """Test session validation with invalid token"""
        # Invalid JWT
        valid, user = auth_manager.validate_session("invalid.token.here")
        assert not valid
        assert user is None

        # Valid JWT but wrong secret
        fake_payload = {
            "session_id": "123",
            "user_id": "456",
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
        }
        fake_token = jwt.encode(fake_payload, "wrong_secret", algorithm="HS256")
        valid, user = auth_manager.validate_session(fake_token)
        assert not valid
        assert user is None

    def test_validate_session_expired_token(self, auth_manager):
        """Test session validation with expired token"""
        # Create expired token
        expired_payload = {
            "session_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "exp": (datetime.now() - timedelta(hours=1)).timestamp(),  # Expired
        }
        expired_token = jwt.encode(
            expired_payload, auth_manager.secret_key, algorithm="HS256"
        )

        valid, user = auth_manager.validate_session(expired_token)
        assert not valid
        assert user is None

    def test_validate_session_nonexistent_session(self, auth_manager):
        """Test session validation for non-existent session in database"""
        # Create valid JWT but no corresponding database session
        fake_payload = {
            "session_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
        }
        fake_token = jwt.encode(
            fake_payload, auth_manager.secret_key, algorithm="HS256"
        )

        valid, user = auth_manager.validate_session(fake_token)
        assert not valid
        assert user is None

    def test_logout_user_success(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test successful user logout"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Get user ID and create session
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ?", (sample_user_data["email"],)
        )
        user_id = cursor.fetchone()[0]
        conn.close()

        token = auth_manager.create_session(user_id)

        # Verify session exists
        valid, _ = auth_manager.validate_session(token)
        assert valid

        # Logout
        success = auth_manager.logout_user(token)
        assert success

        # Verify session no longer valid
        valid, _ = auth_manager.validate_session(token)
        assert not valid

    def test_logout_user_invalid_token(self, auth_manager):
        """Test logout with invalid token"""
        success = auth_manager.logout_user("invalid.token")
        assert not success

    def test_get_sso_login_url(self, auth_manager):
        """Test SSO login URL generation"""
        with patch.dict(
            os.environ,
            {
                "SSO_ENABLED": "true",
                "SSO_CLIENT_ID": "test_client_id",
                "SSO_AUTHORITY": "https://login.example.com",
                "SSO_REDIRECT_URI": "http://localhost:7860/auth/callback",
            },
        ):
            auth_manager.sso_enabled = True
            auth_manager.sso_client_id = "test_client_id"
            auth_manager.sso_authority = "https://login.example.com"
            auth_manager.sso_redirect_uri = "http://localhost:7860/auth/callback"

            url = auth_manager.get_sso_login_url("testco")

            assert url.startswith("https://login.example.com/oauth2/v2.0/authorize")
            assert "client_id=test_client_id" in url
            assert "response_type=code" in url
            assert "scope=openid+email+profile" in url
            assert "testco" in url  # subdomain in state

    def test_get_sso_login_url_disabled(self, auth_manager):
        """Test SSO login URL when SSO is disabled"""
        auth_manager.sso_enabled = False
        url = auth_manager.get_sso_login_url()
        assert url == ""

    def test_get_entra_id_login_url(self, auth_manager):
        """Test Entra ID login URL generation"""
        with patch.dict(
            os.environ,
            {
                "ENTRA_ID_ENABLED": "true",
                "ENTRA_CLIENT_ID": "entra_client_id",
                "ENTRA_TENANT_ID": "tenant_id_123",
                "ENTRA_REDIRECT_URI": "http://localhost:7860/auth/entra-callback",
            },
        ):
            auth_manager.entra_id_enabled = True
            auth_manager.entra_client_id = "entra_client_id"
            auth_manager.entra_tenant_id = "tenant_id_123"
            auth_manager.entra_redirect_uri = (
                "http://localhost:7860/auth/entra-callback"
            )

            url = auth_manager.get_entra_id_login_url("company")

            assert url.startswith(
                "https://login.microsoftonline.com/tenant_id_123/oauth2/v2.0/authorize"
            )
            assert "client_id=entra_client_id" in url
            assert "company" in url  # subdomain in state

    def test_get_entra_id_login_url_disabled(self, auth_manager):
        """Test Entra ID login URL when disabled"""
        auth_manager.entra_id_enabled = False
        url = auth_manager.get_entra_id_login_url()
        assert url == ""

    @patch("auth_manager.requests.post")
    @patch("auth_manager.requests.get")
    def test_handle_sso_callback_success(
        self, mock_get, mock_post, auth_manager, sample_tenant_data
    ):
        """Test successful SSO callback handling"""
        # Setup SSO configuration
        auth_manager.sso_enabled = True
        auth_manager.sso_client_id = "test_client"
        auth_manager.sso_client_secret = "test_secret"
        auth_manager.sso_authority = "https://login.example.com"
        auth_manager.sso_redirect_uri = "http://localhost:7860/auth/callback"

        # Create tenant
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Mock token exchange response
        mock_post.return_value.json.return_value = {"access_token": "access_token_123"}
        mock_post.return_value.raise_for_status.return_value = None

        # Mock user info response
        mock_get.return_value.json.return_value = {
            "sub": "sso_user_123",
            "email": "sso.user@testco.com",
            "given_name": "SSO",
            "family_name": "User",
        }
        mock_get.return_value.raise_for_status.return_value = None

        # Handle callback
        success, user, message = auth_manager.handle_sso_callback(
            "auth_code_123", f"state:{sample_tenant_data['subdomain']}"
        )

        assert success
        assert user is not None
        assert isinstance(user, User)
        assert user.email == "sso.user@testco.com"
        assert user.first_name == "SSO"
        assert "created and authenticated" in message

    def test_handle_sso_callback_disabled(self, auth_manager):
        """Test SSO callback when SSO is disabled"""
        auth_manager.sso_enabled = False
        success, user, message = auth_manager.handle_sso_callback("code", "state")

        assert not success
        assert user is None
        assert "not enabled" in message

    @patch("auth_manager.requests.post")
    def test_handle_sso_callback_token_error(
        self, mock_post, auth_manager, sample_tenant_data
    ):
        """Test SSO callback with token exchange error"""
        auth_manager.sso_enabled = True
        auth_manager.sso_client_id = "test_client"
        auth_manager.sso_client_secret = "test_secret"

        # Create tenant
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Mock token exchange failure
        mock_post.return_value.raise_for_status.side_effect = requests.RequestException(
            "Token error"
        )

        success, user, message = auth_manager.handle_sso_callback(
            "code", f"state:{sample_tenant_data['subdomain']}"
        )

        assert not success
        assert user is None
        assert "failed" in message

    def test_get_all_tenants(self, auth_manager, sample_tenant_data):
        """Test retrieving all tenants"""
        # Create multiple tenants
        auth_manager.create_tenant(
            sample_tenant_data["name"], sample_tenant_data["subdomain"], 50
        )
        auth_manager.create_tenant("Company B", "companyb", 100)

        tenants = auth_manager.get_all_tenants()

        assert len(tenants) == 2
        assert all(isinstance(t, Tenant) for t in tenants)
        tenant_names = [t.name for t in tenants]
        assert sample_tenant_data["name"] in tenant_names
        assert "Company B" in tenant_names

    def test_get_tenant_users(self, auth_manager, sample_tenant_data):
        """Test retrieving users for a specific tenant"""
        # Create tenant
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Create multiple users
        auth_manager.create_user(
            sample_tenant_data["id"], "user1@testco.com", "pass", "User", "One"
        )
        auth_manager.create_user(
            sample_tenant_data["id"], "user2@testco.com", "pass", "User", "Two"
        )

        users = auth_manager.get_tenant_users(sample_tenant_data["id"])

        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)
        user_emails = [u.email for u in users]
        assert "user1@testco.com" in user_emails
        assert "user2@testco.com" in user_emails

    def test_get_azure_ai_config(self, auth_manager):
        """Test Azure AI configuration retrieval"""
        with patch.dict(
            os.environ,
            {
                "AZURE_AI_ENABLED": "true",
                "AZURE_AI_ENDPOINT": "https://test.openai.azure.com",
                "AZURE_AI_KEY": "test_key",
                "AZURE_OPENAI_ENDPOINT": "https://test-openai.openai.azure.com",
                "AZURE_OPENAI_KEY": "openai_key",
            },
        ):
            auth_manager.azure_ai_enabled = True
            auth_manager.azure_ai_endpoint = "https://test.openai.azure.com"
            auth_manager.azure_ai_key = "test_key"
            auth_manager.azure_openai_endpoint = "https://test-openai.openai.azure.com"
            auth_manager.azure_openai_key = "openai_key"

            config = auth_manager.get_azure_ai_config()

            assert "azure_ai" in config
            assert config["azure_ai"]["endpoint"] == "https://test.openai.azure.com"
            assert config["azure_ai"]["api_key"] == "test_key"
            assert config["azure_ai"]["enabled"] is True

            assert "azure_openai" in config
            assert (
                config["azure_openai"]["endpoint"]
                == "https://test-openai.openai.azure.com"
            )
            assert config["azure_openai"]["api_key"] == "openai_key"

    @patch("auth_manager.requests.get")
    def test_validate_azure_credentials_success(self, mock_get, auth_manager):
        """Test successful Azure credential validation"""
        # Setup Azure configuration
        auth_manager.azure_openai_endpoint = "https://test.openai.azure.com"
        auth_manager.azure_openai_key = "valid_key"
        auth_manager.azure_openai_version = "2024-02-15-preview"

        # Mock successful API response
        mock_get.return_value.status_code = 200

        success, message = auth_manager.validate_azure_credentials()

        assert success
        assert "validated successfully" in message

    @patch("auth_manager.requests.get")
    def test_validate_azure_credentials_failure(self, mock_get, auth_manager):
        """Test Azure credential validation failure"""
        # Setup Azure configuration
        auth_manager.azure_openai_endpoint = "https://test.openai.azure.com"
        auth_manager.azure_openai_key = "invalid_key"
        auth_manager.azure_openai_version = "2024-02-15-preview"

        # Mock failed API response
        mock_get.return_value.status_code = 401

        success, message = auth_manager.validate_azure_credentials()

        assert not success
        assert "validation failed" in message

    def test_validate_azure_credentials_no_config(self, auth_manager):
        """Test Azure credential validation with no configuration"""
        success, message = auth_manager.validate_azure_credentials()

        assert not success
        assert "No Azure credentials configured" in message

    def test_is_entra_id_enabled(self, auth_manager):
        """Test Entra ID enabled check"""
        # Test disabled
        assert not auth_manager.is_entra_id_enabled()

        # Test enabled
        auth_manager.entra_id_enabled = True
        auth_manager.entra_client_id = "client_id"
        auth_manager.entra_client_secret = "client_secret"
        auth_manager.entra_tenant_id = "tenant_id"

        assert auth_manager.is_entra_id_enabled()

    def test_is_azure_ai_enabled(self, auth_manager):
        """Test Azure AI enabled check"""
        # Test disabled
        assert not auth_manager.is_azure_ai_enabled()

        # Test enabled with Azure AI
        auth_manager.azure_ai_enabled = True
        auth_manager.azure_ai_endpoint = "https://test.ai.azure.com"
        auth_manager.azure_ai_key = "key"

        assert auth_manager.is_azure_ai_enabled()

        # Test enabled with Azure OpenAI
        auth_manager.azure_ai_endpoint = None
        auth_manager.azure_ai_key = None
        auth_manager.azure_openai_endpoint = "https://test.openai.azure.com"
        auth_manager.azure_openai_key = "openai_key"

        assert auth_manager.is_azure_ai_enabled()

    def test_get_authentication_methods(self, auth_manager):
        """Test authentication methods availability"""
        # Default state
        methods = auth_manager.get_authentication_methods()
        assert methods["local"] is True
        assert methods["sso"] is False
        assert methods["entra_id"] is False
        assert methods["adfs"] is False

        # Enable SSO
        auth_manager.sso_enabled = True
        auth_manager.sso_client_id = "client_id"
        methods = auth_manager.get_authentication_methods()
        assert methods["sso"] is True

        # Enable Entra ID
        auth_manager.entra_id_enabled = True
        auth_manager.entra_client_id = "entra_client"
        auth_manager.entra_client_secret = "entra_secret"
        auth_manager.entra_tenant_id = "entra_tenant"
        methods = auth_manager.get_authentication_methods()
        assert methods["entra_id"] is True

    def test_error_handling_database_operations(self, auth_manager):
        """Test error handling in database operations"""
        with patch.object(auth_manager, "get_conn") as mock_get_conn:
            mock_get_conn.side_effect = Exception("Database connection failed")

            # Test authentication error handling
            success, user, message = auth_manager.authenticate_user(
                "test@example.com", "password"
            )
            assert not success
            assert user is None
            assert "Authentication error" in message

    def test_session_token_hash_consistency(
        self, auth_manager, sample_tenant_data, sample_user_data
    ):
        """Test that session token hashes are consistent"""
        # Create tenant and user
        tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )
        assert tenant_success, f"Failed to create tenant: {tenant_message}"

        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next(
            (t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None
        )
        assert tenant is not None, "Tenant should exist after creation"

        user_success, user_message = auth_manager.create_user(
            tenant.id,
            sample_user_data["email"],
            sample_user_data["password"],
            sample_user_data["first_name"],
            sample_user_data["last_name"],
        )
        assert user_success, f"Failed to create user: {user_message}"

        # Get user ID
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ?", (sample_user_data["email"],)
        )
        user_id = cursor.fetchone()[0]
        conn.close()

        # Create session
        token = auth_manager.create_session(user_id)

        # Verify token hash matches what's stored
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token_hash FROM user_sessions WHERE user_id = ?", (user_id,)
        )
        stored_hash = cursor.fetchone()[0]
        conn.close()

        assert token_hash == stored_hash

    def test_concurrent_user_creation_prevention(
        self, auth_manager, sample_tenant_data
    ):
        """Test that duplicate user creation is properly prevented"""
        # Create tenant
        auth_manager.create_tenant(
            sample_tenant_data["name"],
            sample_tenant_data["subdomain"],
            sample_tenant_data["max_users"],
        )

        # Simulate concurrent user creation attempts
        email = "concurrent@testco.com"

        success1, message1 = auth_manager.create_user(
            sample_tenant_data["id"], email, "password1", "User", "One"
        )
        success2, message2 = auth_manager.create_user(
            sample_tenant_data["id"], email, "password2", "User", "Two"
        )

        # One should succeed, one should fail
        assert success1 != success2  # One True, one False
        if success1:
            assert "already exists" in message2
        else:
            assert "already exists" in message1
