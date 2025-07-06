"""
Integration tests for Enhanced AI Services API

This module tests the complete API functionality including database integration,
authentication, and multi-tenant support.
"""

import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from prompt_data_manager import PromptDataManager
from web_app import WebApp


class TestAIServicesAPIIntegration:
    """Test AI Services API integration."""

    @pytest.fixture(scope="class")
    def setup_test_app(self):
        """Set up test application with temporary database."""
        # Create temporary database
        self.test_db = tempfile.mktemp(suffix=".db")

        # Set environment variables
        os.environ["DB_PATH"] = self.test_db
        os.environ["SECRET_KEY"] = "test-secret-key-for-integration-tests"
        os.environ["MULTITENANT_MODE"] = "false"  # Single-user mode for testing

        # Create web app
        self.app = WebApp()
        self.client = TestClient(self.app.app)

        # Initialize test data
        self.data_manager = PromptDataManager(
            db_path=self.test_db, tenant_id="single-user", user_id="single-user"
        )

        yield self.client

        # Cleanup
        try:
            os.unlink(self.test_db)
        except FileNotFoundError:
            pass

    def test_get_providers_endpoint(self, setup_test_app):
        """Test GET /api/ai-models/providers endpoint."""
        client = setup_test_app

        response = client.get("/api/ai-models/providers")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "providers" in data

        providers = data["providers"]
        assert len(providers) > 0

        # Check for expected providers
        provider_ids = [p["id"] for p in providers]
        assert "openai" in provider_ids
        assert "azure_openai" in provider_ids
        assert "anthropic" in provider_ids

        # Check provider structure
        openai_provider = next(p for p in providers if p["id"] == "openai")
        assert "name" in openai_provider
        assert "supported_features" in openai_provider
        assert "configuration_fields" in openai_provider
        assert "api_key" in openai_provider["configuration_fields"]

    def test_get_operation_types_endpoint(self, setup_test_app):
        """Test GET /api/ai-models/operation-types endpoint."""
        client = setup_test_app

        response = client.get("/api/ai-models/operation-types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "operation_types" in data

        operation_types = data["operation_types"]
        assert len(operation_types) > 0

        # Check for expected operation types
        op_ids = [op["id"] for op in operation_types]
        assert "default" in op_ids
        assert "prompt_enhancement" in op_ids
        assert "prompt_optimization" in op_ids

        # Check operation structure
        default_op = next(op for op in operation_types if op["id"] == "default")
        assert "name" in default_op
        assert "description" in default_op

    def test_get_models_empty_initially(self, setup_test_app):
        """Test GET /api/ai-models/ returns empty list initially."""
        client = setup_test_app

        response = client.get("/api/ai-models/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["models"] == []
        assert data["count"] == 0

    def test_add_model_complete_workflow(self, setup_test_app):
        """Test complete model addition workflow."""
        client = setup_test_app

        # Test adding a model
        model_data = {
            "name": "test-gpt-4",
            "display_name": "Test GPT-4",
            "provider": "openai",
            "model_id": "gpt-4",
            "description": "Test model for integration testing",
            "api_key": "test-api-key",
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
            "max_context_length": 8192,
            "supports_streaming": True,
            "supports_function_calling": True,
            "is_enabled": True,
        }

        response = client.post("/api/ai-models/", json=model_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Model added successfully" in data["message"]

        # Verify model was added by retrieving it
        response = client.get("/api/ai-models/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1

        added_model = data["models"][0]
        assert added_model["name"] == "test-gpt-4"
        assert added_model["provider"] == "openai"
        assert added_model["model_id"] == "gpt-4"
        assert added_model["display_name"] == "Test GPT-4"
        assert added_model["supports_streaming"] is True

    def test_add_model_invalid_provider(self, setup_test_app):
        """Test adding model with invalid provider."""
        client = setup_test_app

        model_data = {
            "name": "invalid-model",
            "provider": "invalid_provider",
            "model_id": "some-model",
        }

        response = client.post("/api/ai-models/", json=model_data)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid provider" in data["detail"]

    def test_update_model_workflow(self, setup_test_app):
        """Test model update workflow."""
        client = setup_test_app

        # First add a model
        model_data = {
            "name": "update-test-model",
            "provider": "openai",
            "model_id": "gpt-3.5-turbo",
            "temperature": 0.7,
        }

        response = client.post("/api/ai-models/", json=model_data)
        assert response.status_code == 200

        # Update the model
        update_data = {
            "display_name": "Updated Display Name",
            "description": "Updated description",
            "temperature": 0.9,
            "supports_streaming": True,
        }

        response = client.put("/api/ai-models/update-test-model", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Model updated successfully" in data["message"]

        # Verify updates by retrieving the model
        response = client.get("/api/ai-models/")
        data = response.json()

        updated_model = next(
            m for m in data["models"] if m["name"] == "update-test-model"
        )
        assert updated_model["display_name"] == "Updated Display Name"
        assert updated_model["description"] == "Updated description"
        assert updated_model["temperature"] == 0.9
        assert updated_model["supports_streaming"] is True

    def test_update_nonexistent_model(self, setup_test_app):
        """Test updating a model that doesn't exist."""
        client = setup_test_app

        update_data = {"display_name": "Nonexistent Model"}

        response = client.put("/api/ai-models/nonexistent-model", json=update_data)

        assert response.status_code == 404
        data = response.json()
        assert "Model not found" in data["detail"]

    def test_delete_model_workflow(self, setup_test_app):
        """Test model deletion workflow."""
        client = setup_test_app

        # First add a model
        model_data = {
            "name": "delete-test-model",
            "provider": "openai",
            "model_id": "gpt-3.5-turbo",
        }

        response = client.post("/api/ai-models/", json=model_data)
        assert response.status_code == 200

        # Verify model exists
        response = client.get("/api/ai-models/")
        data = response.json()
        model_names = [m["name"] for m in data["models"]]
        assert "delete-test-model" in model_names

        # Delete the model
        response = client.delete("/api/ai-models/delete-test-model")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Model deleted successfully" in data["message"]

        # Verify model was deleted
        response = client.get("/api/ai-models/")
        data = response.json()
        model_names = [m["name"] for m in data["models"]]
        assert "delete-test-model" not in model_names

    def test_delete_nonexistent_model(self, setup_test_app):
        """Test deleting a model that doesn't exist."""
        client = setup_test_app

        response = client.delete("/api/ai-models/nonexistent-model")

        assert response.status_code == 404
        data = response.json()
        assert "Model not found" in data["detail"]

    def test_test_model_endpoint(self, setup_test_app):
        """Test model testing endpoint."""
        client = setup_test_app

        # First add a model
        model_data = {
            "name": "test-model",
            "provider": "google",  # Use Google since it has mock implementation
            "model_id": "gemini-pro",
        }

        response = client.post("/api/ai-models/", json=model_data)
        assert response.status_code == 200

        # Test the model
        test_data = {"test_prompt": "Hello, this is a test prompt."}

        response = client.post("/api/ai-models/test-model/test", json=test_data)

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "status" in data
        assert "response_time" in data
        assert data["model_name"] == "test-model"

    def test_test_nonexistent_model(self, setup_test_app):
        """Test testing a model that doesn't exist."""
        client = setup_test_app

        test_data = {"test_prompt": "Hello"}

        response = client.post("/api/ai-models/nonexistent-model/test", json=test_data)

        assert response.status_code == 404
        data = response.json()
        assert "Model not found" in data["detail"]

    def test_health_check_endpoint(self, setup_test_app):
        """Test health check endpoint."""
        client = setup_test_app

        # Add a test model first
        model_data = {
            "name": "health-test-model",
            "provider": "google",
            "model_id": "gemini-pro",
        }

        response = client.post("/api/ai-models/", json=model_data)
        assert response.status_code == 200

        # Run health checks
        response = client.post("/api/ai-models/health-check")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert "Health checks completed" in data["message"]

    def test_get_operation_configs_endpoint(self, setup_test_app):
        """Test GET /api/ai-models/operations endpoint."""
        client = setup_test_app

        response = client.get("/api/ai-models/operations")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configurations" in data

        configurations = data["configurations"]
        assert len(configurations) > 0

        # Should include all operation types
        op_types = [config["operation_type"] for config in configurations]
        assert "default" in op_types
        assert "prompt_enhancement" in op_types

    def test_update_operation_config_workflow(self, setup_test_app):
        """Test operation configuration update workflow."""
        client = setup_test_app

        # First add some models
        model1_data = {
            "name": "primary-model",
            "provider": "openai",
            "model_id": "gpt-4",
        }
        model2_data = {
            "name": "fallback-model",
            "provider": "openai",
            "model_id": "gpt-3.5-turbo",
        }

        client.post("/api/ai-models/", json=model1_data)
        client.post("/api/ai-models/", json=model2_data)

        # Update operation configuration
        config_data = {
            "primary_model": "primary-model",
            "fallback_models": ["fallback-model"],
            "is_enabled": True,
            "custom_parameters": {"temperature": 0.8},
        }

        response = client.put(
            "/api/ai-models/operations/prompt_enhancement", json=config_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Operation configuration updated successfully" in data["message"]

        # Verify the configuration was updated
        response = client.get("/api/ai-models/operations")
        data = response.json()

        enhancement_config = next(
            config
            for config in data["configurations"]
            if config["operation_type"] == "prompt_enhancement"
        )
        assert enhancement_config["primary_model"] == "primary-model"
        assert json.loads(enhancement_config["fallback_models"]) == ["fallback-model"]

    def test_update_operation_config_invalid_operation(self, setup_test_app):
        """Test updating operation config with invalid operation type."""
        client = setup_test_app

        config_data = {"primary_model": "some-model"}

        response = client.put(
            "/api/ai-models/operations/invalid_operation", json=config_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid operation type" in data["detail"]

    def test_get_model_recommendations_endpoint(self, setup_test_app):
        """Test model recommendations endpoint."""
        client = setup_test_app

        # Add some models with different characteristics
        cheap_model = {
            "name": "cheap-model",
            "provider": "openai",
            "model_id": "gpt-3.5-turbo",
            "cost_per_1k_input_tokens": 0.0005,
            "cost_per_1k_output_tokens": 0.0015,
        }
        expensive_model = {
            "name": "expensive-model",
            "provider": "openai",
            "model_id": "gpt-4",
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
        }

        client.post("/api/ai-models/", json=cheap_model)
        client.post("/api/ai-models/", json=expensive_model)

        # Get recommendations for testing (should prefer cheaper models)
        response = client.get("/api/ai-models/recommendations/prompt_testing")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert data["operation_type"] == "prompt_testing"

        recommendations = data["recommendations"]
        assert len(recommendations) > 0
        assert all(
            "model" in rec and "score" in rec and "reason" in rec
            for rec in recommendations
        )

    def test_get_recommendations_invalid_operation(self, setup_test_app):
        """Test getting recommendations for invalid operation type."""
        client = setup_test_app

        response = client.get("/api/ai-models/recommendations/invalid_operation")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid operation type" in data["detail"]

    def test_get_usage_stats_endpoint(self, setup_test_app):
        """Test usage statistics endpoint."""
        client = setup_test_app

        response = client.get("/api/ai-models/usage-stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stats" in data

        stats = data["stats"]
        assert "total_requests" in stats
        assert "total_tokens" in stats
        assert "total_cost" in stats
        assert "models" in stats

    def test_export_configuration_endpoint(self, setup_test_app):
        """Test configuration export endpoint."""
        client = setup_test_app

        # Add some test data first
        model_data = {
            "name": "export-test-model",
            "provider": "openai",
            "model_id": "gpt-4",
        }
        client.post("/api/ai-models/", json=model_data)

        response = client.post("/api/ai-models/export")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configuration" in data

        config = data["configuration"]
        assert "models" in config
        assert "operation_configs" in config
        assert "export_timestamp" in config
        assert "version" in config

        # Verify exported model
        assert len(config["models"]) > 0
        exported_model = next(
            m for m in config["models"] if m["name"] == "export-test-model"
        )
        assert exported_model["provider"] == "openai"

    def test_import_configuration_endpoint(self, setup_test_app):
        """Test configuration import endpoint."""
        client = setup_test_app

        # Prepare configuration data to import
        import_config = {
            "models": [
                {
                    "name": "imported-model",
                    "provider": "anthropic",
                    "model_id": "claude-3-haiku",
                    "display_name": "Imported Claude",
                    "cost_per_1k_input_tokens": 0.00025,
                    "cost_per_1k_output_tokens": 0.00125,
                    "is_enabled": True,
                }
            ],
            "operation_configs": [
                {
                    "operation_type": "summarization",
                    "primary_model": "imported-model",
                    "fallback_models": "[]",
                    "is_enabled": True,
                    "custom_parameters": "{}",
                }
            ],
            "version": "1.0",
        }

        response = client.post("/api/ai-models/import", json=import_config)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Imported" in data["message"]
        assert "1 models" in data["message"]
        assert "1 operation configurations" in data["message"]

        # Verify imported model
        response = client.get("/api/ai-models/")
        data = response.json()
        model_names = [m["name"] for m in data["models"]]
        assert "imported-model" in model_names

        imported_model = next(
            m for m in data["models"] if m["name"] == "imported-model"
        )
        assert imported_model["provider"] == "anthropic"
        assert imported_model["display_name"] == "Imported Claude"

    def test_api_error_handling(self, setup_test_app):
        """Test API error handling."""
        client = setup_test_app

        # Test invalid JSON
        response = client.post("/api/ai-models/", json={"invalid": "data"})
        assert response.status_code in [400, 422]  # Validation error

        # Test missing required fields
        response = client.post("/api/ai-models/", json={"name": "test"})
        assert response.status_code in [400, 422]  # Validation error

    def test_database_integration(self, setup_test_app):
        """Test that API properly integrates with database operations."""
        client = setup_test_app

        # Add model via API
        model_data = {
            "name": "db-integration-test",
            "provider": "openai",
            "model_id": "gpt-4",
            "description": "Database integration test",
        }

        response = client.post("/api/ai-models/", json=model_data)
        assert response.status_code == 200

        # Verify it's in the database directly
        # Create data manager to check database state
        data_manager = PromptDataManager(
            db_path=os.environ["DB_PATH"],
            tenant_id="single-user",
            user_id="single-user",
        )
        models = data_manager.get_ai_models()
        model_names = [m["name"] for m in models]
        assert "db-integration-test" in model_names

        db_model = next(m for m in models if m["name"] == "db-integration-test")
        assert db_model["provider"] == "openai"
        assert db_model["description"] == "Database integration test"

        # Update via API
        update_data = {"description": "Updated via API"}
        response = client.put("/api/ai-models/db-integration-test", json=update_data)
        assert response.status_code == 200

        # Verify update in database
        models = data_manager.get_ai_models()
        db_model = next(m for m in models if m["name"] == "db-integration-test")
        assert db_model["description"] == "Updated via API"

        # Delete via API
        response = client.delete("/api/ai-models/db-integration-test")
        assert response.status_code == 200

        # Verify deletion in database
        models = data_manager.get_ai_models()
        model_names = [m["name"] for m in models]
        assert "db-integration-test" not in model_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
