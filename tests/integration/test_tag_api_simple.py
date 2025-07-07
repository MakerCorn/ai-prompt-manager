"""
Simple integration tests for tag management API endpoints.

This module tests the tag management REST API endpoints
with real database interactions in single-user mode.
"""

import os
import tempfile
import unittest

# Import test dependencies
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.middleware.sessions import SessionMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from prompt_data_manager import PromptDataManager

if FASTAPI_AVAILABLE:
    from api_endpoints_enhanced import get_ai_models_router


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestTagAPISimple(unittest.TestCase):
    """Simple integration tests for tag management API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Set environment variables for single-user mode
        os.environ["DB_PATH"] = self.temp_db.name
        os.environ["MULTITENANT_MODE"] = "false"
        os.environ["LOCAL_DEV_MODE"] = "true"

        # Create FastAPI app with tag router and middleware
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="test-secret-key")
        self.app.include_router(get_ai_models_router())
        self.client = TestClient(self.app)

        # Initialize data manager and add test data
        self.data_manager = PromptDataManager(
            db_path=self.temp_db.name, tenant_id="single-user", user_id="single-user"
        )

        # Create test prompts with tags
        self.data_manager.add_prompt(
            name="API Test Prompt 1",
            title="First API Test Prompt",
            content="This is API test content",
            category="API Testing",
            tags="api, testing, python, automation",
        )

        self.data_manager.add_prompt(
            name="API Test Prompt 2",
            title="Second API Test Prompt",
            content="More API test content",
            category="Development",
            tags="api, development, web, javascript",
        )

        # Create test template with tags
        self.data_manager.create_template(
            name="API Test Template",
            description="API test template",
            content="Template content with {variable}",
            category="Custom",
            tags="template, api, testing",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        if "DB_PATH" in os.environ:
            del os.environ["DB_PATH"]
        if "MULTITENANT_MODE" in os.environ:
            del os.environ["MULTITENANT_MODE"]
        if "LOCAL_DEV_MODE" in os.environ:
            del os.environ["LOCAL_DEV_MODE"]
        os.unlink(self.temp_db.name)

    def test_get_all_tags_endpoint(self):
        """Test GET /api/ai-models/tags endpoint."""
        # Test all entity types
        response = self.client.get("/api/ai-models/tags?entity_type=all")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        self.assertIn("tags", data)

        # Check that expected tags are present
        tags = data["tags"]
        expected_tags = {
            "api",
            "testing",
            "python",
            "automation",
            "development",
            "web",
            "javascript",
            "template",
        }
        self.assertTrue(expected_tags.issubset(set(tags)))

    def test_tag_statistics_endpoint(self):
        """Test GET /api/ai-models/tags/statistics endpoint."""
        response = self.client.get("/api/ai-models/tags/statistics")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("statistics", data)
        self.assertIn("popular_tags", data)

        # Check statistics structure
        stats = data["statistics"]
        self.assertIn("api", stats)
        self.assertIn("testing", stats)

        # Check that api tag appears in both prompts and templates
        api_stats = stats["api"]
        self.assertEqual(api_stats["prompts"], 2)
        self.assertEqual(api_stats["templates"], 1)
        self.assertEqual(api_stats["total"], 3)

    def test_search_by_tags_endpoint(self):
        """Test POST /api/ai-models/tags/search endpoint."""
        # Test OR search
        search_request = {
            "tags": ["api", "python"],
            "entity_type": "prompts",
            "match_all": False,
            "include_enhancement_prompts": True,
        }

        response = self.client.post("/api/ai-models/tags/search", json=search_request)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["search_params"]["logic"], "OR")

        # Should find both prompts (both have 'api' tag)
        self.assertEqual(data["count"], 2)

    def test_suggest_tags_endpoint(self):
        """Test POST /api/ai-models/tags/suggest endpoint."""
        # Test tag suggestion
        suggestion_request = {"partial_tag": "ap", "limit": 5}

        response = self.client.post(
            "/api/ai-models/tags/suggest", json=suggestion_request
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("suggestions", data)
        self.assertEqual(data["partial_tag"], "ap")

        # Should suggest "api"
        suggestions = data["suggestions"]
        self.assertIn("api", suggestions)


if __name__ == "__main__":
    unittest.main()
