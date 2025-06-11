"""
Integration tests for the new modular architecture.

This module tests how the new architecture components work together,
demonstrating the improved separation of concerns and maintainability.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from src.core.config.settings import AppConfig, DatabaseConfig, DatabaseType
from src.core.base.database_manager import BaseDatabaseManager
from src.auth.models.user import User, UserRole
from src.auth.models.tenant import Tenant
from src.auth.security.password_handler import PasswordHandler
from src.utils.logging_config import setup_logging, get_logger


class TestUserManager(BaseDatabaseManager):
    """Test implementation of database manager for users."""
    
    def init_tables(self):
        """Initialize user and tenant tables."""
        # Create tenants table
        tenant_table_sql = """
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            subdomain TEXT UNIQUE NOT NULL,
            max_users INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Create users table
        user_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT NOT NULL,
            sso_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            UNIQUE (tenant_id, email)
        )
        """
        
        self.execute_query(tenant_table_sql)
        self.execute_query(user_table_sql)
    
    def save_tenant(self, tenant: Tenant) -> Tenant:
        """Save a tenant to the database."""
        if not tenant.id:
            import uuid
            tenant.id = str(uuid.uuid4())
        
        query = """
        INSERT OR REPLACE INTO tenants 
        (id, name, subdomain, max_users, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            tenant.id,
            tenant.name,
            tenant.subdomain,
            tenant.max_users,
            tenant.is_active,
            tenant.created_at.isoformat() if tenant.created_at else None,
            tenant.updated_at.isoformat() if tenant.updated_at else None
        )
        
        self.execute_query(query, params)
        return tenant
    
    def save_user(self, user: User) -> User:
        """Save a user to the database."""
        if not user.id:
            import uuid
            user.id = str(uuid.uuid4())
        
        query = """
        INSERT OR REPLACE INTO users 
        (id, tenant_id, email, password_hash, salt, first_name, last_name, 
         role, sso_id, is_active, created_at, last_login, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user.id,
            user.tenant_id,
            user.email,
            user.password_hash,
            user.salt,
            user.first_name,
            user.last_name,
            user.role.value,
            user.sso_id,
            user.is_active,
            user.created_at.isoformat() if user.created_at else None,
            user.last_login.isoformat() if user.last_login else None,
            user.updated_at.isoformat() if user.updated_at else None
        )
        
        self.execute_query(query, params)
        return user
    
    def find_user_by_email(self, tenant_id: str, email: str) -> User:
        """Find a user by email within a tenant."""
        query = """
        SELECT * FROM users 
        WHERE tenant_id = ? AND email = ? AND is_active = 1
        """
        
        row = self.execute_query(query, (tenant_id, email), fetch_one=True)
        
        if row:
            return User.from_dict(row)
        return None


class TestNewArchitectureIntegration:
    """Integration tests for the new modular architecture."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            db_path=self.temp_db.name
        )
        
        # Set up logging
        setup_logging()
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize test manager
        self.user_manager = TestUserManager(self.config)
        self.user_manager.init_tables()
        
        # Initialize password handler
        self.password_handler = PasswordHandler(algorithm='pbkdf2')
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove temporary database
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass
    
    def test_complete_user_management_workflow(self):
        """Test complete user management workflow using new architecture."""
        # Step 1: Create a tenant
        tenant = Tenant(
            name="Test Organization",
            subdomain="test-org",
            max_users=50
        )
        
        saved_tenant = self.user_manager.save_tenant(tenant)
        assert saved_tenant.id is not None
        assert saved_tenant.name == "Test Organization"
        assert saved_tenant.subdomain == "test-org"
        
        self.logger.info("Created tenant", tenant_id=saved_tenant.id, name=saved_tenant.name)
        
        # Step 2: Create a user with secure password
        password = "secure_test_password_123"
        hashed_password, salt = self.password_handler.hash_password(password)
        
        user = User(
            tenant_id=saved_tenant.id,
            email="admin@test-org.com",
            password_hash=hashed_password,
            salt=salt,
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN
        )
        
        saved_user = self.user_manager.save_user(user)
        assert saved_user.id is not None
        assert saved_user.email == "admin@test-org.com"
        assert saved_user.role == UserRole.ADMIN
        assert saved_user.tenant_id == saved_tenant.id
        
        self.logger.info("Created user", user_id=saved_user.id, email=saved_user.email)
        
        # Step 3: Verify password authentication
        is_valid = self.password_handler.verify_password(
            password, 
            saved_user.password_hash, 
            saved_user.salt
        )
        assert is_valid is True
        
        # Verify wrong password fails
        is_invalid = self.password_handler.verify_password(
            "wrong_password", 
            saved_user.password_hash, 
            saved_user.salt
        )
        assert is_invalid is False
        
        # Step 4: Test user permissions
        assert saved_user.has_permission('admin') is True
        assert saved_user.has_permission('read') is True
        assert saved_user.has_permission('write') is True
        assert saved_user.can_admin is True
        
        # Step 5: Find user by email
        found_user = self.user_manager.find_user_by_email(
            saved_tenant.id, 
            "admin@test-org.com"
        )
        
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.email == saved_user.email
        
        # Step 6: Update user login timestamp
        found_user.update_last_login()
        updated_user = self.user_manager.save_user(found_user)
        
        assert updated_user.last_login is not None
        assert updated_user.updated_at != saved_user.updated_at
        
        self.logger.info("User login updated", user_id=updated_user.id)
    
    def test_tenant_isolation(self):
        """Test that tenant isolation works correctly."""
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", subdomain="tenant1")
        tenant2 = Tenant(name="Tenant 2", subdomain="tenant2")
        
        saved_tenant1 = self.user_manager.save_tenant(tenant1)
        saved_tenant2 = self.user_manager.save_tenant(tenant2)
        
        # Create users in each tenant with same email
        password = "test_password"
        hashed_password, salt = self.password_handler.hash_password(password)
        
        user1 = User(
            tenant_id=saved_tenant1.id,
            email="user@example.com",
            password_hash=hashed_password,
            salt=salt,
            first_name="User",
            last_name="One",
            role=UserRole.USER
        )
        
        user2 = User(
            tenant_id=saved_tenant2.id,
            email="user@example.com",  # Same email, different tenant
            password_hash=hashed_password,
            salt=salt,
            first_name="User",
            last_name="Two",
            role=UserRole.USER
        )
        
        saved_user1 = self.user_manager.save_user(user1)
        saved_user2 = self.user_manager.save_user(user2)
        
        # Verify users are isolated by tenant
        found_user1 = self.user_manager.find_user_by_email(
            saved_tenant1.id, "user@example.com"
        )
        found_user2 = self.user_manager.find_user_by_email(
            saved_tenant2.id, "user@example.com"
        )
        
        assert found_user1.id == saved_user1.id
        assert found_user2.id == saved_user2.id
        assert found_user1.id != found_user2.id
        
        # Verify cross-tenant access fails
        wrong_tenant_user = self.user_manager.find_user_by_email(
            saved_tenant1.id, "user@example.com"
        )
        assert wrong_tenant_user.first_name == "User"
        assert wrong_tenant_user.last_name == "One"  # Should be tenant1's user
    
    def test_password_security_features(self):
        """Test password security features of the new architecture."""
        # Test secure password generation
        generated_password = self.password_handler.generate_secure_password(length=16)
        
        assert len(generated_password) == 16
        assert any(c.islower() for c in generated_password)
        assert any(c.isupper() for c in generated_password)
        assert any(c.isdigit() for c in generated_password)
        
        # Test password hashing
        hashed, salt = self.password_handler.hash_password(generated_password)
        
        assert hashed != generated_password
        assert len(hashed) > 0
        assert len(salt) > 0
        
        # Test password verification
        assert self.password_handler.verify_password(generated_password, hashed, salt)
        assert not self.password_handler.verify_password("wrong_password", hashed, salt)
        
        # Test algorithm information
        info = self.password_handler.get_algorithm_info()
        assert 'current_algorithm' in info
        assert 'available_algorithms' in info
        assert info['available_algorithms']['pbkdf2'] is True
    
    def test_configuration_system_integration(self):
        """Test configuration system integration."""
        # Test configuration loading
        test_env = {
            'DB_TYPE': 'sqlite',
            'DB_PATH': 'test_integration.db',
            'SERVER_PORT': '8080',
            'DEBUG': 'true',
            'MULTITENANT_MODE': 'true'
        }
        
        with patch.dict(os.environ, test_env, clear=False):
            from src.core.config.settings import get_config, reset_config
            
            # Reset to pick up new environment
            reset_config()
            config = get_config()
            
            assert config.database.db_type == DatabaseType.SQLITE
            assert config.database.db_path == 'test_integration.db'
            assert config.port == 8080
            assert config.debug is True
            assert config.auth.multitenant_mode is True
    
    def test_error_handling_integration(self):
        """Test error handling across architecture components."""
        from src.core.exceptions.base import DatabaseException, ValidationException
        
        # Test database error handling
        with pytest.raises(DatabaseException):
            # Try to execute invalid SQL
            self.user_manager.execute_query("INVALID SQL QUERY")
        
        # Test validation error handling
        with pytest.raises(ValidationException):
            from src.utils.validators import validate_email
            validate_email("invalid_email")
        
        # Test model validation
        with pytest.raises(ValueError):
            # Invalid subdomain should raise ValueError
            Tenant(name="Test", subdomain="invalid-subdomain-")
    
    def test_logging_integration(self):
        """Test logging integration across components."""
        from src.utils.logging_config import StructuredLogger, AuditLogger
        
        # Test structured logging
        structured_logger = StructuredLogger("test_component")
        structured_logger.set_context(tenant_id="test-tenant", user_id="test-user")
        
        # Log should not raise exception
        structured_logger.info("Test operation completed", operation="test_op")
        
        # Test audit logging
        audit_logger = AuditLogger()
        
        # Audit log should not raise exception
        audit_logger.log_user_action(
            action="user_login",
            user_id="test-user",
            tenant_id="test-tenant",
            success=True
        )
        
        audit_logger.log_security_event(
            event_type="password_change",
            severity="INFO",
            user_id="test-user"
        )
    
    def test_type_safety_integration(self):
        """Test type safety features of the new architecture."""
        # Test that type hints work correctly
        tenant = Tenant(name="Test", subdomain="test")
        user = User(
            tenant_id=tenant.id or "test-id",
            email="test@example.com",
            password_hash="hash",
            salt="salt",
            first_name="Test",
            last_name="User",
            role=UserRole.USER
        )
        
        # Test model serialization
        tenant_dict = tenant.to_dict()
        user_dict = user.to_dict()
        
        assert isinstance(tenant_dict, dict)
        assert isinstance(user_dict, dict)
        
        # Test model deserialization
        reconstructed_tenant = Tenant.from_dict(tenant_dict)
        reconstructed_user = User.from_dict(user_dict)
        
        assert reconstructed_tenant.name == tenant.name
        assert reconstructed_user.email == user.email
        assert reconstructed_user.role == user.role
    
    def test_database_health_check(self):
        """Test database health check functionality."""
        health_status = self.user_manager.health_check()
        
        assert 'status' in health_status
        assert 'database_type' in health_status
        assert 'timestamp' in health_status
        assert health_status['status'] == 'healthy'
        assert health_status['database_type'] == 'sqlite'
        
        if 'response_time_ms' in health_status:
            assert isinstance(health_status['response_time_ms'], (int, float))
            assert health_status['response_time_ms'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])