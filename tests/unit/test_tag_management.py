"""
Unit tests for the tag management system.

This module tests tag functionality across prompts and templates,
including tag operations, search, and statistics.
"""

import os
import tempfile
import unittest

from prompt_data_manager import PromptDataManager

# test imports removed: unused MagicMock, patch


class TestTagManagement(unittest.TestCase):
    """Test cases for tag management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Initialize data manager with test tenant
        self.data_manager = PromptDataManager(
            db_path=self.temp_db.name, tenant_id="test-tenant", user_id="test-user"
        )

        # Create test prompts with tags
        self.data_manager.add_prompt(
            name="Test Prompt 1",
            title="First Test Prompt",
            content="This is test content",
            category="Testing",
            tags="python, testing, automation",
        )

        self.data_manager.add_prompt(
            name="Test Prompt 2",
            title="Second Test Prompt",
            content="More test content",
            category="Development",
            tags="python, development, web",
        )

        # Create test template with tags
        self.data_manager.create_template(
            name="Test Template 1",
            description="Test template",
            content="Template content with {variable}",
            category="Custom",
            tags="template, automation, testing",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_get_all_tags(self):
        """Test retrieving all unique tags."""
        # Test all entity types
        all_tags = self.data_manager.get_all_tags("all")
        expected_tags = {
            "python",
            "testing",
            "automation",
            "development",
            "web",
            "template",
        }
        self.assertEqual(set(all_tags), expected_tags)

        # Test prompts only
        prompt_tags = self.data_manager.get_all_tags("prompts")
        expected_prompt_tags = {"python", "testing", "automation", "development", "web"}
        self.assertEqual(set(prompt_tags), expected_prompt_tags)

        # Test templates only
        template_tags = self.data_manager.get_all_tags("templates")
        expected_template_tags = {"template", "automation", "testing"}
        self.assertEqual(set(template_tags), expected_template_tags)

    def test_search_by_tags_or_logic(self):
        """Test tag-based search with OR logic."""
        # Search for prompts with python OR web tags
        results = self.data_manager.search_by_tags(
            tags=["python", "web"], entity_type="prompts", match_all=False
        )

        self.assertEqual(len(results), 2)
        result_names = {result["name"] for result in results}
        self.assertEqual(result_names, {"Test Prompt 1", "Test Prompt 2"})

    def test_search_by_tags_and_logic(self):
        """Test tag-based search with AND logic."""
        # Search for prompts with both python AND testing tags
        results = self.data_manager.search_by_tags(
            tags=["python", "testing"], entity_type="prompts", match_all=True
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Test Prompt 1")

    def test_search_templates_by_tags(self):
        """Test tag-based search for templates."""
        results = self.data_manager.search_by_tags(
            tags=["template"], entity_type="templates", match_all=False
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Test Template 1")

    def test_tag_statistics(self):
        """Test tag usage statistics."""
        stats = self.data_manager.get_tag_statistics()

        # Check that all tags are present
        expected_tags = {
            "python",
            "testing",
            "automation",
            "development",
            "web",
            "template",
        }
        self.assertEqual(set(stats.keys()), expected_tags)

        # Check specific tag counts
        self.assertEqual(stats["python"]["prompts"], 2)
        self.assertEqual(stats["python"]["templates"], 0)
        self.assertEqual(stats["python"]["total"], 2)

        self.assertEqual(stats["testing"]["prompts"], 1)
        self.assertEqual(stats["testing"]["templates"], 1)
        self.assertEqual(stats["testing"]["total"], 2)

        self.assertEqual(stats["template"]["prompts"], 0)
        self.assertEqual(stats["template"]["templates"], 1)
        self.assertEqual(stats["template"]["total"], 1)

    def test_popular_tags(self):
        """Test popular tags functionality."""
        # Test all entity types
        popular_all = self.data_manager.get_popular_tags("all", limit=5)
        self.assertGreater(len(popular_all), 0)

        # Check that results are sorted by count (descending)
        if len(popular_all) > 1:
            self.assertGreaterEqual(popular_all[0]["count"], popular_all[1]["count"])

        # Test prompts only
        popular_prompts = self.data_manager.get_popular_tags("prompts", limit=5)
        self.assertGreater(len(popular_prompts), 0)

        # Test templates only
        popular_templates = self.data_manager.get_popular_tags("templates", limit=5)
        self.assertGreater(len(popular_templates), 0)

    def test_suggest_tags(self):
        """Test tag suggestions."""
        # Test prefix matching
        suggestions = self.data_manager.suggest_tags("pyt")
        self.assertIn("python", suggestions)

        # Test substring matching
        suggestions = self.data_manager.suggest_tags("est")
        self.assertIn("testing", suggestions)

        # Test empty query
        suggestions = self.data_manager.suggest_tags("")
        self.assertEqual(suggestions, [])

        # Test non-matching query
        suggestions = self.data_manager.suggest_tags("nonexistent")
        self.assertEqual(suggestions, [])

    def test_empty_database_tags(self):
        """Test tag operations on empty database."""
        # Create new data manager with empty database
        temp_empty_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_empty_db.close()

        try:
            empty_dm = PromptDataManager(
                db_path=temp_empty_db.name,
                tenant_id="empty-tenant",
                user_id="empty-user",
            )

            # Test empty results
            self.assertEqual(empty_dm.get_all_tags(), [])
            self.assertEqual(empty_dm.get_tag_statistics(), {})
            self.assertEqual(empty_dm.get_popular_tags(), [])
            self.assertEqual(empty_dm.suggest_tags("test"), [])
            self.assertEqual(empty_dm.search_by_tags(["test"]), [])

        finally:
            os.unlink(temp_empty_db.name)

    def test_tag_case_handling(self):
        """Test tag case sensitivity and normalization."""
        # Add prompt with mixed case tags
        self.data_manager.add_prompt(
            name="Case Test",
            title="Case Test Prompt",
            content="Testing case handling",
            category="Testing",
            tags="Python, TESTING, WebDev",
        )

        # Tags should be case-sensitive as stored
        all_tags = self.data_manager.get_all_tags()
        self.assertIn("Python", all_tags)
        self.assertIn("TESTING", all_tags)
        self.assertIn("WebDev", all_tags)

        # Search should find the case-specific tag
        results = self.data_manager.search_by_tags(["Python"])
        self.assertGreater(len(results), 0)

        # Verify the specific prompt is found
        result_names = {result["name"] for result in results}
        self.assertIn("Case Test", result_names)

    def test_special_characters_in_tags(self):
        """Test handling of special characters in tags."""
        # Add prompt with special characters in tags
        self.data_manager.add_prompt(
            name="Special Chars Test",
            title="Special Characters Test",
            content="Testing special characters",
            category="Testing",
            tags="c++, .net, web-dev, api_testing",
        )

        all_tags = self.data_manager.get_all_tags()
        self.assertIn("c++", all_tags)
        self.assertIn(".net", all_tags)
        self.assertIn("web-dev", all_tags)
        self.assertIn("api_testing", all_tags)

    def test_tag_whitespace_handling(self):
        """Test proper handling of whitespace in tags."""
        # Add prompt with whitespace variations
        self.data_manager.add_prompt(
            name="Whitespace Test",
            title="Whitespace Test Prompt",
            content="Testing whitespace",
            category="Testing",
            tags="  spaced  ,  trimmed  , normal",
        )

        all_tags = self.data_manager.get_all_tags()
        # Tags should be trimmed
        self.assertIn("spaced", all_tags)
        self.assertIn("trimmed", all_tags)
        self.assertIn("normal", all_tags)

        # Should not contain tags with leading/trailing spaces
        whitespace_tags = [
            tag for tag in all_tags if tag.startswith(" ") or tag.endswith(" ")
        ]
        self.assertEqual(len(whitespace_tags), 0)


class TestTagModel(unittest.TestCase):
    """Test cases for tag-related functionality in Prompt and Template models."""

    def test_prompt_tag_operations(self):
        """Test Prompt model tag operations."""
        from src.prompts.models.prompt import Prompt

        prompt = Prompt(
            tenant_id="test-tenant",
            user_id="test-user",
            name="Test Prompt",
            title="Test Title",
            content="Test content",
            tags="python, testing",
        )

        # Test tag_list property
        self.assertEqual(prompt.tag_list, ["python", "testing"])

        # Test add_tag
        prompt.add_tag("automation")
        self.assertIn("automation", prompt.tag_list)

        # Test remove_tag
        prompt.remove_tag("testing")
        self.assertNotIn("testing", prompt.tag_list)

        # Test has_tag
        self.assertTrue(prompt.has_tag("python"))
        self.assertFalse(prompt.has_tag("nonexistent"))

        # Test setting tag_list
        prompt.tag_list = ["new", "tags", "list"]
        self.assertEqual(set(prompt.tag_list), {"new", "tags", "list"})

    def test_template_tag_operations(self):
        """Test Template model tag operations."""
        from src.templates.models.template import Template

        template = Template(
            tenant_id="test-tenant",
            user_id="test-user",
            name="Test Template",
            description="Test description",
            content="Test content with {variable}",
            tags="template, automation",
        )

        # Test tag_list property
        self.assertEqual(template.tag_list, ["template", "automation"])

        # Test add_tag
        template.add_tag("testing")
        self.assertIn("testing", template.tag_list)

        # Test remove_tag
        template.remove_tag("automation")
        self.assertNotIn("automation", template.tag_list)

        # Test has_tag
        self.assertTrue(template.has_tag("template"))
        self.assertFalse(template.has_tag("nonexistent"))


if __name__ == "__main__":
    unittest.main()
