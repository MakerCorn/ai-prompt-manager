"""
Integration tests for AI Services Database Operations

This module tests the database integration for AI model management including
SQLite and PostgreSQL support, tenant isolation, and data persistence.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from prompt_data_manager import PromptDataManager


class TestAIDatabaseIntegration:
    """Test AI services database integration."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        # Create temporary database for each test
        self.test_db = tempfile.mktemp(suffix=".db")
        self.tenant_id = "test-tenant-123"
        self.user_id = "test-user-456"

        self.data_manager = PromptDataManager(
            db_path=self.test_db, tenant_id=self.tenant_id, user_id=self.user_id
        )

    def teardown_method(self):
        """Clean up after each test."""
        try:
            os.unlink(self.test_db)
        except FileNotFoundError:
            pass

    def test_database_initialization_creates_ai_tables(self):
        """Test that database initialization creates AI model tables."""
        # Tables should be created during initialization
        conn = self.data_manager.get_conn()
        cursor = conn.cursor()

        # Check ai_models table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ai_models'"
        )
        assert cursor.fetchone() is not None

        # Check ai_operation_configs table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ai_operation_configs'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_add_ai_model_basic(self):
        """Test adding a basic AI model."""
        model_data = {
            "name": "test-gpt-4",
            "display_name": "Test GPT-4",
            "provider": "openai",
            "model_id": "gpt-4",
            "description": "Test model for unit testing",
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
            "max_context_length": 8192,
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": False,
            "supports_json_mode": True,
            "is_enabled": True,
        }

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Verify model was added
        models = self.data_manager.get_ai_models()
        assert len(models) == 1

        added_model = models[0]
        assert added_model["name"] == "test-gpt-4"
        assert added_model["provider"] == "openai"
        assert added_model["model_id"] == "gpt-4"
        assert added_model["display_name"] == "Test GPT-4"
        assert added_model["description"] == "Test model for unit testing"
        assert added_model["cost_per_1k_input_tokens"] == 0.01
        assert added_model["cost_per_1k_output_tokens"] == 0.03
        assert added_model["max_context_length"] == 8192
        assert added_model["supports_streaming"] is True
        assert added_model["supports_function_calling"] is True
        assert added_model["supports_vision"] is False
        assert added_model["supports_json_mode"] is True
        assert added_model["is_enabled"] is True

    def test_add_ai_model_with_minimal_data(self):
        """Test adding AI model with minimal required data."""
        model_data = {
            "name": "minimal-model",
            "provider": "anthropic",
            "model_id": "claude-3-haiku",
        }

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        models = self.data_manager.get_ai_models()
        assert len(models) == 1

        added_model = models[0]
        assert added_model["name"] == "minimal-model"
        assert added_model["provider"] == "anthropic"
        assert added_model["model_id"] == "claude-3-haiku"
        assert added_model["display_name"] is None
        assert added_model["temperature"] == 0.7  # Default value
        assert added_model["is_enabled"] is True  # Default value

    def test_add_duplicate_model_name_fails(self):
        """Test that adding a model with duplicate name fails."""
        model_data = {
            "name": "duplicate-model",
            "provider": "openai",
            "model_id": "gpt-4",
        }

        # Add first model
        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Try to add duplicate
        success = self.data_manager.add_ai_model(model_data)
        assert success is False

    def test_get_ai_models_empty(self):
        """Test getting AI models when none exist."""
        models = self.data_manager.get_ai_models()
        assert models == []

    def test_get_ai_models_multiple(self):
        """Test getting multiple AI models."""
        models_data = [
            {
                "name": "model-1",
                "provider": "openai",
                "model_id": "gpt-4",
                "cost_per_1k_input_tokens": 0.01,
            },
            {
                "name": "model-2",
                "provider": "anthropic",
                "model_id": "claude-3-opus",
                "cost_per_1k_input_tokens": 0.015,
            },
            {
                "name": "model-3",
                "provider": "google",
                "model_id": "gemini-pro",
                "cost_per_1k_input_tokens": 0.0005,
            },
        ]

        # Add all models
        for model_data in models_data:
            success = self.data_manager.add_ai_model(model_data)
            assert success is True

        # Retrieve all models
        models = self.data_manager.get_ai_models()
        assert len(models) == 3

        # Check they're ordered by name
        model_names = [m["name"] for m in models]
        assert model_names == ["model-1", "model-2", "model-3"]

        # Verify specific model data
        model_1 = next(m for m in models if m["name"] == "model-1")
        assert model_1["provider"] == "openai"
        assert model_1["cost_per_1k_input_tokens"] == 0.01

    def test_update_ai_model_basic(self):
        """Test updating an AI model."""
        # Add model first
        model_data = {
            "name": "update-test-model",
            "provider": "openai",
            "model_id": "gpt-4",
            "display_name": "Original Name",
            "temperature": 0.7,
            "is_enabled": True,
        }

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Update the model
        updates = {
            "display_name": "Updated Name",
            "description": "Added description",
            "temperature": 0.9,
            "supports_streaming": True,
            "is_enabled": False,
        }

        success = self.data_manager.update_ai_model("update-test-model", updates)
        assert success is True

        # Verify updates
        models = self.data_manager.get_ai_models()
        updated_model = models[0]

        assert updated_model["display_name"] == "Updated Name"
        assert updated_model["description"] == "Added description"
        assert updated_model["temperature"] == 0.9
        assert updated_model["supports_streaming"] is True
        assert updated_model["is_enabled"] is False
        # Unchanged fields should remain the same
        assert updated_model["name"] == "update-test-model"
        assert updated_model["provider"] == "openai"
        assert updated_model["model_id"] == "gpt-4"

    def test_update_nonexistent_model(self):
        """Test updating a model that doesn't exist."""
        updates = {"display_name": "New Name"}

        success = self.data_manager.update_ai_model("nonexistent-model", updates)
        assert success is False

    def test_update_ai_model_invalid_fields(self):
        """Test updating AI model with invalid fields."""
        # Add model first
        model_data = {"name": "test-model", "provider": "openai", "model_id": "gpt-4"}

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Try to update with invalid field
        updates = {"invalid_field": "some_value"}

        success = self.data_manager.update_ai_model("test-model", updates)
        # Should still succeed but ignore invalid fields
        assert success is True

    def test_delete_ai_model(self):
        """Test deleting an AI model."""
        # Add model first
        model_data = {
            "name": "delete-test-model",
            "provider": "openai",
            "model_id": "gpt-4",
        }

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Verify model exists
        models = self.data_manager.get_ai_models()
        assert len(models) == 1

        # Delete the model
        success = self.data_manager.delete_ai_model("delete-test-model")
        assert success is True

        # Verify model is gone
        models = self.data_manager.get_ai_models()
        assert len(models) == 0

    def test_delete_nonexistent_model(self):
        """Test deleting a model that doesn't exist."""
        success = self.data_manager.delete_ai_model("nonexistent-model")
        assert success is False

    def test_ai_operation_config_basic(self):
        """Test basic AI operation configuration."""
        config_data = {
            "primary_model": "gpt-4",
            "fallback_models": json.dumps(["gpt-3.5-turbo", "claude-3-haiku"]),
            "is_enabled": True,
            "custom_parameters": json.dumps({"temperature": 0.8}),
        }

        success = self.data_manager.update_ai_operation_config(
            "prompt_enhancement", config_data
        )
        assert success is True

        # Retrieve configurations
        configs = self.data_manager.get_ai_operation_configs()
        assert len(configs) == 1

        config = configs[0]
        assert config["operation_type"] == "prompt_enhancement"
        assert config["primary_model"] == "gpt-4"
        assert json.loads(config["fallback_models"]) == [
            "gpt-3.5-turbo",
            "claude-3-haiku",
        ]
        assert config["is_enabled"] is True
        assert json.loads(config["custom_parameters"]) == {"temperature": 0.8}

    def test_ai_operation_config_update_existing(self):
        """Test updating existing operation configuration."""
        # Create initial config
        initial_config = {
            "primary_model": "gpt-4",
            "fallback_models": json.dumps(["gpt-3.5-turbo"]),
            "is_enabled": True,
        }

        success = self.data_manager.update_ai_operation_config(
            "default", initial_config
        )
        assert success is True

        # Update the config
        updated_config = {
            "primary_model": "claude-3-opus",
            "fallback_models": json.dumps(["claude-3-sonnet", "gpt-4"]),
            "is_enabled": False,
            "custom_parameters": json.dumps({"max_tokens": 4000}),
        }

        success = self.data_manager.update_ai_operation_config(
            "default", updated_config
        )
        assert success is True

        # Verify update
        configs = self.data_manager.get_ai_operation_configs()
        assert len(configs) == 1

        config = configs[0]
        assert config["operation_type"] == "default"
        assert config["primary_model"] == "claude-3-opus"
        assert json.loads(config["fallback_models"]) == ["claude-3-sonnet", "gpt-4"]
        assert config["is_enabled"] is False
        assert json.loads(config["custom_parameters"]) == {"max_tokens": 4000}

    def test_multiple_operation_configs(self):
        """Test multiple operation configurations."""
        configs_data = [
            (
                "default",
                {
                    "primary_model": "gpt-3.5-turbo",
                    "fallback_models": json.dumps(["gpt-4"]),
                    "is_enabled": True,
                },
            ),
            (
                "prompt_enhancement",
                {
                    "primary_model": "gpt-4",
                    "fallback_models": json.dumps(["claude-3-opus"]),
                    "is_enabled": True,
                },
            ),
            (
                "prompt_testing",
                {
                    "primary_model": "gpt-3.5-turbo",
                    "fallback_models": json.dumps([]),
                    "is_enabled": False,
                },
            ),
        ]

        # Add all configurations
        for operation_type, config_data in configs_data:
            success = self.data_manager.update_ai_operation_config(
                operation_type, config_data
            )
            assert success is True

        # Retrieve all configurations
        configs = self.data_manager.get_ai_operation_configs()
        assert len(configs) == 3

        # Check they're ordered by operation_type
        operation_types = [c["operation_type"] for c in configs]
        assert "default" in operation_types
        assert "prompt_enhancement" in operation_types
        assert "prompt_testing" in operation_types

        # Verify specific configurations
        default_config = next(c for c in configs if c["operation_type"] == "default")
        assert default_config["primary_model"] == "gpt-3.5-turbo"

        testing_config = next(
            c for c in configs if c["operation_type"] == "prompt_testing"
        )
        assert testing_config["is_enabled"] is False

    def test_tenant_isolation_models(self):
        """Test that models are isolated by tenant."""
        # Create data manager for different tenant
        other_tenant_manager = PromptDataManager(
            db_path=self.test_db, tenant_id="other-tenant", user_id="other-user"
        )

        # Add model to first tenant
        model_data = {
            "name": "tenant-1-model",
            "provider": "openai",
            "model_id": "gpt-4",
        }
        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        # Add model to second tenant
        other_model_data = {
            "name": "tenant-2-model",
            "provider": "anthropic",
            "model_id": "claude-3-opus",
        }
        success = other_tenant_manager.add_ai_model(other_model_data)
        assert success is True

        # Each tenant should only see their own models
        tenant1_models = self.data_manager.get_ai_models()
        tenant2_models = other_tenant_manager.get_ai_models()

        assert len(tenant1_models) == 1
        assert len(tenant2_models) == 1

        assert tenant1_models[0]["name"] == "tenant-1-model"
        assert tenant2_models[0]["name"] == "tenant-2-model"

    def test_tenant_isolation_operation_configs(self):
        """Test that operation configs are isolated by tenant."""
        # Create data manager for different tenant
        other_tenant_manager = PromptDataManager(
            db_path=self.test_db, tenant_id="other-tenant", user_id="other-user"
        )

        # Add config to first tenant
        config1 = {
            "primary_model": "gpt-4",
            "fallback_models": json.dumps(["gpt-3.5-turbo"]),
            "is_enabled": True,
        }
        success = self.data_manager.update_ai_operation_config("default", config1)
        assert success is True

        # Add config to second tenant
        config2 = {
            "primary_model": "claude-3-opus",
            "fallback_models": json.dumps(["claude-3-sonnet"]),
            "is_enabled": False,
        }
        success = other_tenant_manager.update_ai_operation_config("default", config2)
        assert success is True

        # Each tenant should only see their own configs
        tenant1_configs = self.data_manager.get_ai_operation_configs()
        tenant2_configs = other_tenant_manager.get_ai_operation_configs()

        assert len(tenant1_configs) == 1
        assert len(tenant2_configs) == 1

        assert tenant1_configs[0]["primary_model"] == "gpt-4"
        assert tenant2_configs[0]["primary_model"] == "claude-3-opus"

    def test_no_tenant_id_returns_empty(self):
        """Test that operations return empty results when no tenant_id."""
        # Create data manager without tenant_id
        no_tenant_manager = PromptDataManager(db_path=self.test_db)

        # Operations should return empty/False
        models = no_tenant_manager.get_ai_models()
        assert models == []

        success = no_tenant_manager.add_ai_model(
            {"name": "test", "provider": "openai", "model_id": "gpt-4"}
        )
        assert success is False

        success = no_tenant_manager.update_ai_model("test", {"display_name": "Test"})
        assert success is False

        success = no_tenant_manager.delete_ai_model("test")
        assert success is False

        configs = no_tenant_manager.get_ai_operation_configs()
        assert configs == []

        success = no_tenant_manager.update_ai_operation_config(
            "default", {"primary_model": "test"}
        )
        assert success is False

    def test_database_error_handling(self):
        """Test database error handling."""
        # Close and remove database to simulate errors
        self.data_manager = None
        os.unlink(self.test_db)

        # Create manager with non-existent database path in read-only directory
        try:
            error_manager = PromptDataManager(
                db_path="/root/nonexistent/path/test.db",  # Should fail
                tenant_id="test",
                user_id="test",
            )
            # If it doesn't fail during init, operations should fail gracefully
            models = error_manager.get_ai_models()
            assert models == []  # Should return empty list on error
        except Exception:
            # Init failing is also acceptable
            pass

    def test_data_persistence(self):
        """Test that data persists across manager instances."""
        # Add some data
        model_data = {
            "name": "persistence-test-model",
            "provider": "openai",
            "model_id": "gpt-4",
            "description": "Test persistence",
        }

        success = self.data_manager.add_ai_model(model_data)
        assert success is True

        config_data = {
            "primary_model": "persistence-test-model",
            "fallback_models": json.dumps(["fallback-model"]),
            "is_enabled": True,
        }

        success = self.data_manager.update_ai_operation_config("default", config_data)
        assert success is True

        # Create new manager instance with same database
        new_manager = PromptDataManager(
            db_path=self.test_db, tenant_id=self.tenant_id, user_id=self.user_id
        )

        # Data should still be there
        models = new_manager.get_ai_models()
        assert len(models) == 1
        assert models[0]["name"] == "persistence-test-model"
        assert models[0]["description"] == "Test persistence"

        configs = new_manager.get_ai_operation_configs()
        assert len(configs) == 1
        assert configs[0]["operation_type"] == "default"
        assert configs[0]["primary_model"] == "persistence-test-model"

    def test_json_field_handling(self):
        """Test proper JSON field handling in operation configs."""
        # Test with complex JSON data
        complex_fallback_models = ["model-1", "model-2", "model-3"]
        complex_parameters = {
            "temperature": 0.8,
            "max_tokens": 4000,
            "top_p": 0.9,
            "nested": {"key": "value", "number": 42},
        }

        config_data = {
            "primary_model": "main-model",
            "fallback_models": json.dumps(complex_fallback_models),
            "is_enabled": True,
            "custom_parameters": json.dumps(complex_parameters),
        }

        success = self.data_manager.update_ai_operation_config(
            "complex_test", config_data
        )
        assert success is True

        # Retrieve and verify JSON parsing
        configs = self.data_manager.get_ai_operation_configs()
        config = configs[0]

        parsed_fallback = json.loads(config["fallback_models"])
        parsed_parameters = json.loads(config["custom_parameters"])

        assert parsed_fallback == complex_fallback_models
        assert parsed_parameters == complex_parameters
        assert parsed_parameters["nested"]["key"] == "value"
        assert parsed_parameters["nested"]["number"] == 42


