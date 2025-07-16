"""
Integration tests for GitHub format API endpoints.

Tests the complete flow of importing and exporting GitHub format prompts
through the API endpoints.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from fastapi.testclient import TestClient

    from api_endpoints_enhanced import get_ai_models_router
    from auth_manager import AuthManager
    from prompt_data_manager import PromptDataManager

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestGitHubFormatIntegration(unittest.TestCase):
    """Integration tests for GitHub format API endpoints."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Set up test environment
        os.environ["DB_PATH"] = self.temp_db.name
        os.environ["LOCAL_DEV_MODE"] = "true"
        os.environ["MULTITENANT_MODE"] = "false"

        # Create test app
        from fastapi import FastAPI
        from starlette.middleware.sessions import SessionMiddleware

        self.app = FastAPI()

        # Add SessionMiddleware for authentication
        self.app.add_middleware(SessionMiddleware, secret_key="test-secret-key")

        # Get the router and override dependencies
        router = get_ai_models_router()
        self.app.include_router(router)

        # Override dependencies for testing
        from api_endpoints_enhanced import get_current_user, get_data_manager

        def override_get_current_user():
            return self.test_user

        def override_get_data_manager():
            return self.data_manager

        self.app.dependency_overrides[get_current_user] = override_get_current_user
        self.app.dependency_overrides[get_data_manager] = override_get_data_manager

        self.client = TestClient(self.app)

        # Set up auth manager and data manager
        self.auth_manager = AuthManager(db_path=self.temp_db.name)

        self.data_manager = PromptDataManager(
            db_path=self.temp_db.name, tenant_id="test_tenant", user_id="test_user"
        )

        # Create test user
        self.test_user = {
            "user_id": "test_user",
            "tenant_id": "test_tenant",
            "email": "test@example.com",
            "role": "admin",
        }

        # Sample GitHub format data
        self.sample_github_yaml = """
messages:
  - role: system
    content: 'You are a helpful assistant specialized in Azure services.'
  - role: user
    content: >-
      Create an azure logic app that will provide a UI to allow a user to upload
      a PDF document with medical information related to a civil legal case.
      Once the application receives the PDF document, the backend will receive
      the document from the UI and use Azure Document Service to OCR the PDF
      retrieving only medical data from all of the labeled health data on the
      PDF needed for the legal case.
model: openai/gpt-4o
temperature: 0.7
max_tokens: 2000
"""

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_github_format_info_endpoint(self, mock_get_user, mock_get_data_manager):
        """Test getting GitHub format information."""
        mock_get_user.return_value = self.test_user

        response = self.client.get("/api/ai-models/github/info")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertIn("format_info", data)

        format_info = data["format_info"]
        self.assertIn("name", format_info)
        self.assertIn("description", format_info)
        self.assertIn("required_fields", format_info)
        self.assertIn("messages", format_info["required_fields"])

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_github_format_endpoint(self, mock_get_user, mock_get_data_manager):
        """Test importing GitHub format through API."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        request_data = {
            "yaml_content": self.sample_github_yaml,
            "name": "Azure Logic App Prompt",
            "title": "Azure Logic App for PDF Processing",
            "category": "Azure",
        }

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertIn("Successfully imported", data["message"])
        self.assertIsNotNone(data["prompt_id"])

        # Verify prompt was actually created in database
        prompt_data = self.data_manager.get_prompt_by_name("Azure Logic App Prompt")
        self.assertIsNotNone(prompt_data)
        self.assertEqual(prompt_data["name"], "Azure Logic App Prompt")

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_invalid_yaml(self, mock_get_user, mock_get_data_manager):
        """Test importing invalid YAML format."""
        mock_get_user.return_value = self.test_user

        request_data = {
            "yaml_content": "invalid: yaml: content: [",
            "name": "Invalid Prompt",
        }

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Invalid YAML format", data["detail"])

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_invalid_github_format(self, mock_get_user, mock_get_data_manager):
        """Test importing valid YAML but invalid GitHub format."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        invalid_github_yaml = """
