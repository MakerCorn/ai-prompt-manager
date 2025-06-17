"""
Unit tests for the PromptService business logic layer.

This module tests the prompt service including validation,
business rules, template integration, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.prompts.services.prompt_service import PromptService
from src.prompts.models.prompt import Prompt
from src.prompts.repositories.prompt_repository import PromptRepository
from src.prompts.services.template_service import TemplateService
from src.core.base.database_manager import DatabaseManager
from src.core.base.service_base import ServiceResult
from src.core.exceptions.base import ValidationException, ServiceException


class TestPromptService:
    """Test cases for PromptService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_manager = MagicMock()
        self.mock_repository = MagicMock(spec=PromptRepository)
        self.mock_template_service = MagicMock(spec=TemplateService)
        
        # Create service with mocked dependencies
        self.service = PromptService(self.mock_db_manager)
        self.service.repository = self.mock_repository
        self.service.template_service = self.mock_template_service
    
    def test_prompt_service_initialization(self):
        """Test prompt service initialization."""
        service = PromptService(self.mock_db_manager)
        
        assert service.db_manager == self.mock_db_manager
        assert hasattr(service, 'repository')
        assert hasattr(service, 'template_service')
        assert hasattr(service, 'logger')
    
    def test_create_prompt_success(self):
        """Test successful prompt creation."""
        # Mock repository save
        created_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        self.mock_repository.save.return_value = created_prompt
        self.mock_repository.prompt_exists_by_name.return_value = False
        
        result = self.service.create_prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content',
            category='Testing',
            tags='test, unit'
        )
        
        assert result.success is True
        assert result.data.id == 1
        assert result.data.name == 'test_prompt'
        
        # Verify repository interactions
        self.mock_repository.set_tenant_context.assert_called_once_with('tenant-123')
        self.mock_repository.prompt_exists_by_name.assert_called_once_with('test_prompt')
        self.mock_repository.save.assert_called_once()
    
    def test_create_prompt_duplicate_name(self):
        """Test creating prompt with duplicate name."""
        self.mock_repository.prompt_exists_by_name.return_value = True
        
        result = self.service.create_prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='existing_prompt',
            title='Existing Prompt',
            content='Test content'
        )
        
        assert result.success is False
        assert "already exists" in result.error
        assert result.error_code == "VALIDATION_ERROR"
    
    def test_create_prompt_invalid_name(self):
        """Test creating prompt with invalid name."""
        result = self.service.create_prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='invalid@name',  # Invalid characters
            title='Test Prompt',
            content='Test content'
        )
        
        assert result.success is False
        assert "VALIDATION_ERROR" in result.error_code
    
    def test_create_prompt_empty_content(self):
        """Test creating prompt with empty content."""
        result = self.service.create_prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content=''  # Empty content
        )
        
        assert result.success is False
        assert "VALIDATION_ERROR" in result.error_code
    
    def test_create_prompt_repository_error(self):
        """Test creating prompt with repository error."""
        self.mock_repository.prompt_exists_by_name.return_value = False
        self.mock_repository.save.side_effect = Exception("Database error")
        
        result = self.service.create_prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        
        assert result.success is False
        assert "Failed to create prompt" in result.error
    
    def test_get_prompt_success(self):
        """Test successful prompt retrieval."""
        mock_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        self.mock_repository.find_by_id.return_value = mock_prompt
        
        result = self.service.get_prompt('tenant-123', 1)
        
        assert result.success is True
        assert result.data.id == 1
        assert result.data.name == 'test_prompt'
        
        self.mock_repository.set_tenant_context.assert_called_once_with('tenant-123')
        self.mock_repository.find_by_id.assert_called_once_with(1)
    
    def test_get_prompt_not_found(self):
        """Test getting non-existent prompt."""
        self.mock_repository.find_by_id.return_value = None
        
        result = self.service.get_prompt('tenant-123', 999)
        
        assert result.success is False
        assert "not found" in result.error
        assert result.error_code == "NOT_FOUND"
    
    def test_get_prompt_by_name_success(self):
        """Test successful prompt retrieval by name."""
        mock_prompt = Prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        self.mock_repository.find_by_name.return_value = mock_prompt
        
        result = self.service.get_prompt_by_name('tenant-123', 'test_prompt')
        
        assert result.success is True
        assert result.data.name == 'test_prompt'
        
        self.mock_repository.find_by_name.assert_called_once_with('test_prompt')
    
    def test_update_prompt_success(self):
        """Test successful prompt update."""
        existing_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Old Title',
            content='Old content'
        )
        updated_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='New Title',
            content='New content'
        )
        
        self.mock_repository.find_by_id.return_value = existing_prompt
        self.mock_repository.save.return_value = updated_prompt
        
        result = self.service.update_prompt(
            tenant_id='tenant-123',
            prompt_id=1,
            updates={
                'title': 'New Title',
                'content': 'New content',
                'category': 'Updated'
            }
        )
        
        assert result.success is True
        assert result.data.title == 'New Title'
        assert result.data.content == 'New content'
    
    def test_update_prompt_not_found(self):
        """Test updating non-existent prompt."""
        self.mock_repository.find_by_id.return_value = None
        
        result = self.service.update_prompt(
            tenant_id='tenant-123',
            prompt_id=999,
            updates={'title': 'New Title'}
        )
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_update_prompt_invalid_data(self):
        """Test updating prompt with invalid data."""
        existing_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        self.mock_repository.find_by_id.return_value = existing_prompt
        
        result = self.service.update_prompt(
            tenant_id='tenant-123',
            prompt_id=1,
            updates={'content': ''}  # Empty content
        )
        
        assert result.success is False
        assert "VALIDATION_ERROR" in result.error_code
    
    def test_delete_prompt_success(self):
        """Test successful prompt deletion."""
        self.mock_repository.delete.return_value = True
        
        result = self.service.delete_prompt('tenant-123', 1)
        
        assert result.success is True
        assert result.data is True
        
        self.mock_repository.set_tenant_context.assert_called_once_with('tenant-123')
        self.mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_prompt_not_found(self):
        """Test deleting non-existent prompt."""
        self.mock_repository.delete.return_value = False
        
        result = self.service.delete_prompt('tenant-123', 999)
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_search_prompts_success(self):
        """Test successful prompt search."""
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt1', title='Title 1', content='Content 1'),
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt2', title='Title 2', content='Content 2')
        ]
        self.mock_repository.search_prompts.return_value = mock_prompts
        
        result = self.service.search_prompts('tenant-123', 'search term')
        
        assert result.success is True
        assert len(result.data) == 2
        
        self.mock_repository.search_prompts.assert_called_once_with('search term')
    
    def test_search_prompts_empty_query(self):
        """Test search with empty query."""
        result = self.service.search_prompts('tenant-123', '')
        
        assert result.success is False
        assert "Search query cannot be empty" in result.error
    
    def test_get_prompts_by_category_success(self):
        """Test getting prompts by category."""
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt1', title='Title 1', content='Content 1', category='Testing')
        ]
        self.mock_repository.find_by_category.return_value = mock_prompts
        
        result = self.service.get_prompts_by_category('tenant-123', 'Testing')
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].category == 'Testing'
    
    def test_get_prompts_by_user_success(self):
        """Test getting prompts by user."""
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt1', title='Title 1', content='Content 1')
        ]
        self.mock_repository.find_by_user.return_value = mock_prompts
        
        result = self.service.get_prompts_by_user('tenant-123', 'user-456')
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].user_id == 'user-456'
    
    def test_get_recent_prompts_success(self):
        """Test getting recent prompts."""
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='recent1', title='Recent 1', content='Content 1'),
            Prompt(tenant_id='tenant-123', user_id='user-456', name='recent2', title='Recent 2', content='Content 2')
        ]
        self.mock_repository.find_recent_prompts.return_value = mock_prompts
        
        result = self.service.get_recent_prompts('tenant-123', limit=5)
        
        assert result.success is True
        assert len(result.data) == 2
        
        self.mock_repository.find_recent_prompts.assert_called_once_with(5)
    
    def test_get_categories_success(self):
        """Test getting prompt categories."""
        mock_categories = ['Testing', 'Development', 'Documentation']
        self.mock_repository.get_categories.return_value = mock_categories
        
        result = self.service.get_categories('tenant-123')
        
        assert result.success is True
        assert result.data == mock_categories
    
    def test_get_all_tags_success(self):
        """Test getting all tags."""
        mock_tags = ['test', 'development', 'documentation']
        self.mock_repository.get_all_tags.return_value = mock_tags
        
        result = self.service.get_all_tags('tenant-123')
        
        assert result.success is True
        assert result.data == mock_tags
    
    def test_clone_prompt_success(self):
        """Test successful prompt cloning."""
        original_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='original_prompt',
            title='Original Prompt',
            content='Original content'
        )
        cloned_prompt = Prompt(
            id=2,
            tenant_id='tenant-123',
            user_id='user-456',
            name='cloned_prompt',
            title='Original Prompt',
            content='Original content'
        )
        
        self.mock_repository.find_by_id.return_value = original_prompt
        self.mock_repository.prompt_exists_by_name.return_value = False
        self.mock_repository.save.return_value = cloned_prompt
        
        result = self.service.clone_prompt(
            tenant_id='tenant-123',
            prompt_id=1,
            new_name='cloned_prompt'
        )
        
        assert result.success is True
        assert result.data.name == 'cloned_prompt'
        assert result.data.id == 2
    
    def test_clone_prompt_not_found(self):
        """Test cloning non-existent prompt."""
        self.mock_repository.find_by_id.return_value = None
        
        result = self.service.clone_prompt(
            tenant_id='tenant-123',
            prompt_id=999,
            new_name='cloned_prompt'
        )
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_clone_prompt_name_exists(self):
        """Test cloning prompt with existing name."""
        original_prompt = Prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='original_prompt',
            title='Original Prompt',
            content='Original content'
        )
        
        self.mock_repository.find_by_id.return_value = original_prompt
        self.mock_repository.prompt_exists_by_name.return_value = True
        
        result = self.service.clone_prompt(
            tenant_id='tenant-123',
            prompt_id=1,
            new_name='existing_name'
        )
        
        assert result.success is False
        assert "already exists" in result.error
    
    def test_validate_prompt_data_success(self):
        """Test successful prompt data validation."""
        valid_data = {
            'name': 'valid_prompt',
            'title': 'Valid Prompt',
            'content': 'Valid content',
            'category': 'Testing',
            'tags': 'test, valid'
        }
        
        # Should not raise exception
        self.service._validate_prompt_data(valid_data)
    
    def test_validate_prompt_data_missing_required(self):
        """Test prompt data validation with missing required fields."""
        invalid_data = {
            'title': 'Missing Name',
            'content': 'Valid content'
        }
        
        with pytest.raises(ValidationException) as exc_info:
            self.service._validate_prompt_data(invalid_data)
        
        assert "Missing required fields" in str(exc_info.value)
        assert 'name' in exc_info.value.details['missing_fields']
    
    def test_validate_prompt_data_empty_strings(self):
        """Test prompt data validation with empty strings."""
        invalid_data = {
            'name': '',
            'title': 'Valid Title',
            'content': 'Valid content'
        }
        
        with pytest.raises(ValidationException) as exc_info:
            self.service._validate_prompt_data(invalid_data)
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_validate_prompt_data_invalid_name_format(self):
        """Test prompt data validation with invalid name format."""
        invalid_data = {
            'name': 'invalid@name#format',
            'title': 'Valid Title',
            'content': 'Valid content'
        }
        
        with pytest.raises(ValidationException) as exc_info:
            self.service._validate_prompt_data(invalid_data)
        
        assert "invalid format" in str(exc_info.value)
    
    def test_validate_prompt_data_long_strings(self):
        """Test prompt data validation with overly long strings."""
        invalid_data = {
            'name': 'a' * 201,  # Too long
            'title': 'Valid Title',
            'content': 'Valid content'
        }
        
        with pytest.raises(ValidationException) as exc_info:
            self.service._validate_prompt_data(invalid_data)
        
        assert "too long" in str(exc_info.value)
    
    def test_apply_template_to_prompt_success(self):
        """Test applying template to prompt."""
        prompt_data = {
            'content': 'Test content',
            'category': 'Testing',
            'tags': 'test, template'
        }
        template_result = 'Templated content with Test content'
        
        self.mock_template_service.apply_template.return_value = template_result
        
        result = self.service.apply_template_to_prompt(prompt_data, 'default_template')
        
        assert result.success is True
        assert result.data == template_result
        
        self.mock_template_service.apply_template.assert_called_once_with(
            'default_template',
            prompt_data
        )
    
    def test_apply_template_to_prompt_template_error(self):
        """Test applying template with template service error."""
        prompt_data = {
            'content': 'Test content',
            'category': 'Testing'
        }
        
        self.mock_template_service.apply_template.side_effect = Exception("Template error")
        
        result = self.service.apply_template_to_prompt(prompt_data, 'invalid_template')
        
        assert result.success is False
        assert "Failed to apply template" in result.error
    
    def test_enhance_prompt_with_template_success(self):
        """Test enhancing prompt with template."""
        original_prompt = 'Original prompt content'
        enhancement_instructions = 'Make it more detailed'
        enhanced_result = 'Enhanced prompt content with more details'
        
        template_data = {
            'original_prompt': original_prompt,
            'enhancement_instructions': enhancement_instructions,
            'target_model': 'gpt-4'
        }
        
        self.mock_template_service.apply_template.return_value = enhanced_result
        
        result = self.service.enhance_prompt_with_template(
            original_prompt,
            enhancement_instructions,
            'gpt-4'
        )
        
        assert result.success is True
        assert result.data == enhanced_result
        
        self.mock_template_service.apply_template.assert_called_once_with(
            'enhancement_template',
            template_data
        )
    
    def test_get_prompt_statistics_success(self):
        """Test getting prompt statistics."""
        self.mock_repository.count.return_value = 10
        self.mock_repository.count_by_category.return_value = 5
        self.mock_repository.count_by_user.return_value = 3
        self.mock_repository.get_categories.return_value = ['Cat1', 'Cat2']
        
        result = self.service.get_prompt_statistics('tenant-123', 'user-456')
        
        assert result.success is True
        assert result.data['total_prompts'] == 10
        assert result.data['total_categories'] == 2
        assert 'prompts_by_user' in result.data
    
    def test_service_error_handling(self):
        """Test service error handling."""
        self.mock_repository.find_by_id.side_effect = Exception("Unexpected error")
        
        result = self.service.get_prompt('tenant-123', 1)
        
        assert result.success is False
        assert "Failed to get prompt" in result.error
        assert result.error_code == "INTERNAL_ERROR"
    
    def test_service_logging_operations(self):
        """Test that service logs operations."""
        created_prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        self.mock_repository.save.return_value = created_prompt
        self.mock_repository.prompt_exists_by_name.return_value = False
        
        with patch.object(self.service, 'log_operation') as mock_log:
            self.service.create_prompt(
                tenant_id='tenant-123',
                user_id='user-456',
                name='test_prompt',
                title='Test Prompt',
                content='Test content'
            )
            
            mock_log.assert_called()
            call_args = mock_log.call_args
            assert 'create prompt' in call_args[0][0]
            assert call_args[1]['user_id'] == 'user-456'
            assert call_args[1]['tenant_id'] == 'tenant-123'


if __name__ == '__main__':
    pytest.main([__file__])