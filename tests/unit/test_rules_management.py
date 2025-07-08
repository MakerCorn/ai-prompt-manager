"""
Comprehensive unit tests for Rules Management functionality
Testing database operations, CRUD operations, and multi-tenant isolation for rules
"""

import os
import sqlite3
import tempfile
import uuid
from unittest.mock import MagicMock, patch

import pytest

from prompt_data_manager import PromptDataManager


class TestRulesManagement:
    """Test suite for Rules management functionality"""

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
            return PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=user_id
            )

    @pytest.fixture
    def postgres_data_manager(self, tenant_id, user_id):
        """Create PromptDataManager instance configured for PostgreSQL"""
        with patch("prompt_data_manager.POSTGRES_AVAILABLE", True):
            with patch("prompt_data_manager.DB_TYPE", "postgres"):
                with patch(
                    "prompt_data_manager.POSTGRES_DSN",
                    "postgresql://test:test@localhost:5432/test",
                ):
                    with patch("prompt_data_manager.psycopg2") as mock_psycopg2:
                        mock_conn = MagicMock()
                        mock_cursor = MagicMock()
                        mock_conn.cursor.return_value = mock_cursor
                        mock_psycopg2.connect.return_value = mock_conn
                        manager = PromptDataManager(
                            tenant_id=tenant_id, user_id=user_id
                        )
                        return manager

    @pytest.fixture
    def sample_rule_data(self):
        """Sample rule data for testing"""
        return {
            "name": "test-rule",
            "title": "Test Rule",
            "content": "# Test Rule\\n\\n## Guidelines\\n- Be specific\\n- Be clear\\n- Be helpful",
            "category": "Testing",
            "tags": "test, guidelines, unit",
            "description": "A test rule for unit testing",
            "is_builtin": False,
        }

    @pytest.fixture
    def sample_builtin_rule_data(self):
        """Sample built-in rule data for testing"""
        return {
            "name": "builtin-rule",
            "title": "Built-in Rule",
            "content": "# Built-in Rule\\n\\n## System Guidelines\\n- Follow system constraints\\n- Maintain consistency",
            "category": "System",
            "tags": "builtin, system",
            "description": "A built-in system rule",
            "is_builtin": True,
        }

    def test_rules_table_creation_sqlite(self, temp_db, tenant_id, user_id):
        """Test that rules table is created correctly in SQLite"""
        with patch.dict(
            os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True
        ):
            PromptDataManager(db_path=temp_db, tenant_id=tenant_id, user_id=user_id)

            # Check that rules table exists
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='rules'"
            )
            result = cursor.fetchone()
            conn.close()

            assert result is not None
            assert result[0] == "rules"

    def test_add_rule_sqlite(self, data_manager_sqlite, sample_rule_data):
        """Test adding a rule with SQLite"""
        result = data_manager_sqlite.add_rule(**sample_rule_data)
        assert "successfully" in result.lower()

    def test_add_rule_postgres(self, postgres_data_manager, sample_rule_data):
        """Test adding a rule with PostgreSQL"""
        # Mock the cursor execute and commit
        with patch.object(postgres_data_manager, "get_conn") as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            result = postgres_data_manager.add_rule(**sample_rule_data)

            # Verify execute was called with correct SQL
            mock_cursor.execute.assert_called_once()
            call_args = mock_cursor.execute.call_args[0]
            assert "INSERT INTO rules" in call_args[0]
            assert "successfully" in result.lower()

    def test_add_rule_missing_required_fields(self, data_manager_sqlite):
        """Test adding rule with missing required fields"""
        # Test missing name
        result = data_manager_sqlite.add_rule(name="", title="Test", content="Content")
        assert "required" in result.lower()

        # Test missing title
        result = data_manager_sqlite.add_rule(name="test", title="", content="Content")
        assert "required" in result.lower()

        # Test missing content
        result = data_manager_sqlite.add_rule(name="test", title="Test", content="")
        assert "required" in result.lower()

    def test_add_duplicate_rule(self, data_manager_sqlite, sample_rule_data):
        """Test adding duplicate rule names"""
        # Add first rule
        result1 = data_manager_sqlite.add_rule(**sample_rule_data)
        assert "successfully" in result1.lower()

        # Try to add duplicate
        result2 = data_manager_sqlite.add_rule(**sample_rule_data)
        assert "already exists" in result2.lower()

    def test_get_all_rules_empty(self, data_manager_sqlite):
        """Test getting all rules when none exist"""
        rules = data_manager_sqlite.get_all_rules()
        assert rules == []

    def test_get_all_rules_with_data(
        self, data_manager_sqlite, sample_rule_data, sample_builtin_rule_data
    ):
        """Test getting all rules with existing data"""
        # Add rules
        data_manager_sqlite.add_rule(**sample_rule_data)
        data_manager_sqlite.add_rule(**sample_builtin_rule_data)

        rules = data_manager_sqlite.get_all_rules()
        assert len(rules) == 2

        # Check rule properties
        rule_names = [rule["name"] for rule in rules]
        assert "test-rule" in rule_names
        assert "builtin-rule" in rule_names

        # Check built-in flag
        builtin_rule = next(rule for rule in rules if rule["name"] == "builtin-rule")
        assert builtin_rule["is_builtin"] is True

    def test_get_rule_by_name(self, data_manager_sqlite, sample_rule_data):
        """Test getting rule by name"""
        # Add rule
        data_manager_sqlite.add_rule(**sample_rule_data)

        # Get by name
        rule = data_manager_sqlite.get_rule_by_name("test-rule")
        assert rule is not None
        assert rule["name"] == "test-rule"
        assert rule["title"] == "Test Rule"
        assert rule["category"] == "Testing"

        # Test non-existent rule
        rule = data_manager_sqlite.get_rule_by_name("non-existent")
        assert rule is None

    def test_update_rule(self, data_manager_sqlite, sample_rule_data):
        """Test updating existing rule"""
        # Add rule
        data_manager_sqlite.add_rule(**sample_rule_data)

        # Update rule
        result = data_manager_sqlite.update_rule(
            original_name="test-rule",
            name="updated-rule",
            title="Updated Rule",
            content="# Updated Rule\\n\\nNew content",
            category="Updated",
            tags="updated, modified",
            description="Updated description",
        )
        assert "successfully" in result.lower()

        # Verify update
        rule = data_manager_sqlite.get_rule_by_name("updated-rule")
        assert rule is not None
        assert rule["title"] == "Updated Rule"
        assert rule["category"] == "Updated"

    def test_update_nonexistent_rule(self, data_manager_sqlite):
        """Test updating non-existent rule"""
        result = data_manager_sqlite.update_rule(
            original_name="non-existent", name="test", title="Test", content="Content"
        )
        assert "not found" in result.lower()

    def test_delete_rule(self, data_manager_sqlite, sample_rule_data):
        """Test deleting existing rule"""
        # Add rule
        data_manager_sqlite.add_rule(**sample_rule_data)

        # Verify it exists
        rule = data_manager_sqlite.get_rule_by_name("test-rule")
        assert rule is not None

        # Delete rule
        result = data_manager_sqlite.delete_rule("test-rule")
        assert "successfully" in result.lower()

        # Verify deletion
        rule = data_manager_sqlite.get_rule_by_name("test-rule")
        assert rule is None

    def test_delete_nonexistent_rule(self, data_manager_sqlite):
        """Test deleting non-existent rule"""
        result = data_manager_sqlite.delete_rule("non-existent")
        assert "not found" in result.lower()

    def test_search_rules(self, data_manager_sqlite, sample_rule_data):
        """Test searching rules by content"""
        # Add multiple rules
        data_manager_sqlite.add_rule(**sample_rule_data)

        rule2_data = sample_rule_data.copy()
        rule2_data.update(
            {
                "name": "coding-rule",
                "title": "Coding Guidelines",
                "content": "# Coding Rule\\n\\n## Programming Guidelines\\n- Write clean code",
                "category": "Coding",
                "tags": "coding, programming",
            }
        )
        data_manager_sqlite.add_rule(**rule2_data)

        # Search by title
        results = data_manager_sqlite.search_rules("Coding")
        assert len(results) == 1
        assert results[0]["name"] == "coding-rule"

        # Search by content
        results = data_manager_sqlite.search_rules("Guidelines")
        assert len(results) >= 1

        # Search by tag
        results = data_manager_sqlite.search_rules("programming")
        assert len(results) == 1
        assert results[0]["name"] == "coding-rule"

    def test_get_rules_by_category(self, data_manager_sqlite, sample_rule_data):
        """Test getting rules by category"""
        # Add rules in different categories
        data_manager_sqlite.add_rule(**sample_rule_data)

        coding_rule = sample_rule_data.copy()
        coding_rule.update({"name": "coding-rule", "category": "Coding"})
        data_manager_sqlite.add_rule(**coding_rule)

        # Get rules by category
        testing_rules = data_manager_sqlite.get_rules_by_category("Testing")
        assert len(testing_rules) == 1
        assert testing_rules[0]["name"] == "test-rule"

        coding_rules = data_manager_sqlite.get_rules_by_category("Coding")
        assert len(coding_rules) == 1
        assert coding_rules[0]["name"] == "coding-rule"

    def test_tenant_isolation(self, temp_db):
        """Test that rules are properly isolated by tenant"""
        with patch.dict(
            os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True
        ):
            tenant1_id = str(uuid.uuid4())
            tenant2_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())

            # Create managers for different tenants
            manager1 = PromptDataManager(
                db_path=temp_db, tenant_id=tenant1_id, user_id=user_id
            )
            manager2 = PromptDataManager(
                db_path=temp_db, tenant_id=tenant2_id, user_id=user_id
            )

            # Add rule to tenant 1
            manager1.add_rule(
                name="tenant1-rule",
                title="Tenant 1 Rule",
                content="Tenant 1 content",
                category="Testing",
            )

            # Add rule to tenant 2
            manager2.add_rule(
                name="tenant2-rule",
                title="Tenant 2 Rule",
                content="Tenant 2 content",
                category="Testing",
            )

            # Verify isolation
            tenant1_rules = manager1.get_all_rules()
            tenant2_rules = manager2.get_all_rules()

            assert len(tenant1_rules) == 1
            assert len(tenant2_rules) == 1
            assert tenant1_rules[0]["name"] == "tenant1-rule"
            assert tenant2_rules[0]["name"] == "tenant2-rule"

            # Verify cross-tenant access is blocked
            assert manager1.get_rule_by_name("tenant2-rule") is None
            assert manager2.get_rule_by_name("tenant1-rule") is None

    def test_tag_integration_with_rules(self, data_manager_sqlite, sample_rule_data):
        """Test that rules integrate properly with tag management"""
        # Add rule with tags
        data_manager_sqlite.add_rule(**sample_rule_data)

        # Get all tags including rules
        all_tags = data_manager_sqlite.get_all_tags(entity_type="all")
        rule_tags = data_manager_sqlite.get_all_tags(entity_type="rules")

        # Verify rule tags are included
        assert "test" in all_tags
        assert "guidelines" in all_tags
        assert "unit" in all_tags

        assert "test" in rule_tags
        assert "guidelines" in rule_tags
        assert "unit" in rule_tags

        # Get tag statistics
        tag_stats = data_manager_sqlite.get_tag_statistics()
        assert "test" in tag_stats
        assert tag_stats["test"]["rules"] == 1
        assert tag_stats["test"]["total"] == 1

    def test_rules_with_markdown_content(self, data_manager_sqlite):
        """Test rules with complex markdown content"""
        markdown_content = """# Complex Rule

## Purpose
This rule demonstrates complex markdown formatting.

## Guidelines
1. **Bold text** for emphasis
2. *Italic text* for subtle emphasis
3. `Code snippets` for technical terms

### Sub-guidelines
- Use bullet points
- Include examples
- Be specific

## Code Example
```python
def example_function():
    return "Hello, World!"
```

> Important note in blockquote

## Links and References
- [Documentation](https://example.com)
- See also: Other Rule Name

---

*End of rule*"""

        result = data_manager_sqlite.add_rule(
            name="markdown-rule",
            title="Markdown Rule Example",
            content=markdown_content,
            category="Documentation",
            tags="markdown, formatting, complex",
            description="Example of complex markdown in rules",
        )

        assert "successfully" in result.lower()

        # Retrieve and verify
        rule = data_manager_sqlite.get_rule_by_name("markdown-rule")
        assert rule is not None
        assert "# Complex Rule" in rule["content"]
        assert "```python" in rule["content"]
        assert "## Guidelines" in rule["content"]

    def test_builtin_rules_protection(
        self, data_manager_sqlite, sample_builtin_rule_data
    ):
        """Test that built-in rules are properly marked and handled"""
        # Add built-in rule
        data_manager_sqlite.add_rule(**sample_builtin_rule_data)

        # Verify built-in flag
        rule = data_manager_sqlite.get_rule_by_name("builtin-rule")
        assert rule is not None
        assert rule["is_builtin"] is True

        # Note: Protection logic (preventing deletion/modification)
        # would be implemented in the UI/API layer, not in the data layer

    def test_rules_with_special_characters(self, data_manager_sqlite):
        """Test rules with special characters and unicode"""
        special_content = """# Règle Spéciale

## Directives 特殊
- Use émojis: 🎯 📝 ✅
- Handle unicode: αβγ δεζ
- Special chars: @#$%^&*()
- Quotes: "double" 'single' `backtick`

## Code with Special Chars
```javascript
const message = "Hello, 世界!";
console.log(`Message: ${message} 🌍`);
```"""

        result = data_manager_sqlite.add_rule(
            name="special-chars-rule",
            title="Règle avec Caractères Spéciaux",
            content=special_content,
            category="Spécial",
            tags="unicode, émojis, special",
            description="Testing special characters and unicode",
        )

        assert "successfully" in result.lower()

        # Retrieve and verify
        rule = data_manager_sqlite.get_rule_by_name("special-chars-rule")
        assert rule is not None
        assert "🎯" in rule["content"]
        assert "世界" in rule["content"]
        assert "αβγ" in rule["content"]

    def test_empty_tenant_or_user_handling(self, temp_db):
        """Test handling of empty tenant_id or user_id"""
        with patch.dict(
            os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}, clear=True
        ):
            # Test with empty tenant_id
            manager = PromptDataManager(
                db_path=temp_db, tenant_id="", user_id="test-user"
            )

            result = manager.add_rule(name="test", title="Test", content="Content")
            assert "required" in result.lower()

            rules = manager.get_all_rules()
            assert rules == []

    def test_long_content_handling(self, data_manager_sqlite):
        """Test handling of very long rule content"""
        long_content = "# Long Rule\n\n" + "This is a very long line. " * 1000

        result = data_manager_sqlite.add_rule(
            name="long-rule",
            title="Long Content Rule",
            content=long_content,
            category="Testing",
        )

        assert "successfully" in result.lower()

        # Retrieve and verify
        rule = data_manager_sqlite.get_rule_by_name("long-rule")
        assert rule is not None
        assert len(rule["content"]) > 10000
