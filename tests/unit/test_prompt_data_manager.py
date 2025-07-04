"""
Comprehensive unit tests for PromptDataManager class
Testing database operations, multi-tenant isolation, and configuration management
"""

import os
import sqlite3
import tempfile
import uuid
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from prompt_data_manager import PromptDataManager


class TestPromptDataManager:
    """Test suite for PromptDataManager functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def user_id(self):
        """Generate user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def data_manager_sqlite(self, temp_db, tenant_id, user_id):
        """Create PromptDataManager instance with SQLite"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            return PromptDataManager(db_path=temp_db, tenant_id=tenant_id, user_id=user_id)

    @pytest.fixture
    def data_manager_no_tenant(self, temp_db):
        """Create PromptDataManager instance without tenant/user context"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            return PromptDataManager(db_path=temp_db)

    @pytest.fixture
    def postgres_data_manager(self, tenant_id, user_id):
        """Create PromptDataManager instance configured for PostgreSQL"""
        with patch.dict(
            os.environ,
            {
                "DB_TYPE": "postgres",
                "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test",
            },
            clear=True,
        ):
            with patch("prompt_data_manager.POSTGRES_AVAILABLE", True):
                with patch("prompt_data_manager.psycopg2") as mock_psycopg2:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_psycopg2.connect.return_value = mock_conn
                    return PromptDataManager(tenant_id=tenant_id, user_id=user_id)

    @pytest.fixture
    def sample_prompt_data(self):
        """Sample prompt data for testing"""
        return {
            "name": "test-prompt",
            "title": "Test Prompt",
            "content": "This is a test prompt content",
            "category": "Testing",
            "tags": "test, unit, automation",
            "is_enhancement_prompt": False,
        }

    @pytest.fixture
    def sample_enhancement_prompt_data(self):
        """Sample enhancement prompt data for testing"""
        return {
            "name": "enhancement-prompt",
            "title": "Enhancement Prompt",
            "content": "This is an enhancement prompt",
            "category": "Enhancement",
            "tags": "enhance, improve",
            "is_enhancement_prompt": True,
        }

    def test_initialization_sqlite(self, temp_db, tenant_id, user_id):
        """Test PromptDataManager initialization with SQLite"""
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager = PromptDataManager(db_path=temp_db, tenant_id=tenant_id, user_id=user_id)
            assert manager.db_type == "sqlite"
            assert manager.db_path == temp_db
            assert manager.tenant_id == tenant_id
            assert manager.user_id == user_id

    def test_initialization_postgres_success(self, postgres_data_manager, tenant_id, user_id):
        """Test PromptDataManager initialization with PostgreSQL"""
        assert postgres_data_manager.db_type == "postgres"
        assert postgres_data_manager.dsn == "postgresql://test:test@localhost:5432/test"
        assert postgres_data_manager.tenant_id == tenant_id
        assert postgres_data_manager.user_id == user_id
        assert postgres_data_manager.db_path is None

    def test_initialization_postgres_missing_psycopg2(self):
        """Test PromptDataManager initialization fails when psycopg2 not available"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "postgres", "POSTGRES_DSN": "postgresql://test:test@localhost:5432/test"},
            clear=True,
        ):
            with patch("prompt_data_manager.POSTGRES_AVAILABLE", False):
                with pytest.raises(ImportError, match="psycopg2 is required"):
                    PromptDataManager()

    def test_initialization_postgres_missing_dsn(self):
        """Test PromptDataManager initialization fails when POSTGRES_DSN not set"""
        with patch.dict(os.environ, {"DB_TYPE": "postgres"}, clear=True):
            with patch("prompt_data_manager.POSTGRES_AVAILABLE", True):
                with pytest.raises(ValueError, match="POSTGRES_DSN environment variable"):
                    PromptDataManager()

    def test_get_conn_sqlite(self, data_manager_sqlite):
        """Test database connection for SQLite"""
        conn = data_manager_sqlite.get_conn()
        assert conn is not None
        assert hasattr(conn, "cursor")
        conn.close()

    def test_get_conn_sqlite_no_path(self, tenant_id, user_id):
        """Test database connection fails when SQLite path not set"""
        with patch.dict(os.environ, {"DB_TYPE": "sqlite"}, clear=True):
            manager = PromptDataManager(tenant_id=tenant_id, user_id=user_id)
            manager.db_path = None
            with pytest.raises(ValueError, match="Database path not set"):
                manager.get_conn()

    def test_database_initialization_sqlite(self, data_manager_sqlite):
        """Test database tables are created correctly for SQLite"""
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()

        # Check prompts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'")
        assert cursor.fetchone() is not None

        # Check config table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        assert cursor.fetchone() is not None

        # Check prompts table columns
        cursor.execute("PRAGMA table_info(prompts)")
        columns = [column[1] for column in cursor.fetchall()]
        expected_columns = [
            "id",
            "tenant_id",
            "user_id",
            "name",
            "title",
            "content",
            "category",
            "tags",
            "is_enhancement_prompt",
            "created_at",
            "updated_at",
        ]
        for col in expected_columns:
            assert col in columns

        # Check config table columns
        cursor.execute("PRAGMA table_info(config)")
        config_columns = [column[1] for column in cursor.fetchall()]
        expected_config_columns = ["id", "tenant_id", "user_id", "key", "value"]
        for col in expected_config_columns:
            assert col in config_columns

        conn.close()

    def test_add_prompt_success(self, data_manager_sqlite, sample_prompt_data):
        """Test successful prompt addition"""
        result = data_manager_sqlite.add_prompt(**sample_prompt_data)

        assert "successfully" in result
        assert "added" in result

        # Verify prompt exists in database
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prompts WHERE name = ? AND tenant_id = ?",
            (sample_prompt_data["name"], data_manager_sqlite.tenant_id),
        )
        prompt = cursor.fetchone()
        assert prompt is not None
        assert prompt[3] == sample_prompt_data["name"]  # name
        assert prompt[4] == sample_prompt_data["title"]  # title
        assert prompt[5] == sample_prompt_data["content"]  # content
        assert prompt[6] == sample_prompt_data["category"]  # category
        assert prompt[7] == sample_prompt_data["tags"]  # tags
        conn.close()

    def test_add_prompt_missing_tenant_id(self, data_manager_no_tenant, sample_prompt_data):
        """Test prompt addition fails without tenant ID"""
        result = data_manager_no_tenant.add_prompt(**sample_prompt_data)

        assert "error" in result.lower()
        assert "tenant_id" in result.lower()

    def test_add_prompt_missing_required_fields(self, data_manager_sqlite):
        """Test prompt addition fails with missing required fields"""
        # Missing name
        result = data_manager_sqlite.add_prompt(
            name="", title="Test", content="Content", category="Test", tags=""
        )
        assert "error" in result.lower()

        # Missing title
        result = data_manager_sqlite.add_prompt(
            name="test", title="", content="Content", category="Test", tags=""
        )
        assert "error" in result.lower()

        # Missing content
        result = data_manager_sqlite.add_prompt(
            name="test", title="Test", content="", category="Test", tags=""
        )
        assert "error" in result.lower()

    def test_add_prompt_duplicate_name_same_tenant(self, data_manager_sqlite, sample_prompt_data):
        """Test prompt addition fails with duplicate name in same tenant"""
        # Add first prompt
        result1 = data_manager_sqlite.add_prompt(**sample_prompt_data)
        assert "successfully" in result1

        # Try to add duplicate
        duplicate_data = sample_prompt_data.copy()
        duplicate_data["title"] = "Different Title"
        result2 = data_manager_sqlite.add_prompt(**duplicate_data)

        assert "error" in result2.lower()
        assert "already exists" in result2.lower() or "duplicate" in result2.lower()

    def test_add_prompt_same_name_different_tenant(self, temp_db, sample_prompt_data):
        """Test prompt addition allows same name in different tenants"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            # Create managers for different tenants
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=str(uuid.uuid4()))
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=str(uuid.uuid4()))

            # Add same prompt name to different tenants
            result1 = manager1.add_prompt(**sample_prompt_data)
            result2 = manager2.add_prompt(**sample_prompt_data)

            assert "successfully" in result1
            assert "successfully" in result2

    def test_add_enhancement_prompt(self, data_manager_sqlite, sample_enhancement_prompt_data):
        """Test adding enhancement prompt"""
        result = data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        assert "successfully" in result

        # Verify enhancement flag is set
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_enhancement_prompt FROM prompts WHERE name = ? AND tenant_id = ?",
            (sample_enhancement_prompt_data["name"], data_manager_sqlite.tenant_id),
        )
        is_enhancement = cursor.fetchone()[0]
        assert is_enhancement == 1  # SQLite stores boolean as integer
        conn.close()

    def test_update_prompt_success(self, data_manager_sqlite, sample_prompt_data):
        """Test successful prompt update"""
        # Add original prompt
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Update prompt
        updated_data = {
            "original_name": sample_prompt_data["name"],
            "new_name": "updated-prompt",
            "title": "Updated Title",
            "content": "Updated content",
            "category": "Updated Category",
            "tags": "updated, tags",
            "is_enhancement_prompt": True,
        }

        result = data_manager_sqlite.update_prompt(**updated_data)
        assert "successfully" in result

        # Verify update
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, title, content, category, tags, is_enhancement_prompt FROM prompts WHERE tenant_id = ?",
            (data_manager_sqlite.tenant_id,),
        )
        prompt = cursor.fetchone()
        assert prompt[0] == updated_data["new_name"]
        assert prompt[1] == updated_data["title"]
        assert prompt[2] == updated_data["content"]
        assert prompt[3] == updated_data["category"]
        assert prompt[4] == updated_data["tags"]
        assert prompt[5] == 1  # is_enhancement_prompt
        conn.close()

    def test_update_prompt_nonexistent(self, data_manager_sqlite):
        """Test updating non-existent prompt"""
        result = data_manager_sqlite.update_prompt(
            original_name="nonexistent",
            new_name="new-name",
            title="Title",
            content="Content",
            category="Category",
            tags="tags",
        )

        assert "error" in result.lower()

    def test_update_prompt_name_conflict(self, data_manager_sqlite, sample_prompt_data):
        """Test updating prompt with conflicting name"""
        # Add two prompts
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        
        second_prompt = sample_prompt_data.copy()
        second_prompt["name"] = "second-prompt"
        second_prompt["title"] = "Second Prompt"
        data_manager_sqlite.add_prompt(**second_prompt)

        # Try to update second prompt to use first prompt's name
        result = data_manager_sqlite.update_prompt(
            original_name="second-prompt",
            new_name=sample_prompt_data["name"],  # Conflict
            title="Updated Title",
            content="Updated content",
            category="Category",
            tags="tags",
        )

        assert "error" in result.lower()
        assert "already exists" in result.lower() or "conflict" in result.lower()

    def test_delete_prompt_success(self, data_manager_sqlite, sample_prompt_data):
        """Test successful prompt deletion"""
        # Add prompt first
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Delete prompt
        result = data_manager_sqlite.delete_prompt(sample_prompt_data["name"])
        assert "successfully" in result

        # Verify deletion
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prompts WHERE name = ? AND tenant_id = ?",
            (sample_prompt_data["name"], data_manager_sqlite.tenant_id),
        )
        prompt = cursor.fetchone()
        assert prompt is None
        conn.close()

    def test_delete_prompt_nonexistent(self, data_manager_sqlite):
        """Test deleting non-existent prompt"""
        result = data_manager_sqlite.delete_prompt("nonexistent-prompt")
        assert "error" in result.lower()

    def test_delete_prompt_tenant_isolation(self, temp_db, sample_prompt_data):
        """Test prompt deletion respects tenant isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=str(uuid.uuid4()))
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=str(uuid.uuid4()))

            # Add prompt to tenant1
            manager1.add_prompt(**sample_prompt_data)

            # Try to delete from tenant2 (should fail)
            result = manager2.delete_prompt(sample_prompt_data["name"])
            assert "error" in result.lower()

            # Verify prompt still exists for tenant1
            prompts = manager1.get_all_prompts()
            assert len(prompts) == 1

    def test_get_all_prompts(self, data_manager_sqlite, sample_prompt_data, sample_enhancement_prompt_data):
        """Test retrieving all prompts"""
        # Add multiple prompts
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        # Get all prompts
        prompts = data_manager_sqlite.get_all_prompts()

        assert len(prompts) == 2
        prompt_names = [p["name"] for p in prompts]
        assert sample_prompt_data["name"] in prompt_names
        assert sample_enhancement_prompt_data["name"] in prompt_names

        # Check prompt structure
        prompt = prompts[0]
        expected_fields = ["id", "name", "title", "content", "category", "tags", "is_enhancement_prompt", "created_at", "updated_at"]
        for field in expected_fields:
            assert field in prompt

    def test_get_all_prompts_exclude_enhancement(self, data_manager_sqlite, sample_prompt_data, sample_enhancement_prompt_data):
        """Test retrieving all prompts excluding enhancement prompts"""
        # Add multiple prompts
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        # Get all prompts excluding enhancements
        prompts = data_manager_sqlite.get_all_prompts(include_enhancement_prompts=False)

        assert len(prompts) == 1
        assert prompts[0]["name"] == sample_prompt_data["name"]
        assert not prompts[0]["is_enhancement_prompt"]

    def test_get_all_prompts_tenant_isolation(self, temp_db, sample_prompt_data):
        """Test get_all_prompts respects tenant isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=str(uuid.uuid4()))
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=str(uuid.uuid4()))

            # Add prompt to tenant1
            manager1.add_prompt(**sample_prompt_data)

            # Each tenant should only see their own prompts
            prompts1 = manager1.get_all_prompts()
            prompts2 = manager2.get_all_prompts()

            assert len(prompts1) == 1
            assert len(prompts2) == 0

    def test_get_enhancement_prompts(self, data_manager_sqlite, sample_prompt_data, sample_enhancement_prompt_data):
        """Test retrieving only enhancement prompts"""
        # Add multiple prompts
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        # Get enhancement prompts
        enhancement_prompts = data_manager_sqlite.get_enhancement_prompts()

        assert len(enhancement_prompts) == 1
        assert enhancement_prompts[0]["name"] == sample_enhancement_prompt_data["name"]
        assert enhancement_prompts[0]["is_enhancement_prompt"] is True

    def test_get_prompt_by_name_success(self, data_manager_sqlite, sample_prompt_data):
        """Test retrieving prompt by name"""
        # Add prompt
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Get prompt by name
        prompt = data_manager_sqlite.get_prompt_by_name(sample_prompt_data["name"])

        assert prompt is not None
        assert prompt["name"] == sample_prompt_data["name"]
        assert prompt["title"] == sample_prompt_data["title"]
        assert prompt["content"] == sample_prompt_data["content"]

    def test_get_prompt_by_name_nonexistent(self, data_manager_sqlite):
        """Test retrieving non-existent prompt by name"""
        prompt = data_manager_sqlite.get_prompt_by_name("nonexistent")
        assert prompt is None

    def test_get_prompt_by_name_tenant_isolation(self, temp_db, sample_prompt_data):
        """Test get_prompt_by_name respects tenant isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=str(uuid.uuid4()))
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=str(uuid.uuid4()))

            # Add prompt to tenant1
            manager1.add_prompt(**sample_prompt_data)

            # tenant1 should find it, tenant2 should not
            prompt1 = manager1.get_prompt_by_name(sample_prompt_data["name"])
            prompt2 = manager2.get_prompt_by_name(sample_prompt_data["name"])

            assert prompt1 is not None
            assert prompt2 is None

    def test_search_prompts_content_match(self, data_manager_sqlite, sample_prompt_data):
        """Test searching prompts by content"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Search by content keyword
        results = data_manager_sqlite.search_prompts("test prompt")
        assert len(results) == 1
        assert results[0]["name"] == sample_prompt_data["name"]

    def test_search_prompts_title_match(self, data_manager_sqlite, sample_prompt_data):
        """Test searching prompts by title"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Search by title keyword
        results = data_manager_sqlite.search_prompts("Test Prompt")
        assert len(results) == 1

    def test_search_prompts_tags_match(self, data_manager_sqlite, sample_prompt_data):
        """Test searching prompts by tags"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Search by tag keyword
        results = data_manager_sqlite.search_prompts("automation")
        assert len(results) == 1

    def test_search_prompts_case_insensitive(self, data_manager_sqlite, sample_prompt_data):
        """Test case-insensitive search"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Search with different case
        results = data_manager_sqlite.search_prompts("TEST PROMPT")
        assert len(results) == 1

    def test_search_prompts_empty_term(self, data_manager_sqlite, sample_prompt_data):
        """Test search with empty term returns all prompts"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        results = data_manager_sqlite.search_prompts("")
        assert len(results) == 1

    def test_search_prompts_no_matches(self, data_manager_sqlite, sample_prompt_data):
        """Test search with no matches"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        results = data_manager_sqlite.search_prompts("nonexistent keyword")
        assert len(results) == 0

    def test_search_prompts_exclude_enhancement(self, data_manager_sqlite, sample_prompt_data, sample_enhancement_prompt_data):
        """Test search excluding enhancement prompts"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        # Search should find both by default
        results_all = data_manager_sqlite.search_prompts("prompt")
        assert len(results_all) == 2

        # Search excluding enhancements
        results_filtered = data_manager_sqlite.search_prompts("prompt", include_enhancement_prompts=False)
        assert len(results_filtered) == 1
        assert not results_filtered[0]["is_enhancement_prompt"]

    def test_get_prompts_by_category(self, data_manager_sqlite, sample_prompt_data):
        """Test retrieving prompts by category"""
        # Add prompt with specific category
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Another prompt with different category
        other_prompt = sample_prompt_data.copy()
        other_prompt["name"] = "other-prompt"
        other_prompt["category"] = "Other"
        data_manager_sqlite.add_prompt(**other_prompt)

        # Get prompts by specific category
        testing_prompts = data_manager_sqlite.get_prompts_by_category("Testing")
        assert len(testing_prompts) == 1
        assert testing_prompts[0]["category"] == "Testing"

        other_prompts = data_manager_sqlite.get_prompts_by_category("Other")
        assert len(other_prompts) == 1
        assert other_prompts[0]["category"] == "Other"

    def test_get_prompts_by_category_all(self, data_manager_sqlite, sample_prompt_data):
        """Test retrieving all prompts with 'All' category"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # "All" should return all prompts
        all_prompts = data_manager_sqlite.get_prompts_by_category("All")
        assert len(all_prompts) == 1

        # None should also return all prompts
        all_prompts_none = data_manager_sqlite.get_prompts_by_category(None)
        assert len(all_prompts_none) == 1

    def test_get_prompts_by_category_exclude_enhancement(self, data_manager_sqlite, sample_prompt_data, sample_enhancement_prompt_data):
        """Test get_prompts_by_category excluding enhancement prompts"""
        data_manager_sqlite.add_prompt(**sample_prompt_data)
        data_manager_sqlite.add_prompt(**sample_enhancement_prompt_data)

        # Get all prompts excluding enhancements
        prompts = data_manager_sqlite.get_prompts_by_category("All", include_enhancement_prompts=False)
        assert len(prompts) == 1
        assert not prompts[0]["is_enhancement_prompt"]

    def test_get_categories(self, data_manager_sqlite, sample_prompt_data):
        """Test retrieving unique categories"""
        # Add prompts with different categories
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        other_prompt = sample_prompt_data.copy()
        other_prompt["name"] = "other-prompt"
        other_prompt["category"] = "Development"
        data_manager_sqlite.add_prompt(**other_prompt)

        # Another prompt with same category as first
        third_prompt = sample_prompt_data.copy()
        third_prompt["name"] = "third-prompt"
        third_prompt["category"] = "Testing"
        data_manager_sqlite.add_prompt(**third_prompt)

        categories = data_manager_sqlite.get_categories()
        assert len(categories) == 2  # Should be unique
        assert "Testing" in categories
        assert "Development" in categories
        assert categories == sorted(categories)  # Should be sorted

    def test_save_config_success(self, data_manager_sqlite):
        """Test successful configuration save"""
        success = data_manager_sqlite.save_config("test_key", "test_value")
        assert success is True

        # Verify in database
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM config WHERE key = ? AND tenant_id = ? AND user_id = ?",
            ("test_key", data_manager_sqlite.tenant_id, data_manager_sqlite.user_id),
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "test_value"
        conn.close()

    def test_save_config_update_existing(self, data_manager_sqlite):
        """Test updating existing configuration"""
        # Save initial config
        data_manager_sqlite.save_config("test_key", "initial_value")

        # Update config
        success = data_manager_sqlite.save_config("test_key", "updated_value")
        assert success is True

        # Verify only one record exists with updated value
        conn = sqlite3.connect(data_manager_sqlite.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM config WHERE key = ? AND tenant_id = ? AND user_id = ?",
            ("test_key", data_manager_sqlite.tenant_id, data_manager_sqlite.user_id),
        )
        results = cursor.fetchall()
        assert len(results) == 1
        assert results[0][0] == "updated_value"
        conn.close()

    def test_save_config_tenant_user_isolation(self, temp_db):
        """Test configuration save respects tenant and user isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=user1_id)
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=user2_id)
            manager3 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=user2_id)

            # Save same key with different values
            manager1.save_config("shared_key", "value1")
            manager2.save_config("shared_key", "value2")
            manager3.save_config("shared_key", "value3")

            # Each should have their own value
            assert manager1.get_config("shared_key") == "value1"
            assert manager2.get_config("shared_key") == "value2"
            assert manager3.get_config("shared_key") == "value3"

    def test_get_config_success(self, data_manager_sqlite):
        """Test successful configuration retrieval"""
        # Save config first
        data_manager_sqlite.save_config("test_key", "test_value")

        # Get config
        value = data_manager_sqlite.get_config("test_key")
        assert value == "test_value"

    def test_get_config_nonexistent(self, data_manager_sqlite):
        """Test retrieving non-existent configuration"""
        value = data_manager_sqlite.get_config("nonexistent_key")
        assert value is None

    def test_get_config_tenant_user_isolation(self, temp_db):
        """Test configuration retrieval respects tenant and user isolation"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())

        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=user1_id)
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=user2_id)

            # Save config for manager1
            manager1.save_config("test_key", "value1")

            # manager1 should see it, manager2 should not
            value1 = manager1.get_config("test_key")
            value2 = manager2.get_config("test_key")

            assert value1 == "value1"
            assert value2 is None

    def test_config_error_handling(self, data_manager_sqlite):
        """Test configuration error handling"""
        # Mock database error for save_config
        with patch.object(data_manager_sqlite, "get_conn") as mock_get_conn:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = Exception("Database error")
            mock_get_conn.return_value = mock_conn

            success = data_manager_sqlite.save_config("test_key", "test_value")
            assert success is False

        # Mock database error for get_config
        with patch.object(data_manager_sqlite, "get_conn") as mock_get_conn:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = Exception("Database error")
            mock_get_conn.return_value = mock_conn

            value = data_manager_sqlite.get_config("test_key")
            assert value is None

    def test_database_migration_existing_table(self, temp_db, tenant_id, user_id):
        """Test database migration handles existing tables correctly"""
        # Create database with old schema (missing columns)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized'
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE config (
                key TEXT NOT NULL,
                value TEXT
            )
        """
        )
        conn.commit()
        conn.close()

        # Initialize PromptDataManager (should run migrations)
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True):
            manager = PromptDataManager(db_path=temp_db, tenant_id=tenant_id, user_id=user_id)

        # Verify new columns were added
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(prompts)")
        prompt_columns = [column[1] for column in cursor.fetchall()]
        assert "tenant_id" in prompt_columns
        assert "user_id" in prompt_columns
        assert "name" in prompt_columns
        assert "is_enhancement_prompt" in prompt_columns

        cursor.execute("PRAGMA table_info(config)")
        config_columns = [column[1] for column in cursor.fetchall()]
        assert "id" in config_columns
        assert "tenant_id" in config_columns
        assert "user_id" in config_columns
        conn.close()

    def test_prompt_ordering(self, data_manager_sqlite):
        """Test that prompts are returned in correct order"""
        # Add prompts in different categories and names
        prompts_data = [
            {"name": "z-prompt", "title": "Z Prompt", "content": "Content", "category": "B-Category", "tags": ""},
            {"name": "a-prompt", "title": "A Prompt", "content": "Content", "category": "A-Category", "tags": ""},
            {"name": "m-prompt", "title": "M Prompt", "content": "Content", "category": "A-Category", "tags": ""},
        ]

        for prompt_data in prompts_data:
            data_manager_sqlite.add_prompt(**prompt_data)

        # Get all prompts (should be ordered by category, then name)
        prompts = data_manager_sqlite.get_all_prompts()
        
        # Should be ordered by category first, then by name within category
        expected_order = ["a-prompt", "m-prompt", "z-prompt"]
        actual_order = [p["name"] for p in prompts]
        assert actual_order == expected_order

    def test_sql_injection_prevention(self, data_manager_sqlite):
        """Test that SQL injection attempts are prevented"""
        # Try SQL injection in prompt name
        malicious_name = "'; DROP TABLE prompts; --"
        result = data_manager_sqlite.add_prompt(
            name=malicious_name,
            title="Test",
            content="Content",
            category="Test",
            tags="",
        )
        
        # Should succeed (name is parameterized)
        assert "successfully" in result

        # Verify table still exists and contains the data
        prompts = data_manager_sqlite.get_all_prompts()
        assert len(prompts) == 1
        assert prompts[0]["name"] == malicious_name

        # Try SQL injection in search
        results = data_manager_sqlite.search_prompts("'; DROP TABLE prompts; --")
        # Should not cause error and return empty results
        assert isinstance(results, list)

    def test_unicode_content_handling(self, data_manager_sqlite):
        """Test handling of Unicode content"""
        unicode_prompt = {
            "name": "unicode-test",
            "title": "Unicode Test ñáéíóú 中文 🚀",
            "content": "Content with émojis 🎉 and speciál çharacters",
            "category": "Tësting",
            "tags": "unicodé, tëst",
        }

        # Add prompt with Unicode content
        result = data_manager_sqlite.add_prompt(**unicode_prompt)
        assert "successfully" in result

        # Retrieve and verify Unicode content is preserved
        prompt = data_manager_sqlite.get_prompt_by_name("unicode-test")
        assert prompt is not None
        assert prompt["title"] == unicode_prompt["title"]
        assert prompt["content"] == unicode_prompt["content"]
        assert prompt["category"] == unicode_prompt["category"]
        assert prompt["tags"] == unicode_prompt["tags"]

    def test_large_content_handling(self, data_manager_sqlite):
        """Test handling of large content"""
        large_content = "x" * 10000  # 10KB content
        
        large_prompt = {
            "name": "large-content",
            "title": "Large Content Test",
            "content": large_content,
            "category": "Testing",
            "tags": "large, test",
        }

        # Add prompt with large content
        result = data_manager_sqlite.add_prompt(**large_prompt)
        assert "successfully" in result

        # Retrieve and verify content is preserved
        prompt = data_manager_sqlite.get_prompt_by_name("large-content")
        assert prompt is not None
        assert len(prompt["content"]) == 10000
        assert prompt["content"] == large_content

    def test_concurrent_operations_safety(self, data_manager_sqlite, sample_prompt_data):
        """Test thread safety of operations (basic check)"""
        # Add a prompt
        data_manager_sqlite.add_prompt(**sample_prompt_data)

        # Simulate concurrent reads (should not interfere)
        prompt1 = data_manager_sqlite.get_prompt_by_name(sample_prompt_data["name"])
        prompt2 = data_manager_sqlite.get_prompt_by_name(sample_prompt_data["name"])
        all_prompts = data_manager_sqlite.get_all_prompts()

        assert prompt1 is not None
        assert prompt2 is not None
        assert len(all_prompts) == 1
        assert prompt1["name"] == prompt2["name"] == sample_prompt_data["name"]