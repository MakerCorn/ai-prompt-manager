"""
Unit tests for the exception hierarchy.

This module tests all custom exception classes and their
behavior, error details, and dictionary conversion.
"""

import pytest

from src.core.exceptions.base import (AuthenticationException,
                                      AuthorizationException, BaseAppException,
                                      ConfigurationException,
                                      DatabaseException,
                                      ExternalServiceException,
                                      ServiceException, ValidationException)


class TestBaseAppException:
    """Test cases for BaseAppException class."""

    def test_base_exception_basic_creation(self):
        """Test basic BaseAppException creation."""
        exception = BaseAppException("Test error message")

        assert str(exception) == "Test error message"
        assert exception.message == "Test error message"
        assert exception.code is None
        assert exception.details == {}

    def test_base_exception_with_code(self):
        """Test BaseAppException creation with error code."""
        exception = BaseAppException("Test error", code="TEST_ERROR")

        assert exception.message == "Test error"
        assert exception.code == "TEST_ERROR"
        assert exception.details == {}

    def test_base_exception_with_details(self):
        """Test BaseAppException creation with details."""
        details = {"field": "name", "value": "invalid"}
        exception = BaseAppException("Test error", details=details)

        assert exception.message == "Test error"
        assert exception.code is None
        assert exception.details == details

    def test_base_exception_with_all_parameters(self):
        """Test BaseAppException creation with all parameters."""
        details = {"context": "test"}
        exception = BaseAppException(
            "Complete error", code="COMPLETE_ERROR", details=details
        )

        assert exception.message == "Complete error"
        assert exception.code == "COMPLETE_ERROR"
        assert exception.details == details

    def test_base_exception_to_dict(self):
        """Test BaseAppException conversion to dictionary."""
        details = {"field": "email"}
        exception = BaseAppException(
            "Validation failed", code="VALIDATION_ERROR", details=details
        )

        result_dict = exception.to_dict()

        assert result_dict["error"] == "BaseAppException"
        assert result_dict["message"] == "Validation failed"
        assert result_dict["code"] == "VALIDATION_ERROR"
        assert result_dict["details"] == details

    def test_base_exception_to_dict_minimal(self):
        """Test BaseAppException conversion to dictionary with minimal data."""
        exception = BaseAppException("Simple error")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "BaseAppException"
        assert result_dict["message"] == "Simple error"
        assert result_dict["code"] is None
        assert result_dict["details"] == {}

    def test_base_exception_details_default(self):
        """Test BaseAppException details default to empty dict."""
        exception = BaseAppException("Test", details=None)

        assert exception.details == {}


class TestServiceException:
    """Test cases for ServiceException class."""

    def test_service_exception_inheritance(self):
        """Test ServiceException inherits from BaseAppException."""
        exception = ServiceException("Service error")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Service error"

    def test_service_exception_with_code(self):
        """Test ServiceException with error code."""
        exception = ServiceException("Business logic error", code="BUSINESS_ERROR")

        assert exception.code == "BUSINESS_ERROR"
        assert str(exception) == "Business logic error"

    def test_service_exception_to_dict(self):
        """Test ServiceException to_dict method."""
        exception = ServiceException("Service failed", code="SERVICE_FAILED")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "ServiceException"
        assert result_dict["message"] == "Service failed"
        assert result_dict["code"] == "SERVICE_FAILED"


class TestValidationException:
    """Test cases for ValidationException class."""

    def test_validation_exception_basic(self):
        """Test basic ValidationException creation."""
        exception = ValidationException("Invalid input")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Invalid input"
        assert exception.field is None

    def test_validation_exception_with_field(self):
        """Test ValidationException with field parameter."""
        exception = ValidationException("Email is required", field="email")

        assert exception.message == "Email is required"
        assert exception.field == "email"
        assert exception.details["field"] == "email"

    def test_validation_exception_with_field_and_code(self):
        """Test ValidationException with field and code."""
        exception = ValidationException(
            "Invalid email format", field="email", code="INVALID_FORMAT"
        )

        assert exception.field == "email"
        assert exception.code == "INVALID_FORMAT"
        assert exception.details["field"] == "email"

    def test_validation_exception_to_dict(self):
        """Test ValidationException to_dict includes field."""
        exception = ValidationException("Required field missing", field="name")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "ValidationException"
        assert result_dict["details"]["field"] == "name"

    def test_validation_exception_without_field(self):
        """Test ValidationException without field parameter."""
        exception = ValidationException("General validation error")

        assert exception.field is None
        assert (
            "field" not in exception.details or exception.details.get("field") is None
        )


