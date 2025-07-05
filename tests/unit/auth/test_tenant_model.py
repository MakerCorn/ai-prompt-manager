"""
Unit tests for the Tenant model.

This module tests the Tenant entity model including validation,
business logic, metadata operations, and serialization.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from src.auth.models.tenant import Tenant


class TestTenantModel:
    """Test cases for the Tenant model."""

    def test_tenant_creation_with_required_fields(self):
        """Test creating a tenant with only required fields."""
        tenant = Tenant(name="Test Organization", subdomain="testorg")

        assert tenant.name == "Test Organization"
        assert tenant.subdomain == "testorg"
        assert tenant.max_users == 100
        assert tenant.is_active is True
        assert tenant.id is None
        assert isinstance(tenant.created_at, datetime)
        assert isinstance(tenant.updated_at, datetime)
        assert tenant.settings == {}
        assert tenant.metadata == {}

    def test_tenant_creation_with_all_fields(self):
        """Test creating a tenant with all fields."""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        settings = {"feature_flags": {"new_ui": True}}
        metadata = {"plan": "enterprise", "billing_id": "bill_123"}

        tenant = Tenant(
            id="tenant-123",
            name="Full Organization",
            subdomain="fullorg",
            max_users=500,
            is_active=True,
            created_at=created_at,
            updated_at=updated_at,
            settings=settings,
            metadata=metadata,
        )

        assert tenant.id == "tenant-123"
        assert tenant.name == "Full Organization"
        assert tenant.subdomain == "fullorg"
        assert tenant.max_users == 500
        assert tenant.is_active is True
        assert tenant.created_at == created_at
        assert tenant.updated_at == updated_at
        assert tenant.settings == settings
        assert tenant.metadata == metadata

    def test_tenant_post_init_sets_timestamps(self):
        """Test that __post_init__ sets default timestamps."""
        with patch("src.auth.models.tenant.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            tenant = Tenant(name="Test Organization", subdomain="testorg")

            assert tenant.created_at == mock_now
            assert tenant.updated_at == mock_now

    def test_tenant_post_init_preserves_existing_timestamps(self):
        """Test that __post_init__ preserves existing timestamps."""
        created_at = datetime(2023, 1, 1, 10, 0, 0)
        updated_at = datetime(2023, 1, 1, 11, 0, 0)

        tenant = Tenant(
            name="Test Organization",
            subdomain="testorg",
            created_at=created_at,
            updated_at=updated_at,
        )

        assert tenant.created_at == created_at
        assert tenant.updated_at == updated_at

    def test_subdomain_validation_empty(self):
        """Test subdomain validation fails with empty subdomain."""
        with pytest.raises(ValueError) as exc_info:
            Tenant(name="Test Organization", subdomain="")

        assert "Subdomain cannot be empty" in str(exc_info.value)

    def test_subdomain_validation_invalid_characters(self):
        """Test subdomain validation fails with invalid characters."""
        invalid_subdomains = [
            "test@org",
            "test.org",
            "test org",
            "test_org",
            "test!org",
        ]

        for subdomain in invalid_subdomains:
            with pytest.raises(ValueError) as exc_info:
                Tenant(name="Test Organization", subdomain=subdomain)

            assert "can only contain letters, numbers, and hyphens" in str(
                exc_info.value
            )

    def test_subdomain_validation_hyphen_boundaries(self):
        """Test subdomain validation fails when starting/ending with hyphen."""
        invalid_subdomains = ["-testorg", "testorg-"]

        for subdomain in invalid_subdomains:
            with pytest.raises(ValueError) as exc_info:
                Tenant(name="Test Organization", subdomain=subdomain)

            assert "cannot start or end with hyphen" in str(exc_info.value)

    def test_subdomain_validation_length_constraints(self):
        """Test subdomain validation length constraints."""
        # Too short
        with pytest.raises(ValueError) as exc_info:
            Tenant(name="Test Organization", subdomain="a")

        assert "must be at least 2 characters long" in str(exc_info.value)

        # Too long
        with pytest.raises(ValueError) as exc_info:
            Tenant(name="Test Organization", subdomain="a" * 64)

        assert "must be no more than 63 characters long" in str(exc_info.value)

    def test_subdomain_validation_valid_formats(self):
        """Test subdomain validation passes with valid formats."""
        valid_subdomains = [
            "testorg",
            "test-org",
            "test123",
            "123test",
            "t3st-0rg",
            "ab",  # Minimum length
            "a" * 63,  # Maximum length
        ]

        for subdomain in valid_subdomains:
            # Should not raise exception
            tenant = Tenant(name="Test Organization", subdomain=subdomain)
            assert tenant.subdomain == subdomain

    def test_is_default_tenant_property(self):
        """Test is_default_tenant property."""
        # Default tenant
        default_tenant = Tenant(name="Default Tenant", subdomain="localhost")
        assert default_tenant.is_default_tenant is True

        # Non-default tenant
        regular_tenant = Tenant(name="Test Organization", subdomain="testorg")
        assert regular_tenant.is_default_tenant is False

    def test_user_limit_reached_property(self):
        """Test user_limit_reached property (placeholder implementation)."""
        tenant = Tenant(name="Test Organization", subdomain="testorg", max_users=100)

        # Currently returns False as placeholder
        assert tenant.user_limit_reached is False

    def test_get_setting_method(self):
        """Test get_setting method."""
        tenant = Tenant(
            name="Test Organization",
            subdomain="testorg",
            settings={"feature_flags": {"new_ui": True}, "max_api_calls": 1000},
        )

        # Existing setting
        assert tenant.get_setting("max_api_calls") == 1000
        assert tenant.get_setting("feature_flags") == {"new_ui": True}

        # Non-existent setting with default
        assert tenant.get_setting("nonexistent") is None
        assert tenant.get_setting("nonexistent", "default_value") == "default_value"

    def test_set_setting_method(self):
        """Test set_setting method."""
        tenant = Tenant(name="Test Organization", subdomain="testorg")

        original_updated_at = tenant.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        tenant.set_setting("new_feature", True)

        assert tenant.settings["new_feature"] is True
        assert tenant.updated_at is not None and original_updated_at is not None
        assert tenant.updated_at > original_updated_at

        # Update existing setting
        tenant.set_setting("new_feature", False)
        assert tenant.settings["new_feature"] is False

    def test_get_metadata_method(self):
        """Test get_metadata method."""
        tenant = Tenant(
            name="Test Organization",
            subdomain="testorg",
            metadata={"plan": "enterprise", "billing_id": "bill_123"},
        )

        # Existing metadata
        assert tenant.get_metadata("plan") == "enterprise"
        assert tenant.get_metadata("billing_id") == "bill_123"

        # Non-existent metadata with default
        assert tenant.get_metadata("nonexistent") is None
        assert tenant.get_metadata("nonexistent", "default_value") == "default_value"

    def test_set_metadata_method(self):
        """Test set_metadata method."""
        tenant = Tenant(name="Test Organization", subdomain="testorg")

        original_updated_at = tenant.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        tenant.set_metadata("plan", "enterprise")

        assert tenant.metadata["plan"] == "enterprise"
        assert tenant.updated_at is not None and original_updated_at is not None
        assert tenant.updated_at > original_updated_at

        # Update existing metadata
        tenant.set_metadata("plan", "professional")
        assert tenant.metadata["plan"] == "professional"

    def test_can_add_user_method(self):
        """Test can_add_user method."""
        # Active tenant should be able to add users
        active_tenant = Tenant(name="Active Tenant", subdomain="active", is_active=True)
        assert active_tenant.can_add_user() is True

        # Inactive tenant should not be able to add users
        inactive_tenant = Tenant(
            name="Inactive Tenant", subdomain="inactive", is_active=False
        )
        assert inactive_tenant.can_add_user() is False

    def test_to_dict_method(self):
        """Test to_dict method."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 1, 13, 0, 0)
        settings = {"feature_flags": {"new_ui": True}}
        metadata = {"plan": "enterprise"}

        tenant = Tenant(
            id="tenant-123",
            name="Test Organization",
            subdomain="testorg",
            max_users=500,
            is_active=True,
            created_at=created_at,
            updated_at=updated_at,
            settings=settings,
            metadata=metadata,
        )

        tenant_dict = tenant.to_dict()

        assert tenant_dict == {
            "id": "tenant-123",
            "name": "Test Organization",
            "subdomain": "testorg",
            "max_users": 500,
            "is_active": True,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "settings": settings,
            "metadata": metadata,
        }

    def test_to_dict_method_with_none_timestamps(self):
        """Test to_dict method with None timestamps."""
        tenant = Tenant(name="Test Organization", subdomain="testorg")

        # Manually set timestamps to None to test edge case
        tenant.created_at = None
        tenant.updated_at = None

        tenant_dict = tenant.to_dict()

        assert tenant_dict["created_at"] is None
        assert tenant_dict["updated_at"] is None

    def test_from_dict_method(self):
        """Test from_dict method."""
        tenant_data = {
            "id": "tenant-123",
            "name": "Dictionary Tenant",
            "subdomain": "dictorg",
            "max_users": 250,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T13:00:00",
            "settings": {"feature_flags": {"new_ui": True}},
            "metadata": {"plan": "professional"},
        }

        tenant = Tenant.from_dict(tenant_data)

        assert tenant.id == "tenant-123"
        assert tenant.name == "Dictionary Tenant"
        assert tenant.subdomain == "dictorg"
        assert tenant.max_users == 250
        assert tenant.is_active is True
        assert isinstance(tenant.created_at, datetime)
        assert isinstance(tenant.updated_at, datetime)
        assert tenant.settings == {"feature_flags": {"new_ui": True}}
        assert tenant.metadata == {"plan": "professional"}

    def test_from_dict_method_with_datetime_objects(self):
        """Test from_dict method with datetime objects."""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        tenant_data = {
            "name": "DateTime Tenant",
            "subdomain": "dtorg",
            "created_at": created_at,
            "updated_at": updated_at,
        }

        tenant = Tenant.from_dict(tenant_data)

        assert tenant.created_at == created_at
        assert tenant.updated_at == updated_at

    def test_from_dict_method_with_iso_format_z_suffix(self):
        """Test from_dict method with ISO format Z suffix."""
        tenant_data = {
            "name": "ISO Tenant",
            "subdomain": "isoorg",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T13:00:00Z",
        }

        tenant = Tenant.from_dict(tenant_data)

        assert isinstance(tenant.created_at, datetime)
        assert isinstance(tenant.updated_at, datetime)

    def test_from_dict_method_minimal_data(self):
        """Test from_dict method with minimal data."""
        tenant_data = {"name": "Minimal Tenant", "subdomain": "minimal"}

        tenant = Tenant.from_dict(tenant_data)

        assert tenant.name == "Minimal Tenant"
        assert tenant.subdomain == "minimal"
        assert tenant.max_users == 100  # Default value
        assert tenant.is_active is True  # Default value
        assert tenant.settings == {}  # Default value
        assert tenant.metadata == {}  # Default value
        assert tenant.id is None

    def test_create_default_tenant_method(self):
        """Test create_default_tenant class method."""
        default_tenant = Tenant.create_default_tenant()

        assert default_tenant.name == "Default Tenant"
        assert default_tenant.subdomain == "localhost"
        assert default_tenant.max_users == 1000
        assert default_tenant.is_active is True
        assert default_tenant.is_default_tenant is True
        assert isinstance(default_tenant.created_at, datetime)
        assert isinstance(default_tenant.updated_at, datetime)

    def test_string_representations(self):
        """Test string representation methods."""
        tenant = Tenant(
            id="tenant-123",
            name="Test Organization",
            subdomain="testorg",
            max_users=500,
            is_active=True,
        )

        str_repr = str(tenant)
        assert "Test Organization" in str_repr
        assert "testorg" in str_repr

        repr_str = repr(tenant)
        assert "tenant-123" in repr_str
        assert "Test Organization" in repr_str
        assert "testorg" in repr_str
        assert "max_users=500" in repr_str
        assert "is_active=True" in repr_str

    def test_edge_cases_subdomain_validation(self):
        """Test edge cases in subdomain validation."""
        # Valid edge cases
        valid_cases = [
            "a0",  # Minimum with number
            "0a",  # Starting with number
            "test-123-org",  # Multiple hyphens
            "123-456-789",  # All numbers with hyphens
        ]

        for subdomain in valid_cases:
            tenant = Tenant(name="Edge Case Tenant", subdomain=subdomain)
            assert tenant.subdomain == subdomain

    def test_settings_and_metadata_independence(self):
        """Test that settings and metadata are independent."""
        tenant = Tenant(name="Test Organization", subdomain="testorg")

        # Set both settings and metadata with same key
        tenant.set_setting("key", "setting_value")
        tenant.set_metadata("key", "metadata_value")

        assert tenant.get_setting("key") == "setting_value"
        assert tenant.get_metadata("key") == "metadata_value"

        # Verify they don't interfere with each other
        assert tenant.settings["key"] == "setting_value"
        assert tenant.metadata["key"] == "metadata_value"
        assert len(tenant.settings) == 1
        assert len(tenant.metadata) == 1

    def test_tenant_field_defaults(self):
        """Test tenant field defaults."""
        tenant = Tenant(name="Default Test", subdomain="default")

        # Check all default values
        assert tenant.id is None
        assert tenant.max_users == 100
        assert tenant.is_active is True
        assert isinstance(tenant.created_at, datetime)
        assert isinstance(tenant.updated_at, datetime)
        assert isinstance(tenant.settings, dict)
        assert isinstance(tenant.metadata, dict)
        assert len(tenant.settings) == 0
        assert len(tenant.metadata) == 0


