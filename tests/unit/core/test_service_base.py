"""
Unit tests for the BaseService and service layer functionality.

This module tests the base service class, ServiceResult, and all
service layer patterns including error handling and validation.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.core.base.service_base import (
    BaseService, ServiceResult, TenantAwareService, CachedService
)
from src.core.exceptions.base import (
    ServiceException, ValidationException
)


class TestServiceResult:
    """Test cases for ServiceResult class."""
    
    def test_service_result_success_creation(self):
        """Test creating successful ServiceResult."""
        data = {'id': 1, 'name': 'test'}
        result = ServiceResult.success_result(data)
        
        assert result.success is True
        assert result.data == data
        assert result.error is None
        assert result.error_code is None
        assert result.details is None
    
    def test_service_result_error_creation(self):
        """Test creating error ServiceResult."""
        error_msg = "Something went wrong"
        error_code = "TEST_ERROR"
        details = {'field': 'name'}
        
        result = ServiceResult.error_result(error_msg, error_code, details)
        
        assert result.success is False
        assert result.data is None
        assert result.error == error_msg
        assert result.error_code == error_code
        assert result.details == details
    
    def test_service_result_to_dict_success(self):
        """Test converting successful ServiceResult to dictionary."""
        data = {'id': 1, 'name': 'test'}
        result = ServiceResult.success_result(data)
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['data'] == data
        assert 'timestamp' in result_dict
        assert 'error' not in result_dict
    
    def test_service_result_to_dict_error(self):
        """Test converting error ServiceResult to dictionary."""
        error_msg = "Test error"
        error_code = "TEST_ERROR"
        details = {'info': 'additional info'}
        
        result = ServiceResult.error_result(error_msg, error_code, details)
        result_dict = result.to_dict()
        
        assert result_dict['success'] is False
        assert result_dict['error'] == error_msg
        assert result_dict['error_code'] == error_code
        assert result_dict['details'] == details
        assert 'timestamp' in result_dict
        assert 'data' not in result_dict
    
    def test_service_result_to_dict_minimal_error(self):
        """Test converting minimal error ServiceResult to dictionary."""
        result = ServiceResult.error_result("Simple error")
        result_dict = result.to_dict()
        
        assert result_dict['success'] is False
        assert result_dict['error'] == "Simple error"
        assert 'error_code' not in result_dict
        assert 'details' not in result_dict


class ConcreteService(BaseService):
    """Concrete service implementation for testing."""
    
    def test_operation(self, data):
        """Test operation that may succeed or fail."""
        if data.get('fail'):
            raise ValueError("Test failure")
        return data


class TestBaseService:
    """Test cases for BaseService class."""
    
    def test_base_service_initialization(self):
        """Test BaseService initialization."""
        service = ConcreteService()
        
        assert hasattr(service, 'logger')
        assert service.logger.name == 'ConcreteService'
    
    def test_base_service_custom_logger_name(self):
        """Test BaseService initialization with custom logger name."""
        service = ConcreteService(logger_name='CustomLogger')
        
        assert service.logger.name == 'CustomLogger'
    
    def test_handle_error_validation_exception(self):
        """Test error handling for ValidationException."""
        service = ConcreteService()
        error = ValidationException("Invalid input", field="name")
        
        result = service.handle_error("test operation", error)
        
        assert result.success is False
        assert "Failed to test operation" in result.error
        assert result.error_code == "VALIDATION_ERROR"
    
    def test_handle_error_service_exception(self):
        """Test error handling for ServiceException."""
        service = ConcreteService()
        error = ServiceException("Business logic error")
        
        result = service.handle_error("test operation", error)
        
        assert result.success is False
        assert "Failed to test operation" in result.error
        assert result.error_code == "SERVICE_ERROR"
    
    def test_handle_error_generic_exception(self):
        """Test error handling for generic exceptions."""
        service = ConcreteService()
        error = ValueError("Generic error")
        
        result = service.handle_error("test operation", error)
        
        assert result.success is False
        assert "Failed to test operation" in result.error
        assert result.error_code == "INTERNAL_ERROR"
    
    def test_handle_error_with_details(self):
        """Test error handling with additional details."""
        service = ConcreteService()
        error = ValueError("Test error")
        details = {'context': 'test context'}
        
        result = service.handle_error("test operation", error, details)
        
        assert result.details == details
    
    def test_validate_required_fields_success(self):
        """Test successful required fields validation."""
        service = ConcreteService()
        data = {'name': 'test', 'email': 'test@example.com'}
        required_fields = ['name', 'email']
        
        # Should not raise exception
        service.validate_required_fields(data, required_fields)
    
    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing fields."""
        service = ConcreteService()
        data = {'name': 'test'}
        required_fields = ['name', 'email', 'age']
        
        with pytest.raises(ValidationException) as exc_info:
            service.validate_required_fields(data, required_fields)
        
        assert "Missing required fields" in str(exc_info.value)
        assert exc_info.value.details['missing_fields'] == ['email', 'age']
    
    def test_validate_required_fields_none_values(self):
        """Test required fields validation with None values."""
        service = ConcreteService()
        data = {'name': 'test', 'email': None}
        required_fields = ['name', 'email']
        
        with pytest.raises(ValidationException) as exc_info:
            service.validate_required_fields(data, required_fields)
        
        assert 'email' in exc_info.value.details['missing_fields']
    
    def test_validate_field_types_success(self):
        """Test successful field type validation."""
        service = ConcreteService()
        data = {'name': 'test', 'age': 25, 'active': True}
        field_types = {'name': str, 'age': int, 'active': bool}
        
        # Should not raise exception
        service.validate_field_types(data, field_types)
    
    def test_validate_field_types_failure(self):
        """Test field type validation with incorrect types."""
        service = ConcreteService()
        data = {'name': 'test', 'age': '25', 'active': 'true'}
        field_types = {'name': str, 'age': int, 'active': bool}
        
        with pytest.raises(ValidationException) as exc_info:
            service.validate_field_types(data, field_types)
        
        assert "Type validation errors" in str(exc_info.value)
        assert len(exc_info.value.details['type_errors']) == 2
    
    def test_validate_field_types_none_values_ignored(self):
        """Test field type validation ignores None values."""
        service = ConcreteService()
        data = {'name': 'test', 'age': None}
        field_types = {'name': str, 'age': int}
        
        # Should not raise exception for None values
        service.validate_field_types(data, field_types)
    
    def test_validate_string_length_success(self):
        """Test successful string length validation."""
        service = ConcreteService()
        
        # Should not raise exceptions
        service.validate_string_length("test", "name", min_length=2, max_length=10)
        service.validate_string_length("hello", "name", min_length=5)
        service.validate_string_length("hi", "name", max_length=5)
    
    def test_validate_string_length_too_short(self):
        """Test string length validation with too short string."""
        service = ConcreteService()
        
        with pytest.raises(ValidationException) as exc_info:
            service.validate_string_length("a", "name", min_length=3)
        
        assert "must be at least 3 characters long" in str(exc_info.value)
        assert exc_info.value.field == "name"
    
    def test_validate_string_length_too_long(self):
        """Test string length validation with too long string."""
        service = ConcreteService()
        
        with pytest.raises(ValidationException) as exc_info:
            service.validate_string_length("toolongtext", "name", max_length=5)
        
        assert "must be no more than 5 characters long" in str(exc_info.value)
        assert exc_info.value.field == "name"
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        service = ConcreteService()
        data = {
            'name': '  John Doe  ',
            'description': 'Test with <script>alert("xss")</script> content',
            'age': 25
        }
        
        sanitized = service.sanitize_input(data)
        
        assert sanitized['name'] == 'John Doe'
        assert '<script>' not in sanitized['description']
        assert '&lt;' in sanitized['description']
        assert sanitized['age'] == 25
    
    def test_log_operation(self):
        """Test operation logging."""
        service = ConcreteService()
        
        with patch.object(service.logger, 'info') as mock_info:
            service.log_operation(
                "test operation",
                user_id="user123",
                tenant_id="tenant456",
                details={'key': 'value'}
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "Operation: test operation" in call_args[0][0]
            assert call_args[1]['extra']['user_id'] == "user123"
            assert call_args[1]['extra']['tenant_id'] == "tenant456"
    
    def test_paginate_results(self):
        """Test result pagination."""
        service = ConcreteService()
        items = list(range(100))  # 100 items
        
        # Test first page
        result = service.paginate_results(items, page=1, per_page=10)
        
        assert len(result['items']) == 10
        assert result['items'] == list(range(10))
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 10
        assert result['pagination']['total_items'] == 100
        assert result['pagination']['total_pages'] == 10
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is False
        
        # Test middle page
        result = service.paginate_results(items, page=5, per_page=10)
        
        assert result['items'] == list(range(40, 50))
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is True
        
        # Test last page
        result = service.paginate_results(items, page=10, per_page=10)
        
        assert result['items'] == list(range(90, 100))
        assert result['pagination']['has_next'] is False
        assert result['pagination']['has_prev'] is True
    
    def test_format_response(self):
        """Test response formatting."""
        service = ConcreteService()
        data = {'id': 1, 'name': 'test'}
        
        # Without message
        result = service.format_response(data)
        assert result.success is True
        assert result.data == data
        assert result.details is None
        
        # With message
        result = service.format_response(data, "Operation successful")
        assert result.success is True
        assert result.data == data
        assert result.details['message'] == "Operation successful"


class TestTenantAwareService:
    """Test cases for TenantAwareService class."""
    
    def test_tenant_aware_service_initialization(self):
        """Test TenantAwareService initialization."""
        service = TenantAwareService()
        
        assert service.current_tenant_id is None
        assert service.current_user_id is None
        assert hasattr(service, 'logger')
    
    def test_set_context(self):
        """Test setting tenant and user context."""
        service = TenantAwareService()
        
        service.set_context("tenant123", "user456")
        
        assert service.current_tenant_id == "tenant123"
        assert service.current_user_id == "user456"
    
    def test_ensure_tenant_context_success(self):
        """Test successful tenant context check."""
        service = TenantAwareService()
        service.set_context("tenant123", "user456")
        
        # Should not raise exception
        service.ensure_tenant_context()
    
    def test_ensure_tenant_context_failure(self):
        """Test tenant context check failure."""
        service = TenantAwareService()
        
        with pytest.raises(ServiceException) as exc_info:
            service.ensure_tenant_context()
        
        assert "Tenant context not set" in str(exc_info.value)
        assert exc_info.value.code == "MISSING_TENANT_CONTEXT"
    
    def test_validate_tenant_access_success(self):
        """Test successful tenant access validation."""
        service = TenantAwareService()
        service.set_context("tenant123", "user456")
        
        # Should not raise exception
        service.validate_tenant_access("tenant123")
    
    def test_validate_tenant_access_failure(self):
        """Test tenant access validation failure."""
        service = TenantAwareService()
        service.set_context("tenant123", "user456")
        
        with pytest.raises(ServiceException) as exc_info:
            service.validate_tenant_access("tenant999")
        
        assert "Access denied" in str(exc_info.value)
        assert exc_info.value.code == "TENANT_ACCESS_DENIED"
    
    def test_get_tenant_filter(self):
        """Test getting tenant filter for queries."""
        service = TenantAwareService()
        service.set_context("tenant123", "user456")
        
        filter_dict = service.get_tenant_filter()
        
        assert filter_dict == {'tenant_id': 'tenant123'}
    
    def test_get_tenant_filter_no_context(self):
        """Test getting tenant filter without context."""
        service = TenantAwareService()
        
        with pytest.raises(ServiceException):
            service.get_tenant_filter()


class TestCachedService:
    """Test cases for CachedService class."""
    
    def test_cached_service_initialization(self):
        """Test CachedService initialization."""
        service = CachedService(cache_ttl=600)
        
        assert service.cache_ttl == 600
        assert service.cache == {}
        assert service.cache_timestamps == {}
    
    def test_get_cache_key(self):
        """Test cache key generation."""
        service = CachedService()
        
        key = service._get_cache_key("arg1", "arg2", param1="value1", param2="value2")
        
        assert "arg1" in key
        assert "arg2" in key
        assert "param1=value1" in key
        assert "param2=value2" in key
    
    def test_cache_operations(self):
        """Test cache set and get operations."""
        service = CachedService()
        
        # Set cache value
        service.set_cached("test_key", "test_value")
        
        # Get cache value
        value = service.get_cached("test_key")
        assert value == "test_value"
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        service = CachedService(cache_ttl=0.1)  # 0.1 seconds
        
        # Set cache value
        service.set_cached("test_key", "test_value")
        
        # Should be available immediately
        assert service.get_cached("test_key") == "test_value"
        
        # Mock expired timestamp
        with patch('src.core.base.service_base.datetime') as mock_datetime:
            # Simulate time passage
            mock_datetime.utcnow.return_value = datetime.utcnow()
            service.cache_timestamps["test_key"] = datetime.utcnow()
            
            # Mock future time (expired)
            from datetime import timedelta
            future_time = datetime.utcnow() + timedelta(seconds=1)
            mock_datetime.utcnow.return_value = future_time
            
            # Should return None for expired item
            assert service.get_cached("test_key") is None
            
            # Cache should be cleaned up
            assert "test_key" not in service.cache
            assert "test_key" not in service.cache_timestamps
    
    def test_cache_validity_check(self):
        """Test cache validity checking."""
        service = CachedService(cache_ttl=300)
        
        # Non-existent key
        assert service._is_cache_valid("nonexistent") is False
        
        # Set a value
        service.set_cached("test_key", "test_value")
        
        # Should be valid immediately
        assert service._is_cache_valid("test_key") is True
    
    def test_clear_cache(self):
        """Test cache clearing."""
        service = CachedService()
        
        # Set multiple cache values
        service.set_cached("key1", "value1")
        service.set_cached("key2", "value2")
        
        assert len(service.cache) == 2
        assert len(service.cache_timestamps) == 2
        
        # Clear cache
        service.clear_cache()
        
        assert len(service.cache) == 0
        assert len(service.cache_timestamps) == 0


if __name__ == '__main__':
    pytest.main([__file__])