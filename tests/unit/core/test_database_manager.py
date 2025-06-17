"""
Unit tests for the DatabaseManager core functionality.

This module tests database connection management, query execution,
and transaction handling for both SQLite and PostgreSQL backends.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from src.core.base.database_manager import BaseDatabaseManager, DatabaseManager
from src.core.config.settings import DatabaseConfig, DatabaseType
from src.core.exceptions.base import DatabaseException, ConfigurationException


class TestDatabaseManager(BaseDatabaseManager):
    """Concrete implementation for testing abstract BaseDatabaseManager."""
    
    def _setup_database(self) -> None:
        """Test implementation of abstract method."""
        pass


class TestBaseDatabaseManager:
    """Test cases for BaseDatabaseManager."""
    
    def test_database_manager_initialization_sqlite(self):
        """Test database manager initialization with SQLite config."""
        config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path="test.db")
        manager = TestDatabaseManager(config)
        
        assert manager.config == config
        assert manager.config.db_type == DatabaseType.SQLITE
        assert manager.config.db_path == "test.db"
    
    def test_database_manager_initialization_postgres(self):
        """Test database manager initialization with PostgreSQL config."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRES, 
            dsn="postgresql://user:pass@localhost:5432/test"
        )
        manager = TestDatabaseManager(config)
        
        assert manager.config == config
        assert manager.config.db_type == DatabaseType.POSTGRES
        assert manager.config.dsn == "postgresql://user:pass@localhost:5432/test"
    
    def test_database_manager_initialization_with_none_config(self):
        """Test database manager initialization with None config loads from environment."""
        with patch('src.core.base.database_manager.DatabaseConfig.from_env') as mock_from_env:
            mock_config = DatabaseConfig()
            mock_from_env.return_value = mock_config
            
            manager = TestDatabaseManager(None)
            
            assert manager.config == mock_config
            mock_from_env.assert_called_once()
    
    def test_validate_config_sqlite_success(self):
        """Test successful SQLite config validation."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path="data/test.db")
            manager = TestDatabaseManager(config)
            
            # Should not raise exception
            manager._validate_config()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_validate_config_postgres_success(self):
        """Test successful PostgreSQL config validation."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRES,
            dsn="postgresql://user:pass@localhost:5432/test"
        )
        manager = TestDatabaseManager(config)
        
        # Should not raise exception
        manager._validate_config()
    
    def test_validate_config_postgres_missing_dsn(self):
        """Test PostgreSQL config validation fails without DSN."""
        config = DatabaseConfig(db_type=DatabaseType.POSTGRES)
        
        with pytest.raises(ConfigurationException) as exc_info:
            TestDatabaseManager(config)
        
        assert "POSTGRES_DSN is required" in str(exc_info.value)
    
    @patch('src.core.base.database_manager.POSTGRES_AVAILABLE', False)
    def test_validate_config_postgres_not_available(self):
        """Test PostgreSQL config validation fails when psycopg2 not available."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRES,
            dsn="postgresql://user:pass@localhost:5432/test"
        )
        
        with pytest.raises(ConfigurationException) as exc_info:
            TestDatabaseManager(config)
        
        assert "PostgreSQL dependencies not available" in str(exc_info.value)


class TestDatabaseManagerImplementation:
    """Test cases for the concrete DatabaseManager implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except FileNotFoundError:
            pass
    
    def test_database_manager_concrete_initialization(self):
        """Test concrete DatabaseManager initialization."""
        manager = DatabaseManager(self.config)
        
        assert manager.config == self.config
        assert hasattr(manager, 'logger')
    
    @patch('sqlite3.connect')
    def test_get_connection_context_sqlite(self, mock_connect):
        """Test getting connection context for SQLite."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        manager = DatabaseManager(self.config)
        
        with manager.get_connection_context() as conn:
            assert conn == mock_connection
        
        mock_connect.assert_called_once_with(self.temp_db.name)
    
    @patch('src.core.base.database_manager.POSTGRES_AVAILABLE', True)
    @patch('src.core.base.database_manager.psycopg2.connect')
    def test_get_connection_context_postgres(self, mock_connect):
        """Test getting connection context for PostgreSQL."""
        postgres_config = DatabaseConfig(
            db_type=DatabaseType.POSTGRES,
            dsn="postgresql://user:pass@localhost:5432/test"
        )
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        manager = DatabaseManager(postgres_config)
        
        with manager.get_connection_context() as conn:
            assert conn == mock_connection
        
        mock_connect.assert_called_once_with("postgresql://user:pass@localhost:5432/test")
    
    @patch('sqlite3.connect')
    def test_execute_query_fetch_one(self, mock_connect):
        """Test executing query with fetch_one=True."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'test')
        mock_cursor.description = [('id',), ('name',)]
        
        manager = DatabaseManager(self.config)
        
        result = manager.execute_query("SELECT * FROM test WHERE id = ?", (1,), fetch_one=True)
        
        assert result == {'id': 1, 'name': 'test'}
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test WHERE id = ?", (1,))
        mock_cursor.fetchone.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_execute_query_fetch_all(self, mock_connect):
        """Test executing query with fetch_all=True."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 'test1'), (2, 'test2')]
        mock_cursor.description = [('id',), ('name',)]
        
        manager = DatabaseManager(self.config)
        
        result = manager.execute_query("SELECT * FROM test", (), fetch_all=True)
        
        assert len(result) == 2
        assert result[0] == {'id': 1, 'name': 'test1'}
        assert result[1] == {'id': 2, 'name': 'test2'}
        mock_cursor.fetchall.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_execute_query_no_fetch(self, mock_connect):
        """Test executing query without fetching results."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        manager = DatabaseManager(self.config)
        
        result = manager.execute_query("INSERT INTO test (name) VALUES (?)", ('test',))
        
        assert result == 1
        mock_cursor.execute.assert_called_once_with("INSERT INTO test (name) VALUES (?)", ('test',))
        mock_connection.commit.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_execute_query_exception_handling(self, mock_connect):
        """Test query execution exception handling."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        manager = DatabaseManager(self.config)
        
        with pytest.raises(DatabaseException) as exc_info:
            manager.execute_query("SELECT * FROM nonexistent", ())
        
        assert "Query execution failed" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)
        mock_connection.rollback.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_execute_query_fetch_one_no_result(self, mock_connect):
        """Test executing query with fetch_one when no result found."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        manager = DatabaseManager(self.config)
        
        result = manager.execute_query("SELECT * FROM test WHERE id = ?", (999,), fetch_one=True)
        
        assert result is None
    
    @patch('sqlite3.connect')
    def test_execute_query_fetch_all_no_results(self, mock_connect):
        """Test executing query with fetch_all when no results found."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        manager = DatabaseManager(self.config)
        
        result = manager.execute_query("SELECT * FROM test WHERE id = ?", (999,), fetch_all=True)
        
        assert result == []
    
    def test_setup_database_implementation(self):
        """Test that concrete DatabaseManager has setup_database implementation."""
        manager = DatabaseManager(self.config)
        
        # Should not raise NotImplementedError
        manager._setup_database()
    
    @patch('sqlite3.connect')
    def test_row_to_dict_conversion(self, mock_connect):
        """Test row to dictionary conversion helper method."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        manager = DatabaseManager(self.config)
        
        # Test with description and row data
        description = [('id',), ('name',), ('email',)]
        row = (1, 'John Doe', 'john@example.com')
        
        result = manager._row_to_dict(row, description)
        
        expected = {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}
        assert result == expected
    
    @patch('sqlite3.connect')
    def test_row_to_dict_empty_row(self, mock_connect):
        """Test row to dictionary conversion with empty row."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        manager = DatabaseManager(self.config)
        
        description = [('id',), ('name',)]
        row = None
        
        result = manager._row_to_dict(row, description)
        
        assert result is None


class TestDatabaseManagerIntegration:
    """Integration tests for DatabaseManager with real database operations."""
    
    def setup_method(self):
        """Set up test fixtures with real temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=self.temp_db.name)
        self.manager = DatabaseManager(self.config)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except FileNotFoundError:
            pass
    
    def test_real_database_operations(self):
        """Test real database operations with SQLite."""
        # Create table
        self.manager.execute_query("""
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """, ())
        
        # Insert data
        affected = self.manager.execute_query(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ('John Doe', 'john@example.com')
        )
        assert affected == 1
        
        # Fetch single record
        user = self.manager.execute_query(
            "SELECT * FROM test_users WHERE email = ?",
            ('john@example.com',),
            fetch_one=True
        )
        assert user is not None
        assert user['name'] == 'John Doe'
        assert user['email'] == 'john@example.com'
        
        # Fetch all records
        users = self.manager.execute_query(
            "SELECT * FROM test_users",
            (),
            fetch_all=True
        )
        assert len(users) == 1
        assert users[0]['name'] == 'John Doe'
    
    def test_transaction_rollback_on_error(self):
        """Test that transactions are rolled back on errors."""
        # Create table
        self.manager.execute_query("""
            CREATE TABLE test_transaction (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE
            )
        """, ())
        
        # Insert first record
        self.manager.execute_query(
            "INSERT INTO test_transaction (email) VALUES (?)",
            ('test@example.com',)
        )
        
        # Try to insert duplicate (should fail due to UNIQUE constraint)
        with pytest.raises(DatabaseException):
            self.manager.execute_query(
                "INSERT INTO test_transaction (email) VALUES (?)",
                ('test@example.com',)
            )
        
        # Verify only one record exists
        count = self.manager.execute_query(
            "SELECT COUNT(*) as count FROM test_transaction",
            (),
            fetch_one=True
        )
        assert count['count'] == 1


if __name__ == '__main__':
    pytest.main([__file__])