class TestTenantModelValidation:
    """Test cases for Tenant model validation edge cases."""

    def test_name_validation_edge_cases(self):
        """Test name field edge cases."""
        # Empty name should be allowed (no validation currently)
        tenant = Tenant(name="", subdomain="empty-name")
        assert tenant.name == ""

        # Very long name should be allowed (no validation currently)
        long_name = "A" * 1000
        tenant = Tenant(name=long_name, subdomain="long-name")
        assert tenant.name == long_name

    def test_max_users_edge_cases(self):
        """Test max_users field edge cases."""
        # Zero users
        tenant = Tenant(name="Zero Users", subdomain="zero", max_users=0)
        assert tenant.max_users == 0

        # Negative users (allowed, no validation)
        tenant = Tenant(name="Negative Users", subdomain="negative", max_users=-1)
        assert tenant.max_users == -1

        # Very large number
        tenant = Tenant(name="Many Users", subdomain="many", max_users=1000000)
        assert tenant.max_users == 1000000

    def test_from_dict_error_handling(self):
        """Test from_dict method error handling."""
        # Missing required fields
        with pytest.raises(KeyError):
            Tenant.from_dict({"name": "Missing Subdomain"})

        with pytest.raises(KeyError):
            Tenant.from_dict({"subdomain": "missing-name"})

        # Invalid datetime format (should be handled gracefully)
        tenant_data = {
            "name": "Invalid DateTime",
            "subdomain": "invalid",
            "created_at": "not-a-datetime",
        }

        # Should raise an exception due to invalid datetime format
        with pytest.raises(ValueError):
            Tenant.from_dict(tenant_data)


if __name__ == "__main__":
    pytest.main([__file__])
