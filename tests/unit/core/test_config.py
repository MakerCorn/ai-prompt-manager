"""
Unit tests for the configuration system.

This module tests the centralized configuration management including
environment variable loading, validation, and type safety.
"""

import os
from unittest.mock import patch

import pytest

from src.core.config.settings import (AppConfig, AuthConfig, DatabaseConfig,
                                      DatabaseType, ExternalServicesConfig,
                                      LogLevel, OptimizationService,
                                      TranslationService, get_config,
                                      reset_config)
from src.core.exceptions.base import ConfigurationException


class TestDatabaseConfig:
    """Test cases for DatabaseConfig."""

    def test_database_config_defaults(self):
        """Test database config with default values."""
        config = DatabaseConfig()

        assert config.db_type == DatabaseType.SQLITE
        assert config.db_path == "prompts.db"
        assert config.dsn is None
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 30

    def test_database_config_from_env_sqlite(self):
        """Test database config from environment variables for SQLite."""
        env_vars = {
            "DB_TYPE": "sqlite",
            "DB_PATH": "test.db",
            "DB_POOL_SIZE": "3",
            "DB_MAX_OVERFLOW": "5",
            "DB_POOL_TIMEOUT": "20",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = DatabaseConfig.from_env()

            assert config.db_type == DatabaseType.SQLITE
            assert config.db_path == "test.db"
            assert config.pool_size == 3
            assert config.max_overflow == 5
            assert config.pool_timeout == 20

    def test_database_config_from_env_postgres(self):
        """Test database config from environment variables for PostgreSQL."""
        env_vars = {
            "DB_TYPE": "postgres",
            "POSTGRES_DSN": "postgresql://user:pass@localhost:5432/test",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = DatabaseConfig.from_env()

            assert config.db_type == DatabaseType.POSTGRES
            assert config.dsn == "postgresql://user:pass@localhost:5432/test"

    def test_database_config_invalid_type(self):
        """Test database config with invalid type raises exception."""
        env_vars = {"DB_TYPE": "invalid_db_type"}

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ConfigurationException) as exc_info:
                DatabaseConfig.from_env()

            assert "Invalid DB_TYPE" in str(exc_info.value)

    def test_database_config_validate_postgres_without_dsn(self):
        """Test validation fails for PostgreSQL without DSN."""
        config = DatabaseConfig(db_type=DatabaseType.POSTGRES)

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "POSTGRES_DSN is required" in str(exc_info.value)

    @patch("pathlib.Path.mkdir")
    def test_database_config_validate_sqlite_creates_directory(self, mock_mkdir):
        """Test validation creates directory for SQLite database."""
        config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path="data/test.db")

        config.validate()

        # Should call mkdir to create directory
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestAuthConfig:
    """Test cases for AuthConfig."""

    def test_auth_config_defaults(self):
        """Test auth config with default values."""
        config = AuthConfig()

        assert len(config.secret_key) > 0  # Should generate random secret
        assert config.jwt_expiry_hours == 24
        assert config.password_min_length == 8
        assert config.multitenant_mode is True
        assert config.local_dev_mode is False
        assert config.sso_enabled is False
        assert config.entra_id_enabled is False

    def test_auth_config_from_env(self):
        """Test auth config from environment variables."""
        env_vars = {
            "SECRET_KEY": "test_secret_key",
            "JWT_EXPIRY_HOURS": "48",
            "PASSWORD_MIN_LENGTH": "12",
            "MULTITENANT_MODE": "false",
            "LOCAL_DEV_MODE": "true",
            "SSO_ENABLED": "true",
            "SSO_CLIENT_ID": "test_client_id",
            "SSO_CLIENT_SECRET": "test_client_secret",
            "SSO_AUTHORITY": "https://login.example.com",
            "ENTRA_ID_ENABLED": "true",
            "ENTRA_CLIENT_ID": "entra_client_id",
            "ENTRA_CLIENT_SECRET": "entra_client_secret",
            "ENTRA_TENANT_ID": "tenant_id",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = AuthConfig.from_env()

            assert config.secret_key == "test_secret_key"
            assert config.jwt_expiry_hours == 48
            assert config.password_min_length == 12
            assert config.multitenant_mode is False
            assert config.local_dev_mode is True
            assert config.sso_enabled is True
            assert config.sso_client_id == "test_client_id"
            assert config.entra_id_enabled is True
            assert config.entra_client_id == "entra_client_id"

    def test_auth_config_validate_sso_missing_fields(self):
        """Test validation fails for SSO with missing fields."""
        config = AuthConfig(sso_enabled=True)

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "SSO enabled but missing" in str(exc_info.value)
        assert "SSO_CLIENT_ID" in str(exc_info.value)

    def test_auth_config_validate_entra_missing_fields(self):
        """Test validation fails for Entra ID with missing fields."""
        config = AuthConfig(entra_id_enabled=True)

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "Entra ID enabled but missing" in str(exc_info.value)
        assert "ENTRA_CLIENT_ID" in str(exc_info.value)

    def test_auth_config_validate_success(self):
        """Test successful validation with complete SSO config."""
        config = AuthConfig(
            sso_enabled=True,
            sso_client_id="client_id",
            sso_client_secret="client_secret",
            sso_authority="https://login.example.com",
        )

        # Should not raise exception
        config.validate()


class TestExternalServicesConfig:
    """Test cases for ExternalServicesConfig."""

    def test_external_services_config_defaults(self):
        """Test external services config with default values."""
        config = ExternalServicesConfig()

        assert config.prompt_optimizer == OptimizationService.BUILTIN
        assert config.translation_service == TranslationService.MOCK
        assert config.azure_ai_enabled is False
        assert config.azure_openai_version == "2024-02-15-preview"

    def test_external_services_config_from_env(self):
        """Test external services config from environment variables."""
        env_vars = {
            "PROMPT_OPTIMIZER": "langwatch",
            "LANGWATCH_API_KEY": "lw_key",
            "LANGWATCH_PROJECT_ID": "lw_project",
            "TRANSLATION_SERVICE": "openai",
            "OPENAI_API_KEY": "openai_key",
            "AZURE_AI_ENABLED": "true",
            "AZURE_AI_ENDPOINT": "https://azure.ai.endpoint",
            "AZURE_AI_KEY": "azure_key",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = ExternalServicesConfig.from_env()

            assert config.prompt_optimizer == OptimizationService.LANGWATCH
            assert config.langwatch_api_key == "lw_key"
            assert config.langwatch_project_id == "lw_project"
            assert config.translation_service == TranslationService.OPENAI
            assert config.openai_api_key == "openai_key"
            assert config.azure_ai_enabled is True
            assert config.azure_ai_endpoint == "https://azure.ai.endpoint"

    def test_external_services_config_invalid_optimizer(self):
        """Test external services config with invalid optimizer falls back to builtin."""
        env_vars = {"PROMPT_OPTIMIZER": "invalid_optimizer"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = ExternalServicesConfig.from_env()

            assert config.prompt_optimizer == OptimizationService.BUILTIN

    def test_external_services_config_invalid_translation(self):
        """Test external services config with invalid translation service falls back to mock."""
        env_vars = {"TRANSLATION_SERVICE": "invalid_service"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = ExternalServicesConfig.from_env()

            assert config.translation_service == TranslationService.MOCK


class TestAppConfig:
    """Test cases for AppConfig."""

    def test_app_config_defaults(self):
        """Test app config with default values."""
        config = AppConfig()

        assert config.host == "0.0.0.0"  # nosec B104: Test assertion
        assert config.port == 7860
        assert config.debug is False
        assert config.enable_api is False
        assert config.default_language == "en"
        assert config.log_level == LogLevel.INFO
        assert config.enable_gradio_share is False
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.auth, AuthConfig)
        assert isinstance(config.external_services, ExternalServicesConfig)

    def test_app_config_from_env(self):
        """Test app config from environment variables."""
        env_vars = {
            "SERVER_HOST": "127.0.0.1",
            "SERVER_PORT": "8080",
            "DEBUG": "true",
            "ENABLE_API": "true",
            "DEFAULT_LANGUAGE": "es",
            "LOG_LEVEL": "DEBUG",
            "GRADIO_SHARE": "true",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = AppConfig.from_env()

            assert config.host == "127.0.0.1"
            assert config.port == 8080
            assert config.debug is True
            assert config.enable_api is True
            assert config.default_language == "es"
            assert config.log_level == LogLevel.DEBUG
            assert config.enable_gradio_share is True

    def test_app_config_invalid_log_level(self):
        """Test app config with invalid log level falls back to INFO."""
        env_vars = {"LOG_LEVEL": "INVALID_LEVEL"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = AppConfig.from_env()

            assert config.log_level == LogLevel.INFO

    def test_app_config_validate_invalid_port(self):
        """Test validation fails for invalid port number."""
        config = AppConfig(port=100)  # Below valid range

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "Invalid port number" in str(exc_info.value)

        config = AppConfig(port=70000)  # Above valid range

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "Invalid port number" in str(exc_info.value)

    def test_app_config_validate_calls_subconfig_validation(self):
        """Test that app config validation calls subconfig validation."""
        # Create config that will fail database validation
        config = AppConfig()
        config.database = DatabaseConfig(db_type=DatabaseType.POSTGRES)  # No DSN

        with pytest.raises(ConfigurationException) as exc_info:
            config.validate()

        assert "POSTGRES_DSN is required" in str(exc_info.value)

    def test_app_config_to_dict(self):
        """Test converting app config to dictionary."""
        config = AppConfig(host="localhost", port=3000, debug=True, enable_api=True)

        config_dict = config.to_dict()

        assert config_dict["host"] == "localhost"
        assert config_dict["port"] == 3000
        assert config_dict["debug"] is True
        assert config_dict["enable_api"] is True
        assert "database_type" in config_dict
        assert "log_level" in config_dict

        # Should not include sensitive information
        assert "secret_key" not in str(config_dict)


class TestGlobalConfig:
    """Test cases for global configuration management."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def teardown_method(self):
        """Reset config after each test."""
        reset_config()

    def test_get_config_creates_and_caches_config(self):
        """Test that get_config creates and caches configuration."""
        # First call should create config
        config1 = get_config()
        assert config1 is not None

        # Second call should return same instance
        config2 = get_config()
        assert config1 is config2

    def test_reset_config_clears_cache(self):
        """Test that reset_config clears the cached configuration."""
        # Get initial config
        config1 = get_config()

        # Reset config
        reset_config()

        # Get config again should create new instance
        config2 = get_config()
        assert config1 is not config2

    def test_get_config_with_environment_variables(self):
        """Test get_config with environment variables."""
        env_vars = {
            "SERVER_PORT": "9000",
            "DEBUG": "true",
            "DB_TYPE": "postgres",
            "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = get_config()

            assert config.port == 9000
            assert config.debug is True
            assert config.database.db_type == DatabaseType.POSTGRES
            assert config.database.dsn == "postgresql://test:test@localhost:5432/test"


class TestEnums:
    """Test cases for configuration enums."""

    def test_database_type_enum(self):
        """Test DatabaseType enum values."""
        assert DatabaseType.SQLITE.value == "sqlite"
        assert DatabaseType.POSTGRES.value == "postgres"

    def test_log_level_enum(self):
        """Test LogLevel enum values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_optimization_service_enum(self):
        """Test OptimizationService enum values."""
        assert OptimizationService.BUILTIN.value == "builtin"
        assert OptimizationService.LANGWATCH.value == "langwatch"
        assert OptimizationService.PROMPTPERFECT.value == "promptperfect"
        assert OptimizationService.LANGSMITH.value == "langsmith"
        assert OptimizationService.HELICONE.value == "helicone"

    def test_translation_service_enum(self):
        """Test TranslationService enum values."""
        assert TranslationService.MOCK.value == "mock"
        assert TranslationService.OPENAI.value == "openai"
        assert TranslationService.GOOGLE.value == "google"
        assert TranslationService.LIBRE.value == "libre"


if __name__ == "__main__":
    pytest.main([__file__])
