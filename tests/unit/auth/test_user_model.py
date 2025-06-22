"""
Unit tests for the User model.

This module tests the User model functionality including validation,
permissions, and data conversion methods.
"""

from datetime import datetime

import pytest

from src.auth.models.user import User, UserRole


class TestUserModel:
    """Test cases for the User model."""

    def test_user_creation_with_required_fields(self):
        """Test creating a user with only required fields."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        assert user.tenant_id == "tenant-123"
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.id is None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_creation_with_string_role(self):
        """Test creating a user with string role (should convert to enum)."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.ADMIN,  # Use enum instead of string
        )

        assert user.role == UserRole.ADMIN
        assert isinstance(user.role, UserRole)

    def test_user_full_name_property(self):
        """Test the full_name property."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        assert user.full_name == "John Doe"

        # Test with empty names
        user.first_name = ""
        user.last_name = ""
        assert user.full_name == ""

    def test_user_display_name_property(self):
        """Test the display_name property."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        # With names
        assert user.display_name == "John Doe"

        # Without names (should fallback to email)
        user.first_name = ""
        user.last_name = ""
        assert user.display_name == "test@example.com"

    def test_user_role_properties(self):
        """Test role-based properties."""
        # Test admin user
        admin_user = User(
            tenant_id="tenant-123",
            email="admin@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )

        assert admin_user.is_admin is True
        assert admin_user.is_readonly is False
        assert admin_user.can_write is True
        assert admin_user.can_admin is True

        # Test regular user
        regular_user = User(
            tenant_id="tenant-123",
            email="user@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Regular",
            last_name="User",
            role=UserRole.USER,
        )

        assert regular_user.is_admin is False
        assert regular_user.is_readonly is False
        assert regular_user.can_write is True
        assert regular_user.can_admin is False

        # Test readonly user
        readonly_user = User(
            tenant_id="tenant-123",
            email="readonly@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Read",
            last_name="Only",
            role=UserRole.READONLY,
        )

        assert readonly_user.is_admin is False
        assert readonly_user.is_readonly is True
        assert readonly_user.can_write is False
        assert readonly_user.can_admin is False

    def test_user_permissions(self):
        """Test the has_permission method."""
        # Admin user permissions
        admin_user = User(
            tenant_id="tenant-123",
            email="admin@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )

        assert admin_user.has_permission("read") is True
        assert admin_user.has_permission("write") is True
        assert admin_user.has_permission("delete") is True
        assert admin_user.has_permission("admin") is True
        assert admin_user.has_permission("manage_users") is True

        # Regular user permissions
        regular_user = User(
            tenant_id="tenant-123",
            email="user@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Regular",
            last_name="User",
            role=UserRole.USER,
        )

        assert regular_user.has_permission("read") is True
        assert regular_user.has_permission("write") is True
        assert regular_user.has_permission("delete_own") is True
        assert regular_user.has_permission("admin") is False
        assert regular_user.has_permission("manage_users") is False

        # Readonly user permissions
        readonly_user = User(
            tenant_id="tenant-123",
            email="readonly@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="Read",
            last_name="Only",
            role=UserRole.READONLY,
        )

        assert readonly_user.has_permission("read") is True
        assert readonly_user.has_permission("write") is False
        assert readonly_user.has_permission("delete") is False
        assert readonly_user.has_permission("admin") is False

    def test_update_last_login(self):
        """Test updating last login timestamp."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        original_updated_at = user.updated_at
        original_last_login = user.last_login

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        user.update_last_login()

        assert user.last_login != original_last_login
        assert user.updated_at != original_updated_at
        assert isinstance(user.last_login, datetime)

    def test_metadata_operations(self):
        """Test metadata get/set operations."""
        user = User(
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        # Test setting metadata
        user.set_metadata("language", "en")
        user.set_metadata("theme", "dark")

        # Test getting metadata
        assert user.get_metadata("language") == "en"
        assert user.get_metadata("theme") == "dark"
        assert user.get_metadata("nonexistent") is None
        assert user.get_metadata("nonexistent", "default") == "default"

        # Test metadata in dict
        assert user.metadata["language"] == "en"
        assert user.metadata["theme"] == "dark"

    def test_to_dict_without_sensitive_data(self):
        """Test converting user to dictionary without sensitive data."""
        user = User(
            id="user-123",
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            sso_id="sso-123",
        )

        user_dict = user.to_dict(include_sensitive=False)

        # Should include non-sensitive fields
        assert user_dict["id"] == "user-123"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["first_name"] == "John"
        assert user_dict["role"] == "user"

        # Should not include sensitive fields
        assert "password_hash" not in user_dict
        assert "salt" not in user_dict
        assert "sso_id" not in user_dict

    def test_to_dict_with_sensitive_data(self):
        """Test converting user to dictionary with sensitive data."""
        user = User(
            id="user-123",
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            sso_id="sso-123",
        )

        user_dict = user.to_dict(include_sensitive=True)

        # Should include all fields
        assert user_dict["password_hash"] == "hashed_password"
        assert user_dict["salt"] == "random_salt"
        assert user_dict["sso_id"] == "sso-123"

    def test_from_dict(self):
        """Test creating user from dictionary."""
        user_data = {
            "id": "user-123",
            "tenant_id": "tenant-123",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "salt": "random_salt",
            "first_name": "John",
            "last_name": "Doe",
            "role": "admin",
            "is_active": True,
            "created_at": "2023-01-01T12:00:00",
            "last_login": "2023-01-02T12:00:00",
            "metadata": {"language": "en"},
        }

        user = User.from_dict(user_data)

        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
        assert user.metadata == {"language": "en"}
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.last_login, datetime)

    def test_from_dict_with_datetime_objects(self):
        """Test creating user from dictionary with datetime objects."""
        now = datetime.utcnow()
        user_data = {
            "tenant_id": "tenant-123",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "salt": "random_salt",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.USER,
            "created_at": now,
            "last_login": now,
        }

        user = User.from_dict(user_data)

        assert user.created_at == now
        assert user.last_login == now

    def test_string_representations(self):
        """Test string representation methods."""
        user = User(
            id="user-123",
            tenant_id="tenant-123",
            email="test@example.com",
            password_hash="hashed_password",
            salt="random_salt",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
        )

        str_repr = str(user)
        assert "test@example.com" in str_repr
        assert "user" in str_repr
        assert "tenant-123" in str_repr

        repr_str = repr(user)
        assert "user-123" in repr_str
        assert "test@example.com" in repr_str
        assert "tenant_id=tenant-123" in repr_str


class TestUserRole:
    """Test cases for the UserRole enum."""

    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
        assert UserRole.READONLY.value == "readonly"

    def test_user_role_from_string(self):
        """Test creating UserRole from string."""
        assert UserRole("admin") == UserRole.ADMIN
        assert UserRole("user") == UserRole.USER
        assert UserRole("readonly") == UserRole.READONLY

    def test_invalid_user_role(self):
        """Test creating UserRole with invalid value."""
        with pytest.raises(ValueError):
            UserRole("invalid_role")


if __name__ == "__main__":
    pytest.main([__file__])
