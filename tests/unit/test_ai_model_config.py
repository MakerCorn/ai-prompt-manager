"""
Unit tests for AI Model Configuration System
"""

import pytest

from src.core.config.ai_model_config import (
    AIModelConfiguration,
    AIProvider,
    ModelConfig,
    OperationConfig,
    OperationType,
    create_default_configuration,
    get_default_models,
    get_default_operation_configs,
)


class TestAIProvider:
    """Test AIProvider enum."""

    def test_provider_values(self):
        """Test that all expected providers are available."""
        expected_providers = [
            "openai",
            "azure_openai",
            "anthropic",
            "google",
            "ollama",
            "lmstudio",
            "llamacpp",
            "huggingface",
            "cohere",
            "together",
        ]

        actual_providers = [provider.value for provider in AIProvider]

        for expected in expected_providers:
            assert expected in actual_providers

    def test_provider_enum_access(self):
        """Test accessing providers by enum."""
        assert AIProvider.OPENAI.value == "openai"
        assert AIProvider.AZURE_OPENAI.value == "azure_openai"
        assert AIProvider.ANTHROPIC.value == "anthropic"


class TestOperationType:
    """Test OperationType enum."""

    def test_operation_types(self):
        """Test that all expected operation types are available."""
        expected_operations = [
            "default",
            "prompt_enhancement",
            "prompt_optimization",
            "prompt_testing",
            "prompt_combining",
            "translation",
            "token_calculation",
            "generation",
            "analysis",
            "categorization",
            "summarization",
        ]

        actual_operations = [op.value for op in OperationType]

        for expected in expected_operations:
            assert expected in actual_operations


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a ModelConfig instance."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            display_name="Test GPT-4",
            description="Test model",
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            supports_streaming=True,
            supports_function_calling=True,
        )

        assert model.name == "test-model"
        assert model.provider == AIProvider.OPENAI
        assert model.model_id == "gpt-4"
        assert model.display_name == "Test GPT-4"
        assert model.description == "Test model"
        assert model.cost_per_1k_input_tokens == 0.01
        assert model.cost_per_1k_output_tokens == 0.03
        assert model.supports_streaming is True
        assert model.supports_function_calling is True
        assert model.is_enabled is True  # Default value

    def test_model_config_defaults(self):
        """Test ModelConfig default values."""
        model = ModelConfig(
            name="minimal-model", provider=AIProvider.OPENAI, model_id="gpt-3.5-turbo"
        )

        assert model.display_name is None
        assert model.description is None
        assert model.api_key is None
        assert model.temperature == 0.7
        assert model.top_p == 1.0
        assert model.frequency_penalty == 0.0
        assert model.presence_penalty == 0.0
        assert model.cost_per_1k_input_tokens == 0.0
        assert model.cost_per_1k_output_tokens == 0.0
        assert model.supports_streaming is False
        assert model.supports_function_calling is False
        assert model.supports_vision is False
        assert model.supports_json_mode is False
        assert model.is_enabled is True
        assert model.is_available is False

    def test_get_display_name(self):
        """Test get_display_name method."""
        # With display name
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            display_name="Custom Display Name",
        )
        assert model.get_display_name() == "Custom Display Name"

        # Without display name
        model_no_display = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )
        assert model_no_display.get_display_name() == "test-model"

    def test_get_full_name(self):
        """Test get_full_name method."""
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )
        assert model.get_full_name() == "openai/gpt-4"

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
        )

        # Test with only input tokens
        cost = model.estimate_cost(input_tokens=1000)
        assert cost == 0.01

        # Test with input and output tokens
        cost = model.estimate_cost(input_tokens=1000, output_tokens=500)
        expected = (1000 / 1000) * 0.01 + (500 / 1000) * 0.03
        assert cost == expected

    def test_to_dict(self):
        """Test converting ModelConfig to dictionary."""
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            display_name="Test Model",
            description="Test description",
            api_endpoint="https://api.openai.com",
            cost_per_1k_input_tokens=0.01,
            supports_streaming=True,
        )

        result = model.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "test-model"
        assert result["provider"] == "openai"
        assert result["model_id"] == "gpt-4"
        assert result["display_name"] == "Test Model"
        assert result["description"] == "Test description"
        assert result["api_endpoint"] == "https://api.openai.com"
        assert result["cost_per_1k_input_tokens"] == 0.01
        assert result["supports_streaming"] is True

    def test_from_dict(self):
        """Test creating ModelConfig from dictionary."""
        data = {
            "name": "test-model",
            "provider": "openai",
            "model_id": "gpt-4",
            "display_name": "Test Model",
            "description": "Test description",
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
            "supports_streaming": True,
            "supports_function_calling": True,
            "is_enabled": False,
        }

        model = ModelConfig.from_dict(data)

        assert model.name == "test-model"
        assert model.provider == AIProvider.OPENAI
        assert model.model_id == "gpt-4"
        assert model.display_name == "Test Model"
        assert model.description == "Test description"
        assert model.cost_per_1k_input_tokens == 0.01
        assert model.cost_per_1k_output_tokens == 0.03
        assert model.supports_streaming is True
        assert model.supports_function_calling is True
        assert model.is_enabled is False