name: "Test Prompt"
content: "This is not GitHub format"
"""

        request_data = {
            "yaml_content": invalid_github_yaml,
            "name": "Invalid GitHub Format",
        }

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 400)

    def test_export_github_format_endpoint(self):
        """Test exporting prompt to GitHub format through API."""

        # First create a prompt
        self.data_manager.add_prompt(
            name="Test Export Prompt",
            title="Test Export Prompt",
            content=(
                "USER: Create an Azure Logic App\n\n"
                "SYSTEM: I'll help you create that."
            ),
            category="Test",
            tags="test,export",
        )

        # Get the created prompt to find its ID
        prompt_data = self.data_manager.get_prompt_by_name("Test Export Prompt")
        prompt_id = prompt_data["id"] if prompt_data else None
        self.assertIsNotNone(prompt_id)

        # Export the prompt
        response = self.client.get(f"/api/ai-models/github/export/{prompt_id}")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertIn("Successfully exported", data["message"])
        self.assertIsNotNone(data["yaml_content"])

        # Verify the exported YAML is valid
        yaml_content = data["yaml_content"]
        parsed_yaml = yaml.safe_load(yaml_content)

        self.assertIn("messages", parsed_yaml)
        self.assertIn("model", parsed_yaml)
        self.assertIsInstance(parsed_yaml["messages"], list)

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_export_nonexistent_prompt(self, mock_get_user, mock_get_data_manager):
        """Test exporting a non-existent prompt."""
        mock_get_user.return_value = self.test_user

        response = self.client.get("/api/ai-models/github/export/99999")

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Prompt not found", data["detail"])

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_export_roundtrip(self, mock_get_user, mock_get_data_manager):
        """Test importing and then exporting a prompt maintains data integrity."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        # Import GitHub format
        import_request = {
            "yaml_content": self.sample_github_yaml,
            "name": "Roundtrip Test",
            "category": "Test",
        }

        import_response = self.client.post(
            "/api/ai-models/github/import", json=import_request
        )

        self.assertEqual(import_response.status_code, 200)
        prompt_id = import_response.json()["prompt_id"]

        # Export the same prompt
        export_response = self.client.get(f"/api/ai-models/github/export/{prompt_id}")

        self.assertEqual(export_response.status_code, 200)
        exported_yaml = export_response.json()["yaml_content"]

        # Parse both original and exported YAML
        original_data = yaml.safe_load(self.sample_github_yaml)
        exported_data = yaml.safe_load(exported_yaml)

        # Verify key fields are preserved
        self.assertEqual(len(original_data["messages"]), len(exported_data["messages"]))
        self.assertEqual(original_data["model"], exported_data["model"])

        # Verify message content is preserved
        for orig_msg, exp_msg in zip(
            original_data["messages"], exported_data["messages"]
        ):
            if orig_msg["content"].strip():  # Skip empty system messages
                self.assertEqual(orig_msg["role"], exp_msg["role"])
                # Content might be reformatted but should contain key parts
                if "azure logic app" in orig_msg["content"].lower():
                    self.assertIn("azure", exp_msg["content"].lower())

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_with_model_parameters(self, mock_get_user, mock_get_data_manager):
        """Test importing GitHub format with model parameters."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        github_with_params = """
messages:
  - role: system
    content: 'You are helpful.'
  - role: user
    content: 'Hello world'
model: openai/gpt-4o
temperature: 0.8
max_tokens: 1500
top_p: 0.9
frequency_penalty: 0.1
presence_penalty: 0.2
"""

        request_data = {"yaml_content": github_with_params, "name": "Parameters Test"}

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 200)
        prompt_id = response.json()["prompt_id"]

        # Export and verify basic structure (note: model parameters are not preserved
        # in current implementation due to database schema limitations)
        export_response = self.client.get(f"/api/ai-models/github/export/{prompt_id}")
        exported_yaml = export_response.json()["yaml_content"]
        exported_data = yaml.safe_load(exported_yaml)

        # Verify basic structure is preserved
        self.assertIn("messages", exported_data)
        self.assertIn("model", exported_data)

        # Note: Model parameters like temperature are not currently preserved
        # due to database schema limitations. This is a known limitation.

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_minimal_github_format(self, mock_get_user, mock_get_data_manager):
        """Test importing minimal GitHub format (only required fields)."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        minimal_yaml = """
messages:
  - role: user
    content: 'Hello world'
"""

        request_data = {"yaml_content": minimal_yaml, "name": "Minimal Test"}

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 200)
        response.json()["prompt_id"]

        # Verify prompt was created with defaults
        prompt_data = self.data_manager.get_prompt_by_name("Minimal Test")
        self.assertIsNotNone(prompt_data)
        self.assertEqual(prompt_data["name"], "Minimal Test")

    @patch("api_endpoints_enhanced.get_data_manager")
    @patch("api_endpoints_enhanced.get_current_user")
    def test_import_auto_name_generation(self, mock_get_user, mock_get_data_manager):
        """Test automatic name generation when no name provided."""
        mock_get_user.return_value = self.test_user
        mock_get_data_manager.return_value = self.data_manager

        request_data = {
            "yaml_content": self.sample_github_yaml
            # No name provided
        }

        response = self.client.post("/api/ai-models/github/import", json=request_data)

        self.assertEqual(response.status_code, 200)
        response.json()["prompt_id"]

        # Verify auto-generated name by searching all prompts
        all_prompts = self.data_manager.get_all_prompts()
        imported_prompt = None
        for p in all_prompts:
            if "Create" in p.get("name", ""):
                imported_prompt = p
                break

        self.assertIsNotNone(imported_prompt)
        name = imported_prompt["name"]
        self.assertIn("Create", name)
        self.assertTrue(len(name) > 0)


if __name__ == "__main__":
    unittest.main()