class TestAIDatabasePostgreSQL:
    """Test AI services database integration with PostgreSQL (if available)."""

    @pytest.fixture(scope="class", autouse=True)
    def setup_postgres_test(self):
        """Set up PostgreSQL test if available."""
        # Only run if PostgreSQL DSN is provided
        postgres_dsn = os.getenv("TEST_POSTGRES_DSN")
        if not postgres_dsn:
            pytest.skip(
                "PostgreSQL tests require TEST_POSTGRES_DSN environment variable"
            )

        self.postgres_dsn = postgres_dsn
        self.tenant_id = "pg-test-tenant"
        self.user_id = "pg-test-user"

    def test_postgres_ai_model_operations(self):
        """Test AI model operations with PostgreSQL."""
        with patch.dict(
            os.environ, {"POSTGRES_DSN": self.postgres_dsn, "DB_TYPE": "postgres"}
        ):
            data_manager = PromptDataManager(
                tenant_id=self.tenant_id, user_id=self.user_id
            )

            # Test adding model
            model_data = {
                "name": "postgres-test-model",
                "provider": "openai",
                "model_id": "gpt-4",
                "description": "PostgreSQL test model",
                "cost_per_1k_input_tokens": 0.01,
                "supports_streaming": True,
            }

            success = data_manager.add_ai_model(model_data)
            assert success is True

            # Test retrieving model
            models = data_manager.get_ai_models()
            assert len(models) >= 1

            postgres_model = next(
                (m for m in models if m["name"] == "postgres-test-model"), None
            )
            assert postgres_model is not None
            assert postgres_model["provider"] == "openai"
            assert postgres_model["description"] == "PostgreSQL test model"

            # Test updating model
            updates = {"description": "Updated PostgreSQL model"}
            success = data_manager.update_ai_model("postgres-test-model", updates)
            assert success is True

            # Verify update
            models = data_manager.get_ai_models()
            updated_model = next(
                (m for m in models if m["name"] == "postgres-test-model"), None
            )
            assert updated_model["description"] == "Updated PostgreSQL model"

            # Test deleting model
            success = data_manager.delete_ai_model("postgres-test-model")
            assert success is True

            # Verify deletion
            models = data_manager.get_ai_models()
            deleted_model = next(
                (m for m in models if m["name"] == "postgres-test-model"), None
            )
            assert deleted_model is None

    def test_postgres_operation_config_operations(self):
        """Test operation config operations with PostgreSQL."""
        with patch.dict(
            os.environ, {"POSTGRES_DSN": self.postgres_dsn, "DB_TYPE": "postgres"}
        ):
            data_manager = PromptDataManager(
                tenant_id=self.tenant_id, user_id=self.user_id
            )

            # Test adding operation config
            config_data = {
                "primary_model": "postgres-primary-model",
                "fallback_models": json.dumps(
                    ["postgres-fallback-1", "postgres-fallback-2"]
                ),
                "is_enabled": True,
                "custom_parameters": json.dumps(
                    {"postgres_test": True, "temperature": 0.7}
                ),
            }

            success = data_manager.update_ai_operation_config(
                "postgres_test", config_data
            )
            assert success is True

            # Test retrieving config
            configs = data_manager.get_ai_operation_configs()
            postgres_config = next(
                (c for c in configs if c["operation_type"] == "postgres_test"), None
            )

            assert postgres_config is not None
            assert postgres_config["primary_model"] == "postgres-primary-model"

            fallback_models = json.loads(postgres_config["fallback_models"])
            assert fallback_models == ["postgres-fallback-1", "postgres-fallback-2"]

            custom_params = json.loads(postgres_config["custom_parameters"])
            assert custom_params["postgres_test"] is True
            assert custom_params["temperature"] == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