class TestOperationConfig:
    """Test OperationConfig dataclass."""

    def test_operation_config_creation(self):
        """Test creating an OperationConfig instance."""
        config = OperationConfig(
            operation_type=OperationType.PROMPT_ENHANCEMENT,
            primary_model="gpt-4",
            fallback_models=["gpt-3.5-turbo", "claude-3-haiku"],
            is_enabled=True,
            custom_parameters={"temperature": 0.8},
        )

        assert config.operation_type == OperationType.PROMPT_ENHANCEMENT
        assert config.primary_model == "gpt-4"
        assert config.fallback_models == ["gpt-3.5-turbo", "claude-3-haiku"]
        assert config.is_enabled is True
        assert config.custom_parameters == {"temperature": 0.8}

    def test_operation_config_defaults(self):
        """Test OperationConfig default values."""
        config = OperationConfig(operation_type=OperationType.DEFAULT)

        assert config.primary_model is None
        assert config.fallback_models == []
        assert config.is_enabled is True
        assert config.custom_parameters == {}

    def test_get_model_sequence(self):
        """Test get_model_sequence method."""
        # With primary and fallback models
        config = OperationConfig(
            operation_type=OperationType.PROMPT_ENHANCEMENT,
            primary_model="gpt-4",
            fallback_models=["gpt-3.5-turbo", "claude-3-haiku"],
        )

        sequence = config.get_model_sequence()
        assert sequence == ["gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]

        # With only fallback models
        config_no_primary = OperationConfig(
            operation_type=OperationType.PROMPT_ENHANCEMENT,
            fallback_models=["gpt-3.5-turbo", "claude-3-haiku"],
        )

        sequence = config_no_primary.get_model_sequence()
        assert sequence == ["gpt-3.5-turbo", "claude-3-haiku"]

        # With only primary model
        config_no_fallback = OperationConfig(
            operation_type=OperationType.PROMPT_ENHANCEMENT, primary_model="gpt-4"
        )

        sequence = config_no_fallback.get_model_sequence()
        assert sequence == ["gpt-4"]


class TestAIModelConfiguration:
    """Test AIModelConfiguration class."""

    def test_configuration_creation(self):
        """Test creating an AIModelConfiguration instance."""
        config = AIModelConfiguration()

        assert isinstance(config.models, dict)
        assert isinstance(config.operations, dict)
        assert config.default_timeout == 30
        assert config.max_retries == 3
        assert config.health_check_interval == 300

    def test_add_model(self):
        """Test adding a model to the configuration."""
        config = AIModelConfiguration()
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        config.add_model(model)

        assert "test-model" in config.models
        assert config.models["test-model"] == model

    def test_remove_model(self):
        """Test removing a model from the configuration."""
        config = AIModelConfiguration()
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        config.add_model(model)
        assert "test-model" in config.models

        # Add operation config that uses this model
        op_config = OperationConfig(
            operation_type=OperationType.DEFAULT,
            primary_model="test-model",
            fallback_models=["test-model", "other-model"],
        )
        config.operations[OperationType.DEFAULT] = op_config

        config.remove_model("test-model")

        assert "test-model" not in config.models
        assert config.operations[OperationType.DEFAULT].primary_model is None
        assert (
            "test-model" not in config.operations[OperationType.DEFAULT].fallback_models
        )
        assert "other-model" in config.operations[OperationType.DEFAULT].fallback_models

    def test_get_model(self):
        """Test getting a model by name."""
        config = AIModelConfiguration()
        model = ModelConfig(
            name="test-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        config.add_model(model)

        retrieved_model = config.get_model("test-model")
        assert retrieved_model == model

        non_existent = config.get_model("non-existent")
        assert non_existent is None

    def test_get_enabled_models(self):
        """Test getting enabled models."""
        config = AIModelConfiguration()

        enabled_model = ModelConfig(
            name="enabled-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
        )

        disabled_model = ModelConfig(
            name="disabled-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_enabled=False,
        )

        config.add_model(enabled_model)
        config.add_model(disabled_model)

        enabled_models = config.get_enabled_models()
        assert len(enabled_models) == 1
        assert enabled_models[0] == enabled_model

    def test_get_available_models(self):
        """Test getting available models."""
        config = AIModelConfiguration()

        available_model = ModelConfig(
            name="available-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            is_enabled=True,
            is_available=True,
        )

        unavailable_model = ModelConfig(
            name="unavailable-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_enabled=True,
            is_available=False,
        )

        config.add_model(available_model)
        config.add_model(unavailable_model)

        available_models = config.get_available_models()
        assert len(available_models) == 1
        assert available_models[0] == available_model

    def test_get_models_by_provider(self):
        """Test getting models by provider."""
        config = AIModelConfiguration()

        openai_model = ModelConfig(
            name="openai-model", provider=AIProvider.OPENAI, model_id="gpt-4"
        )

        anthropic_model = ModelConfig(
            name="anthropic-model",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-opus",
        )

        config.add_model(openai_model)
        config.add_model(anthropic_model)

        openai_models = config.get_models_by_provider(AIProvider.OPENAI)
        assert len(openai_models) == 1
        assert openai_models[0] == openai_model

        anthropic_models = config.get_models_by_provider(AIProvider.ANTHROPIC)
        assert len(anthropic_models) == 1
        assert anthropic_models[0] == anthropic_model

    def test_set_operation_model(self):
        """Test setting operation model configuration."""
        config = AIModelConfiguration()

        config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="gpt-4",
            fallback_models=["gpt-3.5-turbo"],
        )

        assert OperationType.PROMPT_ENHANCEMENT in config.operations
        op_config = config.operations[OperationType.PROMPT_ENHANCEMENT]
        assert op_config.primary_model == "gpt-4"
        assert op_config.fallback_models == ["gpt-3.5-turbo"]

    def test_get_operation_models(self):
        """Test getting models for an operation."""
        config = AIModelConfiguration()

        # Add models
        model1 = ModelConfig(
            name="model1", provider=AIProvider.OPENAI, model_id="gpt-4", is_enabled=True
        )
        model2 = ModelConfig(
            name="model2",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            is_enabled=True,
        )
        model3 = ModelConfig(
            name="model3",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3",
            is_enabled=False,
        )

        config.add_model(model1)
        config.add_model(model2)
        config.add_model(model3)

        # Set operation configuration
        config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="model1",
            fallback_models=["model2", "model3"],
        )

        operation_models = config.get_operation_models(OperationType.PROMPT_ENHANCEMENT)
        # Should only return enabled models
        assert len(operation_models) == 2
        assert model1 in operation_models
        assert model2 in operation_models
        assert model3 not in operation_models

    def test_get_best_model_for_operation(self):
        """Test getting best model for an operation."""
        config = AIModelConfiguration()

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

        config.add_model(model1)
        config.add_model(model2)

        # Set operation configuration
        config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="model2",  # Not available
            fallback_models=["model1"],  # Available
        )

        best_model = config.get_best_model_for_operation(
            OperationType.PROMPT_ENHANCEMENT
        )
        assert best_model == model1  # Should return first available model

    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        config = AIModelConfiguration()

        # Add a model
        model = ModelConfig(
            name="test-model",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            cost_per_1k_input_tokens=0.01,
        )
        config.add_model(model)

        # Add operation configuration
        config.set_operation_model(
            OperationType.PROMPT_ENHANCEMENT,
            primary_model="test-model",
            fallback_models=["fallback-model"],
        )

        # Convert to dict
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "models" in config_dict
        assert "operations" in config_dict
        assert "default_timeout" in config_dict

        # Convert back from dict
        restored_config = AIModelConfiguration.from_dict(config_dict)

        assert len(restored_config.models) == 1
        assert "test-model" in restored_config.models
        assert restored_config.models["test-model"].provider == AIProvider.OPENAI
        assert OperationType.PROMPT_ENHANCEMENT in restored_config.operations


