"""
Unit tests for the BaseRepository and repository patterns.

This module tests the repository base classes, CRUD operations,
and tenant-aware data access patterns.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.core.base.repository_base import BaseRepository, TenantAwareRepository
from src.core.base.database_manager import DatabaseManager
from src.core.config.settings import DatabaseConfig, DatabaseType
from src.core.exceptions.base import DatabaseException


# Test entity for repository testing
class TestEntity:
    """Simple test entity for repository testing."""
    
    def __init__(self, id=None, name=None, description=None, tenant_id=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.tenant_id = tenant_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()


class ConcreteRepository(BaseRepository[TestEntity]):
    """Concrete repository implementation for testing."""
    
    def _row_to_entity(self, row: Dict[str, Any]) -> TestEntity:
        """Convert database row to TestEntity."""
        return TestEntity(
            id=row.get('id'),
            name=row.get('name'),
            description=row.get('description'),
            tenant_id=row.get('tenant_id'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: TestEntity) -> Dict[str, Any]:
        """Convert TestEntity to dictionary."""
        return {
            'id': entity.id,
            'name': entity.name,
            'description': entity.description,
            'tenant_id': entity.tenant_id,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def _get_id_field(self) -> str:
        """Get the primary key field name."""
        return 'id'


class ConcreteTenantAwareRepository(TenantAwareRepository[TestEntity]):
    """Concrete tenant-aware repository implementation for testing."""
    
    def _row_to_entity(self, row: Dict[str, Any]) -> TestEntity:
        """Convert database row to TestEntity."""
        return TestEntity(
            id=row.get('id'),
            name=row.get('name'),
            description=row.get('description'),
            tenant_id=row.get('tenant_id'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: TestEntity) -> Dict[str, Any]:
        """Convert TestEntity to dictionary."""
        return {
            'id': entity.id,
            'name': entity.name,
            'description': entity.description,
            'tenant_id': entity.tenant_id,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def _get_id_field(self) -> str:
        """Get the primary key field name."""
        return 'id'
    
    def _dict_to_entity(self, entity_dict: Dict[str, Any]) -> TestEntity:
        """Convert dictionary to TestEntity."""
        return TestEntity(
            id=entity_dict.get('id'),
            name=entity_dict.get('name'),
            description=entity_dict.get('description'),
            tenant_id=entity_dict.get('tenant_id'),
            created_at=entity_dict.get('created_at'),
            updated_at=entity_dict.get('updated_at')
        )


class TestBaseRepository:
    """Test cases for BaseRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.config.db_type.value = "sqlite"
        self.repository = ConcreteRepository(self.mock_db_manager, 'test_entities')
    
    def test_repository_initialization(self):
        """Test repository initialization."""
        assert self.repository.db_manager == self.mock_db_manager
        assert self.repository.table_name == 'test_entities'
        assert hasattr(self.repository, 'logger')
    
    def test_find_by_id_success(self):
        """Test successful find by ID."""
        # Mock database response
        mock_row = {
            'id': 1,
            'name': 'Test Entity',
            'description': 'Test description',
            'tenant_id': 'tenant123',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        self.mock_db_manager.execute_query.return_value = mock_row
        
        entity = self.repository.find_by_id(1)
        
        assert entity is not None
        assert entity.id == 1
        assert entity.name == 'Test Entity'
        
        # Verify query was called correctly
        self.mock_db_manager.execute_query.assert_called_once()
        call_args = self.mock_db_manager.execute_query.call_args
        assert "SELECT * FROM test_entities WHERE id = ?" in call_args[0][0]
        assert call_args[0][1] == (1,)
        assert call_args[1]['fetch_one'] is True
    
    def test_find_by_id_not_found(self):
        """Test find by ID when entity not found."""
        self.mock_db_manager.execute_query.return_value = None
        
        entity = self.repository.find_by_id(999)
        
        assert entity is None
    
    def test_find_by_id_postgres_query(self):
        """Test find by ID uses PostgreSQL syntax when needed."""
        self.mock_db_manager.config.db_type.value = "postgres"
        self.mock_db_manager.execute_query.return_value = None
        
        self.repository.find_by_id(1)
        
        call_args = self.mock_db_manager.execute_query.call_args
        assert "SELECT * FROM test_entities WHERE id = %s" in call_args[0][0]
    
    def test_find_by_id_exception_handling(self):
        """Test find by ID exception handling."""
        self.mock_db_manager.execute_query.side_effect = Exception("Database error")
        
        with pytest.raises(DatabaseException) as exc_info:
            self.repository.find_by_id(1)
        
        assert "Failed to find test_entities by ID" in str(exc_info.value)
    
    def test_find_all_basic(self):
        """Test basic find all operation."""
        mock_rows = [
            {'id': 1, 'name': 'Entity 1', 'description': 'Desc 1', 'tenant_id': 'tenant123'},
            {'id': 2, 'name': 'Entity 2', 'description': 'Desc 2', 'tenant_id': 'tenant123'}
        ]
        self.mock_db_manager.execute_query.return_value = mock_rows
        
        entities = self.repository.find_all()
        
        assert len(entities) == 2
        assert entities[0].id == 1
        assert entities[1].id == 2
        
        # Verify query
        call_args = self.mock_db_manager.execute_query.call_args
        assert "SELECT * FROM test_entities" in call_args[0][0]
        assert call_args[1]['fetch_all'] is True
    
    def test_find_all_with_filters(self):
        """Test find all with filters."""
        self.mock_db_manager.execute_query.return_value = []
        filters = {'name': 'Test', 'tenant_id': 'tenant123'}
        
        self.repository.find_all(filters=filters)
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "WHERE" in query
        assert "name = ?" in query
        assert "tenant_id = ?" in query
        assert "AND" in query
        assert params == ('Test', 'tenant123')
    
    def test_find_all_with_pagination(self):
        """Test find all with pagination."""
        self.mock_db_manager.execute_query.return_value = []
        
        self.repository.find_all(limit=10, offset=20)
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        
        assert "LIMIT 10" in query
        assert "OFFSET 20" in query
    
    def test_find_all_with_ordering(self):
        """Test find all with ordering."""
        self.mock_db_manager.execute_query.return_value = []
        
        # Ascending order
        self.repository.find_all(order_by='name', order_desc=False)
        call_args = self.mock_db_manager.execute_query.call_args
        assert "ORDER BY name ASC" in call_args[0][0]
        
        # Descending order
        self.repository.find_all(order_by='created_at', order_desc=True)
        call_args = self.mock_db_manager.execute_query.call_args
        assert "ORDER BY created_at DESC" in call_args[0][0]
    
    def test_find_all_exception_handling(self):
        """Test find all exception handling."""
        self.mock_db_manager.execute_query.side_effect = Exception("Database error")
        
        with pytest.raises(DatabaseException) as exc_info:
            self.repository.find_all()
        
        assert "Failed to find test_entities records" in str(exc_info.value)
    
    def test_count_basic(self):
        """Test basic count operation."""
        self.mock_db_manager.execute_query.return_value = {'count': 5}
        
        count = self.repository.count()
        
        assert count == 5
        
        call_args = self.mock_db_manager.execute_query.call_args
        assert "SELECT COUNT(*) as count FROM test_entities" in call_args[0][0]
    
    def test_count_with_filters(self):
        """Test count with filters."""
        self.mock_db_manager.execute_query.return_value = {'count': 3}
        filters = {'tenant_id': 'tenant123'}
        
        count = self.repository.count(filters)
        
        assert count == 3
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        assert "WHERE tenant_id = ?" in query
    
    def test_count_no_result(self):
        """Test count when no result returned."""
        self.mock_db_manager.execute_query.return_value = None
        
        count = self.repository.count()
        
        assert count == 0
    
    def test_exists_true(self):
        """Test exists returns True when entity found."""
        mock_entity = TestEntity(id=1, name='Test')
        with patch.object(self.repository, 'find_by_id', return_value=mock_entity):
            assert self.repository.exists(1) is True
    
    def test_exists_false(self):
        """Test exists returns False when entity not found."""
        with patch.object(self.repository, 'find_by_id', return_value=None):
            assert self.repository.exists(999) is False
    
    def test_exists_exception_handling(self):
        """Test exists handles exceptions gracefully."""
        with patch.object(self.repository, 'find_by_id', side_effect=DatabaseException("Error")):
            assert self.repository.exists(1) is False
    
    def test_find_by_field(self):
        """Test find by field."""
        mock_entities = [TestEntity(id=1, name='Test')]
        with patch.object(self.repository, 'find_all', return_value=mock_entities) as mock_find_all:
            entities = self.repository.find_by_field('name', 'Test')
            
            assert entities == mock_entities
            mock_find_all.assert_called_once_with(filters={'name': 'Test'})
    
    def test_find_one_by_field(self):
        """Test find one by field."""
        mock_entities = [TestEntity(id=1, name='Test'), TestEntity(id=2, name='Test')]
        with patch.object(self.repository, 'find_by_field', return_value=mock_entities):
            entity = self.repository.find_one_by_field('name', 'Test')
            
            assert entity.id == 1
    
    def test_find_one_by_field_not_found(self):
        """Test find one by field when no results."""
        with patch.object(self.repository, 'find_by_field', return_value=[]):
            entity = self.repository.find_one_by_field('name', 'NotFound')
            
            assert entity is None
    
    def test_delete_success(self):
        """Test successful delete operation."""
        self.mock_db_manager.execute_query.return_value = 1  # 1 row affected
        
        result = self.repository.delete(1)
        
        assert result is True
        
        call_args = self.mock_db_manager.execute_query.call_args
        assert "DELETE FROM test_entities WHERE id = ?" in call_args[0][0]
        assert call_args[0][1] == (1,)
    
    def test_delete_not_found(self):
        """Test delete when entity not found."""
        self.mock_db_manager.execute_query.return_value = 0  # 0 rows affected
        
        result = self.repository.delete(999)
        
        assert result is False
    
    def test_delete_exception_handling(self):
        """Test delete exception handling."""
        self.mock_db_manager.execute_query.side_effect = Exception("Database error")
        
        with pytest.raises(DatabaseException) as exc_info:
            self.repository.delete(1)
        
        assert "Failed to delete test_entities" in str(exc_info.value)


class TestTenantAwareRepository:
    """Test cases for TenantAwareRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.config.db_type.value = "sqlite"
        self.repository = ConcreteTenantAwareRepository(self.mock_db_manager, 'test_entities')
    
    def test_tenant_aware_repository_initialization(self):
        """Test tenant-aware repository initialization."""
        assert self.repository.current_tenant_id is None
        assert hasattr(self.repository, 'logger')
    
    def test_set_tenant_context(self):
        """Test setting tenant context."""
        self.repository.set_tenant_context('tenant123')
        
        assert self.repository.current_tenant_id == 'tenant123'
    
    def test_ensure_tenant_context_success(self):
        """Test successful tenant context check."""
        self.repository.set_tenant_context('tenant123')
        
        # Should not raise exception
        self.repository._ensure_tenant_context()
    
    def test_ensure_tenant_context_failure(self):
        """Test tenant context check failure."""
        with pytest.raises(DatabaseException) as exc_info:
            self.repository._ensure_tenant_context()
        
        assert "Tenant context not set" in str(exc_info.value)
    
    def test_add_tenant_filter(self):
        """Test adding tenant filter to existing filters."""
        self.repository.set_tenant_context('tenant123')
        
        existing_filters = {'name': 'test'}
        result_filters = self.repository._add_tenant_filter(existing_filters)
        
        assert result_filters['name'] == 'test'
        assert result_filters['tenant_id'] == 'tenant123'
        
        # Test with None filters
        result_filters = self.repository._add_tenant_filter(None)
        assert result_filters == {'tenant_id': 'tenant123'}
    
    def test_tenant_aware_find_by_id(self):
        """Test tenant-aware find by ID."""
        self.repository.set_tenant_context('tenant123')
        mock_row = {
            'id': 1,
            'name': 'Test Entity',
            'tenant_id': 'tenant123'
        }
        self.mock_db_manager.execute_query.return_value = mock_row
        
        entity = self.repository.find_by_id(1)
        
        assert entity is not None
        assert entity.id == 1
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "WHERE id = ? AND tenant_id = ?" in query
        assert params == (1, 'tenant123')
    
    def test_tenant_aware_find_by_id_no_context(self):
        """Test tenant-aware find by ID without context."""
        with pytest.raises(DatabaseException):
            self.repository.find_by_id(1)
    
    def test_tenant_aware_find_all(self):
        """Test tenant-aware find all."""
        self.repository.set_tenant_context('tenant123')
        self.mock_db_manager.execute_query.return_value = []
        
        with patch.object(BaseRepository, 'find_all') as mock_base_find_all:
            self.repository.find_all(filters={'name': 'test'})
            
            # Verify base find_all was called with tenant filter added
            call_args = mock_base_find_all.call_args
            filters = call_args[1]['filters']
            assert filters['tenant_id'] == 'tenant123'
            assert filters['name'] == 'test'
    
    def test_tenant_aware_count(self):
        """Test tenant-aware count."""
        self.repository.set_tenant_context('tenant123')
        self.mock_db_manager.execute_query.return_value = {'count': 5}
        
        with patch.object(BaseRepository, 'count', return_value=5) as mock_base_count:
            count = self.repository.count(filters={'name': 'test'})
            
            assert count == 5
            
            # Verify base count was called with tenant filter added
            call_args = mock_base_count.call_args
            filters = call_args[0][0]
            assert filters['tenant_id'] == 'tenant123'
            assert filters['name'] == 'test'
    
    def test_tenant_aware_delete(self):
        """Test tenant-aware delete."""
        self.repository.set_tenant_context('tenant123')
        self.mock_db_manager.execute_query.return_value = 1
        
        result = self.repository.delete(1)
        
        assert result is True
        
        call_args = self.mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "DELETE FROM test_entities WHERE id = ? AND tenant_id = ?" in query
        assert params == (1, 'tenant123')
    
    def test_tenant_aware_save_new_entity(self):
        """Test tenant-aware save for new entity."""
        self.repository.set_tenant_context('tenant123')
        
        # Mock _insert_entity behavior
        entity = TestEntity(name='New Entity', description='Test')
        inserted_entity = TestEntity(id=1, name='New Entity', description='Test', tenant_id='tenant123')
        
        with patch.object(self.repository, '_insert_entity', return_value=inserted_entity) as mock_insert:
            with patch.object(self.repository, 'find_by_id', return_value=None):  # Entity doesn't exist
                result = self.repository.save(entity)
                
                assert result.id == 1
                assert result.tenant_id == 'tenant123'
                mock_insert.assert_called_once()
    
    def test_tenant_aware_save_existing_entity(self):
        """Test tenant-aware save for existing entity."""
        self.repository.set_tenant_context('tenant123')
        
        entity = TestEntity(id=1, name='Updated Entity', tenant_id='tenant123')
        
        with patch.object(self.repository, 'find_by_id', return_value=entity):  # Entity exists
            with patch.object(BaseRepository, 'save', return_value=entity) as mock_base_save:
                result = self.repository.save(entity)
                
                assert result == entity
                mock_base_save.assert_called_once()
    
    def test_tenant_aware_save_wrong_tenant(self):
        """Test tenant-aware save with entity from wrong tenant."""
        self.repository.set_tenant_context('tenant123')
        
        entity = TestEntity(id=1, name='Entity', tenant_id='tenant456')
        
        with patch.object(self.repository, 'find_by_id', return_value=None):  # Entity not found in current tenant
            with pytest.raises(DatabaseException) as exc_info:
                self.repository.save(entity)
            
            assert "not found in current tenant" in str(exc_info.value)
    
    def test_tenant_aware_insert_entity_sqlite(self):
        """Test tenant-aware insert entity for SQLite."""
        self.repository.set_tenant_context('tenant123')
        self.mock_db_manager.config.db_type.value = "sqlite"
        
        # Mock SQLite connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # last_insert_rowid
        mock_cursor.description = [('id',), ('name',), ('tenant_id',)]
        mock_cursor.fetchone.side_effect = [[1], (1, 'Test Entity', 'tenant123')]  # First call for rowid, second for data
        
        entity_dict = {
            'name': 'Test Entity',
            'description': 'Test description',
            'tenant_id': 'tenant123',
            'created_at': None,
            'updated_at': None
        }
        
        with patch.object(self.mock_db_manager, 'get_connection_context', return_value=mock_conn):
            result = self.repository._insert_entity(entity_dict)
            
            assert result.id == 1
            assert result.name == 'Test Entity'
            assert result.tenant_id == 'tenant123'
            
            # Verify execute was called
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    def test_insert_entity_sets_timestamps(self):
        """Test that insert entity sets timestamps."""
        self.repository.set_tenant_context('tenant123')
        
        entity_dict = {
            'name': 'Test',
            'created_at': None,
            'updated_at': None
        }
        
        with patch.object(self.mock_db_manager, 'get_connection_context') as mock_context:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [[1], (1, 'Test', 'tenant123', datetime.utcnow(), datetime.utcnow())]
            mock_cursor.description = [('id',), ('name',), ('tenant_id',), ('created_at',), ('updated_at',)]
            mock_context.return_value = mock_conn
            
            self.repository._insert_entity(entity_dict)
            
            # Verify timestamps were set in the entity_dict
            assert entity_dict['created_at'] is not None
            assert entity_dict['updated_at'] is not None
            assert isinstance(entity_dict['created_at'], datetime)
            assert isinstance(entity_dict['updated_at'], datetime)


if __name__ == '__main__':
    pytest.main([__file__])