"""
Unit tests for the PromptRepository data access layer.

This module tests the prompt repository including CRUD operations,
tenant isolation, database table creation, and search functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.prompts.repositories.prompt_repository import PromptRepository
from src.prompts.models.prompt import Prompt
from src.core.base.database_manager import DatabaseManager
from src.core.config.settings import DatabaseConfig, DatabaseType
from src.core.exceptions.base import DatabaseException


class TestPromptRepository:
    """Test cases for PromptRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.config.db_type.value = "sqlite"
        self.repository = PromptRepository(self.mock_db_manager)
    
    def test_prompt_repository_initialization(self):
        """Test prompt repository initialization."""
        assert self.repository.db_manager == self.mock_db_manager
        assert self.repository.table_name == 'prompts'
        assert hasattr(self.repository, 'logger')
        assert self.repository.current_tenant_id is None
    
    @patch.object(PromptRepository, '_ensure_tables_exist')
    def test_repository_calls_table_creation(self, mock_ensure_tables):
        """Test that repository calls table creation on initialization."""
        PromptRepository(self.mock_db_manager)
        mock_ensure_tables.assert_called_once()
    
    def test_ensure_tables_exist_sqlite(self):
        """Test table creation for SQLite."""
        self.mock_db_manager.config.db_type.value = "sqlite"
        
        self.repository._ensure_tables_exist()
        
        # Should call execute_query for both prompts and config tables
        assert self.mock_db_manager.execute_query.call_count == 2
        
        # Check that SQLite table creation SQL was called
        calls = self.mock_db_manager.execute_query.call_args_list
        prompts_call = calls[0][0][0]
        config_call = calls[1][0][0]
        
        assert "CREATE TABLE IF NOT EXISTS prompts" in prompts_call
        assert "CREATE TABLE IF NOT EXISTS config" in config_call
        assert "INTEGER PRIMARY KEY AUTOINCREMENT" in prompts_call
    
    def test_ensure_tables_exist_postgres(self):
        """Test table creation for PostgreSQL."""
        self.mock_db_manager.config.db_type.value = "postgres"
        
        self.repository._ensure_tables_exist()
        
        # Should call execute_query for both tables
        assert self.mock_db_manager.execute_query.call_count == 2
        
        # Check that PostgreSQL table creation SQL was called
        calls = self.mock_db_manager.execute_query.call_args_list
        prompts_call = calls[0][0][0]
        
        assert "CREATE TABLE IF NOT EXISTS prompts" in prompts_call
        assert "SERIAL PRIMARY KEY" in prompts_call
        assert "UUID" in prompts_call
    
    def test_row_to_entity_conversion(self):
        """Test converting database row to Prompt entity."""
        row = {
            'id': 1,
            'tenant_id': 'tenant-123',
            'user_id': 'user-456',
            'name': 'test_prompt',
            'title': 'Test Prompt',
            'content': 'Test content',
            'category': 'Testing',
            'tags': 'test, unit',
            'is_enhancement_prompt': True,
            'created_at': datetime(2023, 1, 1, 12, 0, 0),
            'updated_at': datetime(2023, 1, 1, 13, 0, 0)
        }
        
        prompt = self.repository._row_to_entity(row)
        
        assert isinstance(prompt, Prompt)
        assert prompt.id == 1
        assert prompt.tenant_id == 'tenant-123'
        assert prompt.user_id == 'user-456'
        assert prompt.name == 'test_prompt'
        assert prompt.title == 'Test Prompt'
        assert prompt.content == 'Test content'
        assert prompt.category == 'Testing'
        assert prompt.tags == 'test, unit'
        assert prompt.is_enhancement_prompt is True
        assert prompt.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert prompt.updated_at == datetime(2023, 1, 1, 13, 0, 0)
    
    def test_entity_to_dict_conversion(self):
        """Test converting Prompt entity to dictionary."""
        prompt = Prompt(
            id=1,
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content',
            category='Testing',
            tags='test, unit',
            is_enhancement_prompt=True,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 13, 0, 0)
        )
        
        result_dict = self.repository._entity_to_dict(prompt)
        
        assert result_dict['id'] == 1
        assert result_dict['tenant_id'] == 'tenant-123'
        assert result_dict['user_id'] == 'user-456'
        assert result_dict['name'] == 'test_prompt'
        assert result_dict['title'] == 'Test Prompt'
        assert result_dict['content'] == 'Test content'
        assert result_dict['category'] == 'Testing'
        assert result_dict['tags'] == 'test, unit'
        assert result_dict['is_enhancement_prompt'] is True
        assert result_dict['created_at'] == datetime(2023, 1, 1, 12, 0, 0)
        assert result_dict['updated_at'] == datetime(2023, 1, 1, 13, 0, 0)
    
    def test_get_id_field(self):
        """Test getting the ID field name."""
        assert self.repository._get_id_field() == 'id'
    
    def test_dict_to_entity_conversion(self):
        """Test converting dictionary to Prompt entity."""
        entity_dict = {
            'id': 1,
            'tenant_id': 'tenant-123',
            'user_id': 'user-456',
            'name': 'test_prompt',
            'title': 'Test Prompt',
            'content': 'Test content',
            'category': 'Testing',
            'tags': 'test, unit',
            'is_enhancement_prompt': True,
            'created_at': datetime(2023, 1, 1, 12, 0, 0),
            'updated_at': datetime(2023, 1, 1, 13, 0, 0)
        }
        
        prompt = self.repository._dict_to_entity(entity_dict)
        
        assert isinstance(prompt, Prompt)
        assert prompt.id == 1
        assert prompt.tenant_id == 'tenant-123'
        assert prompt.name == 'test_prompt'
    
    def test_find_by_name_method(self):
        """Test finding prompt by name."""
        self.repository.set_tenant_context('tenant-123')
        mock_prompt = Prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='Test content'
        )
        
        with patch.object(self.repository, 'find_one_by_field', return_value=mock_prompt) as mock_find:
            result = self.repository.find_by_name('test_prompt')
            
            assert result == mock_prompt
            mock_find.assert_called_once_with('name', 'test_prompt')
    
    def test_find_by_category_method(self):
        """Test finding prompts by category."""
        self.repository.set_tenant_context('tenant-123')
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt1', title='Prompt 1', content='Content 1'),
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt2', title='Prompt 2', content='Content 2')
        ]
        
        with patch.object(self.repository, 'find_by_field', return_value=mock_prompts) as mock_find:
            results = self.repository.find_by_category('Testing')
            
            assert results == mock_prompts
            mock_find.assert_called_once_with('category', 'Testing')
    
    def test_find_by_user_method(self):
        """Test finding prompts by user."""
        self.repository.set_tenant_context('tenant-123')
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='prompt1', title='Prompt 1', content='Content 1')
        ]
        
        with patch.object(self.repository, 'find_by_field', return_value=mock_prompts) as mock_find:
            results = self.repository.find_by_user('user-456')
            
            assert results == mock_prompts
            mock_find.assert_called_once_with('user_id', 'user-456')
    
    def test_search_prompts_by_content(self):
        """Test searching prompts by content."""
        self.repository.set_tenant_context('tenant-123')
        self.mock_db_manager.config.db_type.value = "sqlite"
        
        mock_rows = [
            {
                'id': 1,
                'tenant_id': 'tenant-123',
                'user_id': 'user-456',
                'name': 'test_prompt',
                'title': 'Test Prompt',
                'content': 'This is test content with search term',
                'category': 'Testing',
                'tags': '',
                'is_enhancement_prompt': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        self.mock_db_manager.execute_query.return_value = mock_rows
        
        results = self.repository.search_prompts('search term')
        
        assert len(results) == 1
        assert results[0].content == 'This is test content with search term'
        
        # Verify search query was called
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "WHERE" in query
        assert "tenant_id = ?" in query
        assert "content LIKE ?" in query or "title LIKE ?" in query or "name LIKE ?" in query
        assert 'tenant-123' in params
        assert '%search term%' in params
    
    def test_search_prompts_postgres_syntax(self):
        """Test search prompts uses PostgreSQL syntax when needed."""
        self.repository.set_tenant_context('tenant-123')
        self.mock_db_manager.config.db_type.value = "postgres"
        self.mock_db_manager.execute_query.return_value = []
        
        self.repository.search_prompts('search term')
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        
        assert "%s" in query
        assert "?" not in query
    
    def test_search_prompts_no_context(self):
        """Test search prompts without tenant context."""
        with pytest.raises(DatabaseException) as exc_info:
            self.repository.search_prompts('search term')
        
        assert "Tenant context not set" in str(exc_info.value)
    
    def test_get_categories_method(self):
        """Test getting distinct categories."""
        self.repository.set_tenant_context('tenant-123')
        mock_rows = [
            {'category': 'Testing'},
            {'category': 'Development'},
            {'category': 'Documentation'}
        ]
        self.mock_db_manager.execute_query.return_value = mock_rows
        
        categories = self.repository.get_categories()
        
        assert categories == ['Testing', 'Development', 'Documentation']
        
        # Verify query
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "SELECT DISTINCT category" in query
        assert "WHERE tenant_id = ?" in query
        assert params == ('tenant-123',)
    
    def test_get_all_tags_method(self):
        """Test getting all unique tags."""
        self.repository.set_tenant_context('tenant-123')
        mock_rows = [
            {'tags': 'tag1, tag2, tag3'},
            {'tags': 'tag2, tag4'},
            {'tags': 'tag1, tag5'}
        ]
        self.mock_db_manager.execute_query.return_value = mock_rows
        
        tags = self.repository.get_all_tags()
        
        # Should return unique tags
        expected_tags = {'tag1', 'tag2', 'tag3', 'tag4', 'tag5'}
        assert set(tags) == expected_tags
    
    def test_get_all_tags_empty_tags(self):
        """Test getting all tags with some empty tag fields."""
        self.repository.set_tenant_context('tenant-123')
        mock_rows = [
            {'tags': 'tag1, tag2'},
            {'tags': ''},
            {'tags': 'tag3'}
        ]
        self.mock_db_manager.execute_query.return_value = mock_rows
        
        tags = self.repository.get_all_tags()
        
        assert set(tags) == {'tag1', 'tag2', 'tag3'}
    
    def test_find_enhancement_prompts(self):
        """Test finding enhancement prompts."""
        self.repository.set_tenant_context('tenant-123')
        mock_prompts = [
            Prompt(
                tenant_id='tenant-123', 
                user_id='user-456', 
                name='enhancement1', 
                title='Enhancement 1', 
                content='Content 1',
                is_enhancement_prompt=True
            )
        ]
        
        with patch.object(self.repository, 'find_by_field', return_value=mock_prompts) as mock_find:
            results = self.repository.find_enhancement_prompts()
            
            assert results == mock_prompts
            mock_find.assert_called_once_with('is_enhancement_prompt', True)
    
    def test_count_by_category(self):
        """Test counting prompts by category."""
        self.repository.set_tenant_context('tenant-123')
        
        with patch.object(self.repository, 'count', return_value=5) as mock_count:
            count = self.repository.count_by_category('Testing')
            
            assert count == 5
            mock_count.assert_called_once_with({'category': 'Testing'})
    
    def test_count_by_user(self):
        """Test counting prompts by user."""
        self.repository.set_tenant_context('tenant-123')
        
        with patch.object(self.repository, 'count', return_value=3) as mock_count:
            count = self.repository.count_by_user('user-456')
            
            assert count == 3
            mock_count.assert_called_once_with({'user_id': 'user-456'})
    
    def test_find_recent_prompts(self):
        """Test finding recent prompts."""
        self.repository.set_tenant_context('tenant-123')
        mock_prompts = [
            Prompt(tenant_id='tenant-123', user_id='user-456', name='recent1', title='Recent 1', content='Content 1'),
            Prompt(tenant_id='tenant-123', user_id='user-456', name='recent2', title='Recent 2', content='Content 2')
        ]
        
        with patch.object(self.repository, 'find_all', return_value=mock_prompts) as mock_find_all:
            results = self.repository.find_recent_prompts(5)
            
            assert results == mock_prompts
            mock_find_all.assert_called_once_with(
                limit=5,
                order_by='updated_at',
                order_desc=True
            )
    
    def test_find_recent_prompts_default_limit(self):
        """Test finding recent prompts with default limit."""
        self.repository.set_tenant_context('tenant-123')
        
        with patch.object(self.repository, 'find_all', return_value=[]) as mock_find_all:
            self.repository.find_recent_prompts()
            
            mock_find_all.assert_called_once_with(
                limit=10,
                order_by='updated_at',
                order_desc=True
            )
    
    def test_prompt_exists_by_name(self):
        """Test checking if prompt exists by name."""
        self.repository.set_tenant_context('tenant-123')
        
        # Mock finding a prompt
        mock_prompt = Prompt(
            tenant_id='tenant-123',
            user_id='user-456', 
            name='existing_prompt',
            title='Existing Prompt',
            content='Content'
        )
        
        with patch.object(self.repository, 'find_by_name', return_value=mock_prompt):
            assert self.repository.prompt_exists_by_name('existing_prompt') is True
        
        # Mock not finding a prompt
        with patch.object(self.repository, 'find_by_name', return_value=None):
            assert self.repository.prompt_exists_by_name('nonexistent_prompt') is False


class TestPromptRepositoryIntegration:
    """Integration tests for PromptRepository with real database operations."""
    
    def setup_method(self):
        """Set up test fixtures with real temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=self.temp_db.name)
        self.db_manager = DatabaseManager(self.config)
        self.repository = PromptRepository(self.db_manager)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except FileNotFoundError:
            pass
    
    def test_real_prompt_crud_operations(self):
        """Test real CRUD operations with SQLite."""
        self.repository.set_tenant_context('tenant-123')
        
        # Create a prompt
        prompt = Prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='test_prompt',
            title='Test Prompt',
            content='This is a test prompt for integration testing',
            category='Testing',
            tags='test, integration'
        )
        
        # Save the prompt
        saved_prompt = self.repository.save(prompt)
        
        assert saved_prompt.id is not None
        assert saved_prompt.name == 'test_prompt'
        assert saved_prompt.tenant_id == 'tenant-123'
        
        # Find the prompt by ID
        found_prompt = self.repository.find_by_id(saved_prompt.id)
        
        assert found_prompt is not None
        assert found_prompt.name == 'test_prompt'
        assert found_prompt.content == 'This is a test prompt for integration testing'
        
        # Update the prompt
        found_prompt.update_content('Updated test content')
        updated_prompt = self.repository.save(found_prompt)
        
        assert updated_prompt.content == 'Updated test content'
        assert updated_prompt.id == saved_prompt.id
        
        # Search for the prompt
        search_results = self.repository.search_prompts('Updated')
        
        assert len(search_results) == 1
        assert search_results[0].id == saved_prompt.id
        
        # Delete the prompt
        deleted = self.repository.delete(saved_prompt.id)
        
        assert deleted is True
        
        # Verify deletion
        deleted_prompt = self.repository.find_by_id(saved_prompt.id)
        assert deleted_prompt is None
    
    def test_real_tenant_isolation(self):
        """Test tenant isolation with real database."""
        # Create prompts for different tenants
        self.repository.set_tenant_context('tenant-123')
        
        prompt1 = Prompt(
            tenant_id='tenant-123',
            user_id='user-456',
            name='tenant1_prompt',
            title='Tenant 1 Prompt',
            content='Content for tenant 1'
        )
        saved_prompt1 = self.repository.save(prompt1)
        
        # Switch to different tenant
        self.repository.set_tenant_context('tenant-789')
        
        prompt2 = Prompt(
            tenant_id='tenant-789',
            user_id='user-101',
            name='tenant2_prompt',
            title='Tenant 2 Prompt',
            content='Content for tenant 2'
        )
        saved_prompt2 = self.repository.save(prompt2)
        
        # Verify tenant 1 can only see its prompt
        self.repository.set_tenant_context('tenant-123')
        tenant1_prompts = self.repository.find_all()
        
        assert len(tenant1_prompts) == 1
        assert tenant1_prompts[0].tenant_id == 'tenant-123'
        assert tenant1_prompts[0].name == 'tenant1_prompt'
        
        # Verify tenant 2 can only see its prompt
        self.repository.set_tenant_context('tenant-789')
        tenant2_prompts = self.repository.find_all()
        
        assert len(tenant2_prompts) == 1
        assert tenant2_prompts[0].tenant_id == 'tenant-789'
        assert tenant2_prompts[0].name == 'tenant2_prompt'
        
        # Verify tenant 1 cannot access tenant 2's prompt by ID
        self.repository.set_tenant_context('tenant-123')
        cross_tenant_access = self.repository.find_by_id(saved_prompt2.id)
        
        assert cross_tenant_access is None
    
    def test_real_search_functionality(self):
        """Test search functionality with real database."""
        self.repository.set_tenant_context('tenant-123')
        
        # Create test prompts
        prompts = [
            Prompt(
                tenant_id='tenant-123',
                user_id='user-456',
                name='python_prompt',
                title='Python Coding Helper',
                content='Help me write Python code for data analysis',
                category='Programming',
                tags='python, coding, data'
            ),
            Prompt(
                tenant_id='tenant-123',
                user_id='user-456',
                name='javascript_prompt',
                title='JavaScript Helper',
                content='Assist with JavaScript development and debugging',
                category='Programming',
                tags='javascript, web, debugging'
            ),
            Prompt(
                tenant_id='tenant-123',
                user_id='user-456',
                name='writing_prompt',
                title='Creative Writing Assistant',
                content='Help me write creative stories and essays',
                category='Writing',
                tags='creative, writing, stories'
            )
        ]
        
        # Save all prompts
        for prompt in prompts:
            self.repository.save(prompt)
        
        # Test content search
        python_results = self.repository.search_prompts('Python')
        assert len(python_results) == 1
        assert python_results[0].name == 'python_prompt'
        
        # Test title search
        helper_results = self.repository.search_prompts('Helper')
        assert len(helper_results) >= 2  # Should find Python and JavaScript helpers
        
        # Test category filtering
        programming_prompts = self.repository.find_by_category('Programming')
        assert len(programming_prompts) == 2
        
        writing_prompts = self.repository.find_by_category('Writing')
        assert len(writing_prompts) == 1
        
        # Test getting categories
        categories = self.repository.get_categories()
        assert 'Programming' in categories
        assert 'Writing' in categories
        
        # Test getting tags
        all_tags = self.repository.get_all_tags()
        assert 'python' in all_tags
        assert 'javascript' in all_tags
        assert 'creative' in all_tags


if __name__ == '__main__':
    pytest.main([__file__])