class TestDefaultConfigurations:
    """Test default configuration functions."""

    def test_get_default_models(self):
        """Test getting default models."""
        models = get_default_models()

        assert isinstance(models, list)
        assert len(models) > 0

        # Check that we have models from different providers
        providers = {model.provider for model in models}
        assert AIProvider.OPENAI in providers
        assert AIProvider.ANTHROPIC in providers
        assert AIProvider.GOOGLE in providers

        # Check specific expected models
        model_names = {model.name for model in models}
        assert "gpt-4-turbo" in model_names
        assert "claude-3-opus" in model_names
        assert "gemini-pro" in model_names

    def test_get_default_operation_configs(self):
        """Test getting default operation configurations."""
        configs = get_default_operation_configs()

        assert isinstance(configs, dict)
        assert len(configs) > 0

        # Check that we have configurations for expected operations
        assert OperationType.DEFAULT in configs
        assert OperationType.PROMPT_ENHANCEMENT in configs
        assert OperationType.PROMPT_OPTIMIZATION in configs

        # Check configuration structure
        default_config = configs[OperationType.DEFAULT]
        assert isinstance(default_config, OperationConfig)
        assert default_config.operation_type == OperationType.DEFAULT

    def test_create_default_configuration(self):
        """Test creating default configuration."""
        config = create_default_configuration()

        assert isinstance(config, AIModelConfiguration)
        assert len(config.models) > 0
        assert len(config.operations) > 0

        # Check that models are properly added
        model_names = set(config.models.keys())
        assert "gpt-4-turbo" in model_names
        assert "claude-3-opus" in model_names

        # Check that operations are properly configured
        assert OperationType.DEFAULT in config.operations
        assert OperationType.PROMPT_ENHANCEMENT in config.operations


if __name__ == "__main__":
    pytest.main([__file__])
