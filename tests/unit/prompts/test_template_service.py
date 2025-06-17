"""
Unit tests for the TemplateService.

This module tests template loading, validation, variable substitution,
and template management functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from src.prompts.services.template_service import TemplateService
from src.core.base.service_base import ServiceResult
from src.core.exceptions.base import ServiceException, ConfigurationException


class TestTemplateService:
    """Test cases for TemplateService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TemplateService()
        # Clear cache between tests
        self.service._template_cache.clear()
    
    def test_template_service_initialization(self):
        """Test template service initialization."""
        service = TemplateService()
        
        assert hasattr(service, 'config')
        assert hasattr(service, 'templates_dir')
        assert hasattr(service, '_template_cache')
        assert hasattr(service, 'default_templates')
        assert isinstance(service._template_cache, dict)
    
    def test_default_templates_mapping(self):
        """Test default template mappings."""
        expected_templates = {
            "default": "default_prompt_template.txt",
            "enhancement": "enhancement_template.txt",
            "business": "business_template.txt",
            "technical": "technical_template.txt",
            "creative": "creative_template.txt",
            "analytical": "analytical_template.txt"
        }
        
        assert self.service.default_templates == expected_templates
    
    @patch('builtins.open', new_callable=mock_open, read_data='Test template content with {variable}')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_template_success(self, mock_exists, mock_file):
        """Test successful template loading."""
        result = self.service.load_template('default')
        
        assert result.success is True
        assert result.data == 'Test template content with {variable}'
        
        # Verify file was opened correctly
        mock_file.assert_called_once()
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_load_template_not_found(self, mock_exists):
        """Test loading non-existent template."""
        result = self.service.load_template('nonexistent')
        
        assert result.success is False
        assert "not found" in result.error
    
    @patch('builtins.open', side_effect=IOError("File read error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_template_read_error(self, mock_exists, mock_file):
        """Test template loading with file read error."""
        result = self.service.load_template('default')
        
        assert result.success is False
        assert "Failed to load template" in result.error
    
    @patch('builtins.open', new_callable=mock_open, read_data='Cached template content')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_template_caching(self, mock_exists, mock_file):
        """Test template caching functionality."""
        # First load
        result1 = self.service.load_template('default')
        assert result1.success is True
        assert result1.data == 'Cached template content'
        
        # Second load should use cache
        result2 = self.service.load_template('default')
        assert result2.success is True
        assert result2.data == 'Cached template content'
        
        # File should only be opened once due to caching
        mock_file.assert_called_once()
    
    def test_get_template_path_default(self):
        """Test getting template path for default templates."""
        path = self.service.get_template_path('default')
        
        assert path.name == 'default_prompt_template.txt'
        assert 'templates' in str(path)
    
    def test_get_template_path_custom(self):
        """Test getting template path for custom templates."""
        path = self.service.get_template_path('my_custom_template.txt')
        
        assert path.name == 'my_custom_template.txt'
        assert 'templates' in str(path)
    
    def test_get_template_path_invalid_name(self):
        """Test getting template path with invalid name."""
        with pytest.raises(ValueError) as exc_info:
            self.service.get_template_path('')
        
        assert "Template name cannot be empty" in str(exc_info.value)
    
    def test_apply_template_success(self):
        """Test successful template application."""
        template_content = "Hello {name}, your category is {category} and tags are {tags}."
        variables = {
            'name': 'World',
            'category': 'Testing',
            'tags': 'test, unit'
        }
        
        with patch.object(self.service, 'load_template') as mock_load:
            mock_load.return_value = ServiceResult.success_result(template_content)
            
            result = self.service.apply_template('test_template', variables)
            
            assert result.success is True
            assert result.data == "Hello World, your category is Testing and tags are test, unit."
    
    def test_apply_template_load_failure(self):
        """Test template application with load failure."""
        variables = {'name': 'World'}
        
        with patch.object(self.service, 'load_template') as mock_load:
            mock_load.return_value = ServiceResult.error_result("Template not found")
            
            result = self.service.apply_template('nonexistent', variables)
            
            assert result.success is False
            assert "Template not found" in result.error
    
    def test_apply_template_substitution_error(self):
        """Test template application with substitution error."""
        template_content = "Hello {name}, your missing is {missing_var}."
        variables = {'name': 'World'}  # missing_var not provided
        
        with patch.object(self.service, 'load_template') as mock_load:
            mock_load.return_value = ServiceResult.success_result(template_content)
            
            result = self.service.apply_template('test_template', variables)
            
            assert result.success is False
            assert "Template substitution failed" in result.error
    
    def test_apply_template_with_defaults(self):
        """Test template application with default values."""
        template_content = "Content: {content}, Category: {category}, User: {user_context}"
        variables = {
            'content': 'Test content',
            'category': 'Testing'
        }
        
        with patch.object(self.service, 'load_template') as mock_load:
            mock_load.return_value = ServiceResult.success_result(template_content)
            
            result = self.service.apply_template('test_template', variables)
            
            # Should use default values for missing variables
            assert result.success is True
            assert "User: " in result.data  # Default empty value
    
    def test_validate_template_success(self):
        """Test successful template validation."""
        valid_template = "This is a valid template with {variable} and {another}."
        
        result = self.service.validate_template(valid_template)
        
        assert result.success is True
        assert result.data['is_valid'] is True
        assert 'variable' in result.data['variables']
        assert 'another' in result.data['variables']
    
    def test_validate_template_no_variables(self):
        """Test template validation with no variables."""
        template = "This template has no variables."
        
        result = self.service.validate_template(template)
        
        assert result.success is True
        assert result.data['is_valid'] is True
        assert len(result.data['variables']) == 0
    
    def test_validate_template_empty(self):
        """Test template validation with empty template."""
        result = self.service.validate_template("")
        
        assert result.success is False
        assert "cannot be empty" in result.error
    
    def test_validate_template_invalid_syntax(self):
        """Test template validation with invalid syntax."""
        invalid_template = "Invalid template with {unclosed variable"
        
        result = self.service.validate_template(invalid_template)
        
        assert result.success is False
        assert "Invalid template syntax" in result.error
    
    def test_get_available_templates(self):
        """Test getting available templates."""
        mock_files = [
            'default_prompt_template.txt',
            'custom_template.txt',
            'another_template.txt',
            'not_a_template.md'  # Should be excluded
        ]
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir') as mock_iterdir:
                mock_files_obj = [Path(f) for f in mock_files]
                mock_iterdir.return_value = mock_files_obj
                
                result = self.service.get_available_templates()
                
                assert result.success is True
                templates = result.data
                
                # Should include .txt files
                assert 'default_prompt_template.txt' in templates
                assert 'custom_template.txt' in templates
                assert 'another_template.txt' in templates
                # Should exclude non-.txt files
                assert 'not_a_template.md' not in templates
    
    def test_get_available_templates_directory_not_exists(self):
        """Test getting available templates when directory doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            result = self.service.get_available_templates()
            
            assert result.success is True
            assert result.data == []
    
    def test_create_custom_template_success(self):
        """Test successful custom template creation."""
        template_content = "Custom template with {variable}"
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pathlib.Path.exists', return_value=False):  # File doesn't exist
                result = self.service.create_custom_template('custom_template.txt', template_content)
                
                assert result.success is True
                
                # Verify file was written
                mock_file.assert_called_once()
                handle = mock_file()
                handle.write.assert_called_once_with(template_content)
    
    def test_create_custom_template_already_exists(self):
        """Test creating custom template when file already exists."""
        template_content = "Custom template"
        
        with patch('pathlib.Path.exists', return_value=True):
            result = self.service.create_custom_template('existing_template.txt', template_content)
            
            assert result.success is False
            assert "already exists" in result.error
    
    def test_create_custom_template_write_error(self):
        """Test creating custom template with write error."""
        template_content = "Custom template"
        
        with patch('builtins.open', side_effect=IOError("Write error")):
            with patch('pathlib.Path.exists', return_value=False):
                result = self.service.create_custom_template('template.txt', template_content)
                
                assert result.success is False
                assert "Failed to create template" in result.error
    
    def test_delete_custom_template_success(self):
        """Test successful custom template deletion."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink') as mock_unlink:
                result = self.service.delete_custom_template('custom_template.txt')
                
                assert result.success is True
                mock_unlink.assert_called_once()
    
    def test_delete_custom_template_not_found(self):
        """Test deleting non-existent template."""
        with patch('pathlib.Path.exists', return_value=False):
            result = self.service.delete_custom_template('nonexistent.txt')
            
            assert result.success is False
            assert "not found" in result.error
    
    def test_delete_custom_template_default(self):
        """Test deleting default template (should fail)."""
        result = self.service.delete_custom_template('default_prompt_template.txt')
        
        assert result.success is False
        assert "Cannot delete default template" in result.error
    
    def test_delete_custom_template_error(self):
        """Test deleting template with file system error."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink', side_effect=OSError("Delete error")):
                result = self.service.delete_custom_template('template.txt')
                
                assert result.success is False
                assert "Failed to delete template" in result.error
    
    def test_get_template_variables_success(self):
        """Test getting template variables."""
        template_content = "Template with {var1} and {var2} and {var1} again."
        
        variables = self.service._get_template_variables(template_content)
        
        # Should return unique variables
        assert set(variables) == {'var1', 'var2'}
    
    def test_get_template_variables_no_variables(self):
        """Test getting variables from template with none."""
        template_content = "Template with no variables."
        
        variables = self.service._get_template_variables(template_content)
        
        assert variables == []
    
    def test_get_template_variables_complex(self):
        """Test getting variables from complex template."""
        template_content = """
        Title: {title}
        Content: {content}
        Category: {category}
        Tags: {tags}
        User Context: {user_context}
        """
        
        variables = self.service._get_template_variables(template_content)
        
        expected_vars = {'title', 'content', 'category', 'tags', 'user_context'}
        assert set(variables) == expected_vars
    
    def test_substitute_variables_with_defaults(self):
        """Test variable substitution with default values."""
        template_content = "Hello {name}, category: {category}, tags: {tags}"
        variables = {'name': 'World', 'category': 'Test'}  # tags missing
        
        result = self.service._substitute_variables(template_content, variables)
        
        # Should substitute known variables and provide defaults for missing ones
        assert "Hello World" in result
        assert "category: Test" in result
        assert "tags: " in result  # Default empty value
    
    def test_substitute_variables_all_provided(self):
        """Test variable substitution with all variables provided."""
        template_content = "Name: {name}, Age: {age}"
        variables = {'name': 'John', 'age': '30'}
        
        result = self.service._substitute_variables(template_content, variables)
        
        assert result == "Name: John, Age: 30"
    
    def test_get_default_variable_value(self):
        """Test getting default values for variables."""
        # Test known variables
        assert self.service._get_default_variable_value('content') == ''
        assert self.service._get_default_variable_value('category') == 'Uncategorized'
        assert self.service._get_default_variable_value('tags') == ''
        assert self.service._get_default_variable_value('user_context') == ''
        
        # Test unknown variable
        assert self.service._get_default_variable_value('unknown_var') == ''
    
    def test_template_service_error_handling(self):
        """Test error handling in template service."""
        with patch.object(self.service, 'load_template', side_effect=Exception("Unexpected error")):
            result = self.service.apply_template('test_template', {})
            
            assert result.success is False
            assert "Failed to apply template" in result.error
    
    def test_clear_template_cache(self):
        """Test clearing template cache."""
        # Add something to cache
        self.service._template_cache['test'] = 'cached content'
        assert len(self.service._template_cache) == 1
        
        self.service.clear_template_cache()
        
        assert len(self.service._template_cache) == 0
    
    @patch('os.getenv')
    def test_template_service_with_environment_config(self, mock_getenv):
        """Test template service respects environment configuration."""
        mock_getenv.side_effect = lambda key, default=None: {
            'PROMPT_TEMPLATE': '/custom/path/custom_template.txt',
            'ENHANCEMENT_TEMPLATE': '/custom/path/enhancement_template.txt'
        }.get(key, default)
        
        service = TemplateService()
        
        # Verify service initializes with environment configuration
        assert hasattr(service, 'config')


class TestTemplateServiceIntegration:
    """Integration tests for TemplateService with real file operations."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = TemplateService()
        # Override templates directory for testing
        self.service.templates_dir = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_real_template_operations(self):
        """Test real template file operations."""
        # Create a test template file
        template_content = "Hello {name}, your task is to work on {category} with tags: {tags}"
        template_path = Path(self.temp_dir) / "test_template.txt"
        
        with open(template_path, 'w') as f:
            f.write(template_content)
        
        # Test loading
        result = self.service.load_template('test_template.txt')
        assert result.success is True
        assert result.data == template_content
        
        # Test application
        variables = {
            'name': 'Developer',
            'category': 'Testing', 
            'tags': 'unit, integration'
        }
        
        apply_result = self.service.apply_template('test_template.txt', variables)
        assert apply_result.success is True
        expected = "Hello Developer, your task is to work on Testing with tags: unit, integration"
        assert apply_result.data == expected
        
        # Test validation
        validate_result = self.service.validate_template(template_content)
        assert validate_result.success is True
        assert set(validate_result.data['variables']) == {'name', 'category', 'tags'}
    
    def test_real_custom_template_creation_and_deletion(self):
        """Test real custom template creation and deletion."""
        template_content = "Custom template for {purpose} with {details}"
        
        # Create custom template
        create_result = self.service.create_custom_template('my_custom.txt', template_content)
        assert create_result.success is True
        
        # Verify file exists
        template_path = Path(self.temp_dir) / "my_custom.txt"
        assert template_path.exists()
        
        # Verify content
        with open(template_path, 'r') as f:
            content = f.read()
        assert content == template_content
        
        # Test loading the created template
        load_result = self.service.load_template('my_custom.txt')
        assert load_result.success is True
        assert load_result.data == template_content
        
        # Delete the template
        delete_result = self.service.delete_custom_template('my_custom.txt')
        assert delete_result.success is True
        
        # Verify file is deleted
        assert not template_path.exists()
    
    def test_real_get_available_templates(self):
        """Test getting available templates with real files."""
        # Create test template files
        template_files = [
            'template1.txt',
            'template2.txt', 
            'not_template.md',
            'template3.txt'
        ]
        
        for filename in template_files:
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(f"Content of {filename}")
        
        # Get available templates
        result = self.service.get_available_templates()
        assert result.success is True
        
        templates = result.data
        
        # Should include .txt files
        assert 'template1.txt' in templates
        assert 'template2.txt' in templates 
        assert 'template3.txt' in templates
        
        # Should exclude non-.txt files
        assert 'not_template.md' not in templates


if __name__ == '__main__':
    pytest.main([__file__])