class TestDatabaseException:
    """Test cases for DatabaseException class."""

    def test_database_exception_inheritance(self):
        """Test DatabaseException inherits from BaseAppException."""
        exception = DatabaseException("Database connection failed")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Database connection failed"

    def test_database_exception_with_details(self):
        """Test DatabaseException with error details."""
        details = {"table": "users", "operation": "INSERT"}
        exception = DatabaseException("Insert failed", details=details)

        assert exception.details == details

    def test_database_exception_to_dict(self):
        """Test DatabaseException to_dict method."""
        exception = DatabaseException("Query timeout", code="TIMEOUT_ERROR")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "DatabaseException"
        assert result_dict["message"] == "Query timeout"
        assert result_dict["code"] == "TIMEOUT_ERROR"


class TestAuthenticationException:
    """Test cases for AuthenticationException class."""

    def test_authentication_exception_inheritance(self):
        """Test AuthenticationException inherits from BaseAppException."""
        exception = AuthenticationException("Invalid credentials")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Invalid credentials"

    def test_authentication_exception_with_code(self):
        """Test AuthenticationException with error code."""
        exception = AuthenticationException("Token expired", code="TOKEN_EXPIRED")

        assert exception.code == "TOKEN_EXPIRED"

    def test_authentication_exception_to_dict(self):
        """Test AuthenticationException to_dict method."""
        exception = AuthenticationException("Login failed")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "AuthenticationException"
        assert result_dict["message"] == "Login failed"


class TestAuthorizationException:
    """Test cases for AuthorizationException class."""

    def test_authorization_exception_basic(self):
        """Test basic AuthorizationException creation."""
        exception = AuthorizationException("Access denied")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Access denied"
        assert exception.required_permission is None

    def test_authorization_exception_with_permission(self):
        """Test AuthorizationException with required permission."""
        exception = AuthorizationException(
            "Insufficient permissions", required_permission="admin"
        )

        assert exception.message == "Insufficient permissions"
        assert exception.required_permission == "admin"
        assert exception.details["required_permission"] == "admin"

    def test_authorization_exception_with_permission_and_code(self):
        """Test AuthorizationException with permission and code."""
        exception = AuthorizationException(
            "Admin access required", required_permission="admin", code="ADMIN_REQUIRED"
        )

        assert exception.required_permission == "admin"
        assert exception.code == "ADMIN_REQUIRED"
        assert exception.details["required_permission"] == "admin"

    def test_authorization_exception_to_dict(self):
        """Test AuthorizationException to_dict includes permission."""
        exception = AuthorizationException(
            "Permission denied", required_permission="write"
        )

        result_dict = exception.to_dict()

        assert result_dict["error"] == "AuthorizationException"
        assert result_dict["details"]["required_permission"] == "write"

    def test_authorization_exception_without_permission(self):
        """Test AuthorizationException without permission parameter."""
        exception = AuthorizationException("General access denied")

        assert exception.required_permission is None
        assert (
            "required_permission" not in exception.details
            or exception.details.get("required_permission") is None
        )


