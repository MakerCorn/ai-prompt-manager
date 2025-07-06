"""
Unit tests for AI Model Manager Service
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.core.config.ai_model_config import (
    AIModelConfiguration,
    AIProvider,
    ModelConfig,
    OperationType,
)
from src.core.exceptions.base import ConfigurationException
from src.core.services.ai_model_manager import (
    AIModelManager,
    ModelHealthChecker,
    ModelSelector,
    get_model_manager,
    reset_model_manager,
)


class TestModelHealthChecker:
    """Test ModelHealthChecker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AIModelConfiguration()
        self.health_checker = ModelHealthChecker(self.config)

    @pytest.mark.asyncio
    async def test_check_openai_health_success(self):
        """Test successful OpenAI health check."""
        model = ModelConfig(
            name="test-gpt-4",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            api_key="test-key",
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await self.health_checker._check_openai_health(model)

            assert result == (True, "Healthy")

    @pytest.mark.asyncio
    async def test_check_openai_health_no_api_key(self):
        """Test OpenAI health check without API key."""
        model = ModelConfig(
            name="test-gpt-4", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        result = await self.health_checker._check_openai_health(model)

        assert result == (False, "API key not configured")

    @pytest.mark.asyncio
    async def test_check_openai_health_api_error(self):
        """Test OpenAI health check with API error."""
        model = ModelConfig(
            name="test-gpt-4",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            api_key="test-key",
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await self.health_checker._check_openai_health(model)

            assert result == (False, "API error: 401")

    @pytest.mark.asyncio
    async def test_check_azure_openai_health_success(self):
        """Test successful Azure OpenAI health check."""
        model = ModelConfig(
            name="test-azure-gpt-4",
            provider=AIProvider.AZURE_OPENAI,
            model_id="gpt-4",
            api_key="test-key",
            api_endpoint="https://test.openai.azure.com",
            deployment_name="gpt-4-deployment",
            api_version="2024-02-15-preview",
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await self.health_checker._check_azure_openai_health(model)

            assert result == (True, "Healthy")

    @pytest.mark.asyncio
    async def test_check_azure_openai_health_missing_config(self):
        """Test Azure OpenAI health check with missing configuration."""
        model = ModelConfig(
            name="test-azure-gpt-4", provider=AIProvider.AZURE_OPENAI, model_id="gpt-4"
        )

        result = await self.health_checker._check_azure_openai_health(model)

        assert result == (False, "API key or endpoint not configured")

    @pytest.mark.asyncio
    async def test_check_anthropic_health_success(self):
        """Test successful Anthropic health check."""
        model = ModelConfig(
            name="test-claude",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-opus-20240229",
            api_key="test-key",
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await self.health_checker._check_anthropic_health(model)

            assert result == (True, "Healthy")

    @pytest.mark.asyncio
    async def test_check_local_health_ollama_success(self):
        """Test successful Ollama health check."""
        model = ModelConfig(
            name="test-ollama",
            provider=AIProvider.OLLAMA,
            model_id="llama2:7b",
            api_endpoint="http://localhost:11434/api/generate",
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await self.health_checker._check_local_health(model)

            assert result == (True, "Healthy")

    @pytest.mark.asyncio
    async def test_check_local_health_no_endpoint(self):
        """Test local health check without endpoint."""
        model = ModelConfig(
            name="test-ollama", provider=AIProvider.OLLAMA, model_id="llama2:7b"
        )

        result = await self.health_checker._check_local_health(model)

        assert result == (False, "API endpoint not configured")

    @pytest.mark.asyncio
    async def test_check_model_health_updates_model(self):
        """Test that check_model_health updates model availability."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.GOOGLE, model_id="gemini-pro"
        )

        # Mock Google health check to return success
        with patch.object(
            self.health_checker, "_check_google_health", return_value=(True, "Healthy")
        ):
            is_healthy, status, response_time = (
                await self.health_checker.check_model_health(model)
            )

            assert is_healthy is True
            assert status == "Healthy"
            assert isinstance(response_time, float)
            assert model.is_available is True
            assert model.last_health_check is not None

    @pytest.mark.asyncio
    async def test_check_model_health_unsupported_provider(self):
        """Test health check with unsupported provider."""
        # Create a model with a provider that doesn't have health check implementation
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.HUGGINGFACE,  # Not implemented in health checker
            model_id="test-model",
        )

        is_healthy, status, response_time = (
            await self.health_checker.check_model_health(model)
        )

        assert is_healthy is False
        assert "Unsupported provider" in status
        assert model.is_available is False

    @pytest.mark.asyncio
    async def test_check_all_models(self):
        """Test checking health of all models."""
        # Add some models to configuration
        model1 = ModelConfig(
            name="model1",
            provider=AIProvider.GOOGLE,
            model_id="gemini-pro",
            is_enabled=True,
        )
        model2 = ModelConfig(
            name="model2",
            provider=AIProvider.GOOGLE,
            model_id="gemini-pro",
            is_enabled=True,
        )
        model3 = ModelConfig(
            name="model3",
            provider=AIProvider.GOOGLE,
            model_id="gemini-pro",
            is_enabled=False,
        )

        self.config.add_model(model1)
        self.config.add_model(model2)
        self.config.add_model(model3)

        with patch.object(
            self.health_checker, "_check_google_health", return_value=(True, "Healthy")
        ):
            results = await self.health_checker.check_all_models()

            # Should only check enabled models
            assert len(results) == 2
            assert "model1" in results
            assert "model2" in results
            assert "model3" not in results

            for result in results.values():
                assert "healthy" in result
                assert "status" in result
                assert "response_time" in result
                assert "last_check" in result


class TestModelSelector:
    """Test ModelSelector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AIModelConfiguration()
        self.selector = ModelSelector(self.config)

    def test_select_model_for_operation_with_configured_models(self):
        """Test selecting model for operation with configured models."""
        # Add models
        model1 = ModelConfig(
            name="model1",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
        )
        model2 = ModelConfig(
            name="model2",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_enabled=True,
            is_available=False,
        )

        self.config.add_model(model1)
        self.config.add_model(model2)

        # Configure operation
        self.config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="model2",  # Not available
            fallback_models=["model1"],  # Available
        )

        selected_model = self.selector.select_model_for_operation(
            OperationType.PROMPT_ENHANCEMENT
        )

        assert selected_model == model1  # Should select first available model

    def test_select_model_for_operation_fallback_to_default(self):
        """Test selecting model falls back to default operation."""
        # Add models
        model1 = ModelConfig(
            name="model1",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
        )
        self.config.add_model(model1)

        # Configure default operation
        self.config.set_operation_model(OperationType.DEFAULT, primary_model="model1")

        # Try to select for unconfigured operation
        selected_model = self.selector.select_model_for_operation(
            OperationType.PROMPT_TESTING
        )

        assert selected_model == model1  # Should fall back to default

    def test_select_model_for_operation_no_models(self):
        """Test selecting model with no configured models."""
        selected_model = self.selector.select_model_for_operation(
            OperationType.PROMPT_ENHANCEMENT
        )

        assert selected_model is None

    def test_select_model_for_operation_with_requirements(self):
        """Test selecting model with specific requirements."""
        # Add models with different capabilities
        model1 = ModelConfig(
            name="model1",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
            supports_vision=False,
            max_context_length=8192,
        )
        model2 = ModelConfig(
            name="model2",
            provider=AIProvider.OPENAI,
            model_id="gpt-4-vision",
            is_enabled=True,
            is_available=True,
            supports_vision=True,
            max_context_length=128000,
        )

        self.config.add_model(model1)
        self.config.add_model(model2)

        # Configure operation
        self.config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="model1",
            fallback_models=["model2"],
        )

        # Select with vision requirement
        selected_model = self.selector.select_model_for_operation(
            OperationType.PROMPT_ENHANCEMENT, requirements={"supports_vision": True}
        )

        assert selected_model == model2  # Should select model with vision support

    def test_model_meets_requirements(self):
        """Test _model_meets_requirements method."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            max_context_length=8192,
            supports_vision=True,
            supports_function_calling=True,
            supports_streaming=False,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
        )

        # Test various requirements
        assert (
            self.selector._model_meets_requirements(model, {"supports_vision": True})
            is True
        )
        assert (
            self.selector._model_meets_requirements(model, {"supports_vision": False})
            is True
        )
        assert (
            self.selector._model_meets_requirements(model, {"supports_streaming": True})
            is False
        )
        assert (
            self.selector._model_meets_requirements(model, {"max_tokens": 4000}) is True
        )
        assert (
            self.selector._model_meets_requirements(model, {"max_tokens": 10000})
            is False
        )
        assert (
            self.selector._model_meets_requirements(
                model, {"max_cost_per_1k_tokens": 0.05}
            )
            is True
        )
        assert (
            self.selector._model_meets_requirements(
                model, {"max_cost_per_1k_tokens": 0.03}
            )
            is False
        )

    def test_get_fallback_models(self):
        """Test getting fallback models excluding failed model."""
        # Add models
        model1 = ModelConfig(
            name="model1",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
        )
        model2 = ModelConfig(
            name="model2",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_enabled=True,
            is_available=True,
        )
        model3 = ModelConfig(
            name="model3",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3",
            is_enabled=True,
            is_available=False,
        )

        self.config.add_model(model1)
        self.config.add_model(model2)
        self.config.add_model(model3)

        # Configure operation
        self.config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="model1",
            fallback_models=["model2", "model3"],
        )

        fallback_models = self.selector.get_fallback_models(
            OperationType.PROMPT_ENHANCEMENT, "model1"
        )

        # Should exclude failed model (model1) and unavailable models (model3)
        assert len(fallback_models) == 1
        assert fallback_models[0] == model2


class TestAIModelManager:
    """Test AIModelManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AIModelManager()

    def test_manager_initialization(self):
        """Test AIModelManager initialization."""
        assert isinstance(self.manager.config, AIModelConfiguration)
        assert isinstance(self.manager.health_checker, ModelHealthChecker)
        assert isinstance(self.manager.selector, ModelSelector)
        assert isinstance(self.manager._usage_stats, dict)

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test manager initialization with health checks."""
        with patch.object(self.manager, "run_health_checks", return_value={}):
            await self.manager.initialize()
            # Should not raise any exceptions

    def test_add_model(self):
        """Test adding a model to the manager."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        initial_count = len(self.manager.config.models)
        self.manager.add_model(model)

        assert len(self.manager.config.models) == initial_count + 1
        assert "test-model" in self.manager.config.models

    def test_remove_model(self):
        """Test removing a model from the manager."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        self.manager.add_model(model)
        assert "test-model" in self.manager.config.models

        self.manager.remove_model("test-model")
        assert "test-model" not in self.manager.config.models

    def test_update_model(self):
        """Test updating a model in the manager."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            temperature=0.7,
        )

        self.manager.add_model(model)

        updates = {"temperature": 0.9, "description": "Updated model"}
        self.manager.update_model("test-model", updates)

        updated_model = self.manager.config.get_model("test-model")
        assert updated_model.temperature == 0.9
        assert updated_model.description == "Updated model"

    def test_update_nonexistent_model(self):
        """Test updating a model that doesn't exist."""
        with pytest.raises(ConfigurationException):
            self.manager.update_model("nonexistent-model", {"temperature": 0.9})

    @pytest.mark.asyncio
    async def test_select_model(self):
        """Test model selection."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
        )

        self.manager.add_model(model)
        self.manager.config.set_operation_model(
            OperationType.DEFAULT, primary_model="test-model"
        )

        selected_model = await self.manager.select_model(OperationType.DEFAULT)
        assert selected_model == model

    @pytest.mark.asyncio
    async def test_run_health_checks(self):
        """Test running health checks."""
        with patch.object(
            self.manager.health_checker,
            "check_all_models",
            return_value={"model1": {"healthy": True}},
        ):
            results = await self.manager.run_health_checks()
            assert "model1" in results

    @pytest.mark.asyncio
    async def test_check_model_health(self):
        """Test checking specific model health."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.GOOGLE, model_id="gemini-pro"
        )

        self.manager.add_model(model)

        with patch.object(
            self.manager.health_checker,
            "check_model_health",
            return_value=(True, "Healthy", 1.5),
        ):
            is_healthy, status, response_time = await self.manager.check_model_health(
                "test-model"
            )

            assert is_healthy is True
            assert status == "Healthy"
            assert response_time == 1.5

    def test_check_nonexistent_model_health(self):
        """Test checking health of nonexistent model."""
        with pytest.raises(ConfigurationException):
            asyncio.run(self.manager.check_model_health("nonexistent-model"))

    def test_get_usage_stats(self):
        """Test getting usage statistics."""
        # Record some usage
        self.manager.record_usage("model1", 1000, 0.05, 1.2)
        self.manager.record_usage("model2", 500, 0.02, 0.8)
        self.manager.record_usage("model1", 800, 0.04, 1.0)  # Second usage for model1

        stats = self.manager.get_usage_stats()

        assert stats["total_requests"] == 3
        assert stats["total_tokens"] == 2300
        assert stats["total_cost"] == 0.11
        assert len(stats["models"]) == 2

        model1_stats = stats["models"]["model1"]
        assert model1_stats["requests"] == 2
        assert model1_stats["tokens"] == 1800
        assert model1_stats["cost"] == 0.09
        assert model1_stats["avg_response_time"] == 1.1

    def test_record_usage(self):
        """Test recording usage statistics."""
        self.manager.record_usage("test-model", 1000, 0.05, 1.5)

        stats = self.manager._usage_stats["test-model"]
        assert stats["requests"] == 1
        assert stats["tokens"] == 1000
        assert stats["cost"] == 0.05
        assert stats["total_response_time"] == 1.5
        assert stats["avg_response_time"] == 1.5
        assert stats["last_used"] is not None

    def test_get_model_recommendations(self):
        """Test getting model recommendations."""
        # Add some models
        model1 = ModelConfig(
            name="expensive-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_available=True,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
        )
        model2 = ModelConfig(
            name="cheap-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_available=True,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
        )

        self.manager.config.add_model(model1)
        self.manager.config.add_model(model2)

        recommendations = self.manager.get_model_recommendations(
            OperationType.PROMPT_TESTING
        )

        assert len(recommendations) <= 5  # Should return top 5
        assert all(
            "model" in rec and "score" in rec and "reason" in rec
            for rec in recommendations
        )

        # For testing, cheaper model should score higher
        scores = {rec["model"].name: rec["score"] for rec in recommendations}
        assert scores["cheap-model"] > scores["expensive-model"]

    def test_export_configuration(self):
        """Test exporting configuration."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )
        self.manager.add_model(model)

        exported = self.manager.export_configuration()

        assert isinstance(exported, dict)
        assert "models" in exported
        assert "operations" in exported
        assert "test-model" in exported["models"]

    def test_import_configuration(self):
        """Test importing configuration."""
        config_data = {
            "models": {
                "imported-model": {
                    "name": "imported-model",
                    "provider": "openai",
                    "model_id": "gpt-4",
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "is_enabled": True,
                }
            },
            "operations": {},
            "default_timeout": 30,
            "max_retries": 3,
            "health_check_interval": 300,
        }

        self.manager.import_configuration(config_data)

        assert "imported-model" in self.manager.config.models
        imported_model = self.manager.config.get_model("imported-model")
        assert imported_model.provider == AIProvider.OPENAI
        assert imported_model.cost_per_1k_input_tokens == 0.01


class TestGlobalModelManager:
    """Test global model manager functions."""

    def setup_method(self):
        """Reset global manager before each test."""
        reset_model_manager()

    @pytest.mark.asyncio
    async def test_get_model_manager(self):
        """Test getting global model manager."""
        manager = await get_model_manager()

        assert isinstance(manager, AIModelManager)

        # Should return same instance on subsequent calls
        manager2 = await get_model_manager()
        assert manager is manager2

    def test_reset_model_manager(self):
        """Test resetting global model manager."""
        # Get manager to initialize it
        asyncio.run(get_model_manager())

        # Reset it
        reset_model_manager()

        # Getting manager again should create new instance
        manager = asyncio.run(get_model_manager())
        assert isinstance(manager, AIModelManager)


if __name__ == "__main__":
    pytest.main([__file__])