class TestExternalServiceException:
    """Test cases for ExternalServiceException class."""

    def test_external_service_exception_basic(self):
        """Test basic ExternalServiceException creation."""
        exception = ExternalServiceException("External API failed")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "External API failed"
        assert exception.service_name is None

    def test_external_service_exception_with_service_name(self):
        """Test ExternalServiceException with service name."""
        exception = ExternalServiceException(
            "Service unavailable", service_name="LangWatch"
        )

        assert exception.message == "Service unavailable"
        assert exception.service_name == "LangWatch"
        assert exception.details["service_name"] == "LangWatch"

    def test_external_service_exception_with_service_and_code(self):
        """Test ExternalServiceException with service name and code."""
        exception = ExternalServiceException(
            "API rate limit exceeded", service_name="PromptPerfect", code="RATE_LIMIT"
        )

        assert exception.service_name == "PromptPerfect"
        assert exception.code == "RATE_LIMIT"
        assert exception.details["service_name"] == "PromptPerfect"

    def test_external_service_exception_to_dict(self):
        """Test ExternalServiceException to_dict includes service name."""
        exception = ExternalServiceException("Service timeout", service_name="OpenAI")

        result_dict = exception.to_dict()

        assert result_dict["error"] == "ExternalServiceException"
        assert result_dict["details"]["service_name"] == "OpenAI"

    def test_external_service_exception_without_service_name(self):
        """Test ExternalServiceException without service name parameter."""
        exception = ExternalServiceException("Unknown external error")

        assert exception.service_name is None
        assert (
            "service_name" not in exception.details
            or exception.details.get("service_name") is None
        )


class TestConfigurationException:
    """Test cases for ConfigurationException class."""

    def test_configuration_exception_inheritance(self):
        """Test ConfigurationException inherits from BaseAppException."""
        exception = ConfigurationException("Invalid configuration")

        assert isinstance(exception, BaseAppException)
        assert exception.message == "Invalid configuration"

    def test_configuration_exception_with_details(self):
        """Test ConfigurationException with configuration details."""
        details = {"setting": "DATABASE_URL", "issue": "malformed"}
        exception = ConfigurationException("Config error", details=details)

        assert exception.details == details

    def test_configuration_exception_to_dict(self):
        """Test ConfigurationException to_dict method."""
        exception = ConfigurationException(
            "Missing required setting", code="MISSING_SETTING"
        )

        result_dict = exception.to_dict()

        assert result_dict["error"] == "ConfigurationException"
        assert result_dict["message"] == "Missing required setting"
        assert result_dict["code"] == "MISSING_SETTING"


class TestExceptionHierarchy:
    """Test cases for exception hierarchy relationships."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from BaseAppException."""
        exceptions = [
            ServiceException("test"),
            ValidationException("test"),
            DatabaseException("test"),
            AuthenticationException("test"),
            AuthorizationException("test"),
            ExternalServiceException("test"),
            ConfigurationException("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, BaseAppException)
            assert isinstance(exception, Exception)

    def test_exception_names_in_to_dict(self):
        """Test that to_dict returns correct exception class names."""
        test_cases = [
            (ServiceException("test"), "ServiceException"),
            (ValidationException("test"), "ValidationException"),
            (DatabaseException("test"), "DatabaseException"),
            (AuthenticationException("test"), "AuthenticationException"),
            (AuthorizationException("test"), "AuthorizationException"),
            (ExternalServiceException("test"), "ExternalServiceException"),
            (ConfigurationException("test"), "ConfigurationException"),
        ]

        for exception, expected_name in test_cases:
            result_dict = exception.to_dict()
            assert result_dict["error"] == expected_name

    def test_all_exceptions_have_message_property(self):
        """Test that all exceptions have message property."""
        message = "Test error message"
        exceptions = [
            BaseAppException(message),
            ServiceException(message),
            ValidationException(message),
            DatabaseException(message),
            AuthenticationException(message),
            AuthorizationException(message),
            ExternalServiceException(message),
            ConfigurationException(message),
        ]

        for exception in exceptions:
            assert hasattr(exception, "message")
            assert exception.message == message
            assert str(exception) == message

    def test_all_exceptions_support_code_and_details(self):
        """Test that all exceptions support code and details parameters."""
        code = "TEST_CODE"
        details = {"key": "value"}
        exceptions = [
            BaseAppException("test", code=code, details=details),
            ServiceException("test", code=code, details=details),
            ValidationException("test", code=code, details=details),
            DatabaseException("test", code=code, details=details),
            AuthenticationException("test", code=code, details=details),
            AuthorizationException("test", code=code, details=details),
            ExternalServiceException("test", code=code, details=details),
            ConfigurationException("test", code=code, details=details),
        ]

        for exception in exceptions:
            assert exception.code == code
            assert exception.details == details


if __name__ == "__main__":
    pytest.main([__file__])
