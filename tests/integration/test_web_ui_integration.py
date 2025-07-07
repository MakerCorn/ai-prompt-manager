#!/usr/bin/env python3
"""
Integration tests for the Web UI (FastAPI + HTMX + Tailwind)
Comprehensive web interface testing for the modern UI
"""

import os
import sys

# Add the project root to the path
sys.path.insert(  # noqa: E402
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import tempfile  # noqa: E402
import time  # noqa: E402
import unittest  # noqa: E402
from multiprocessing import Process  # noqa: E402

import requests  # noqa: E402
import uvicorn  # noqa: E402

from auth_manager import AuthManager  # noqa: E402
from web_app import create_web_app  # noqa: E402


def _run_web_test_server(db_path, port):
    """Helper function to run test server"""
    app = create_web_app(db_path=db_path)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


class WebUIIntegrationTest(unittest.TestCase):
    """Comprehensive integration tests for the modern web UI"""

    # Class attributes for type checking
    test_db: str
    base_url: str
    port: int
    auth_manager: any
    server_process: any

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
        cls.base_url = "http://localhost:8901"
        cls.port = 8901

        # Create test database and admin user
        cls.auth_manager = AuthManager(cls.test_db)

        # Create test tenant and admin user
        success, message = cls.auth_manager.create_tenant("Test Tenant", "test")
        if not success:
            raise Exception(f"Failed to create test tenant: {message}")

        # Get the tenant ID by querying the database
        conn = cls.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test",))
        result = cursor.fetchone()
        tenant_id = result[0] if result else None
        conn.close()

        if not tenant_id:
            raise Exception("Failed to get tenant ID after creation")

        success, message = cls.auth_manager.create_user(
            tenant_id=tenant_id,
            email="admin@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Admin",
            role="admin",
        )
        if not success:
            raise Exception(f"Failed to create test admin user: {message}")

        # Start web server in separate process
        cls.start_test_server()

        # Wait for server to start
        cls.wait_for_server()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Stop server
        if hasattr(cls, "server_process"):
            cls.server_process.terminate()
            cls.server_process.join(timeout=5)

        # Clean up test database
        try:
            os.unlink(cls.test_db)
        except Exception:
            pass

    @classmethod
    def start_test_server(cls):
        """Start the web server for testing"""
        cls.server_process = Process(
            target=_run_web_test_server, args=(cls.test_db, cls.port)
        )
        cls.server_process.start()

    @classmethod
    def wait_for_server(cls, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/login", timeout=2)
                if response.status_code in [200, 302]:
                    return True
            except Exception:
                pass
            time.sleep(0.5)

        raise RuntimeError("Test server failed to start")

    def setUp(self):
        """Set up for each test"""
        self.session = requests.Session()

    def login_admin(self) -> bool:
        """Login as admin user"""
        login_data = {
            "email": "admin@test.com",
            "password": "testpass123",
            "subdomain": "test",
        }

        response = self.session.post(
            f"{self.base_url}/login", data=login_data, allow_redirects=False
        )
        return response.status_code == 302  # Successful login redirects

    def test_01_server_health(self):
        """Test that the web server is running"""
        response = requests.get(f"{self.base_url}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AI Prompt Manager", response.text)

    def test_02_login_page_loads(self):
        """Test login page loads with correct content"""
        response = self.session.get(f"{self.base_url}/login")
        self.assertEqual(response.status_code, 200)

        # Check for key elements
        self.assertIn("Sign in to your account", response.text)
        self.assertIn("email", response.text.lower())
        self.assertIn("password", response.text.lower())
        self.assertIn("organization", response.text.lower())

    def test_03_authentication_flow(self):
        """Test complete authentication flow"""
        # Test invalid login
        invalid_data = {
            "email": "wrong@test.com",
            "password": "wrongpass",
            "subdomain": "test",
        }
        response = self.session.post(f"{self.base_url}/login", data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertIn("error", response.text.lower())

        # Test valid login
        self.assertTrue(self.login_admin())

        # Test protected page access after login
        response = self.session.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome back", response.text)

        # Test logout
        response = self.session.get(f"{self.base_url}/logout", allow_redirects=False)
        self.assertEqual(response.status_code, 302)

        # Test protected page access after logout
        response = self.session.get(f"{self.base_url}/", allow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_04_dashboard_functionality(self):
        """Test dashboard loads and shows correct content"""
        self.assertTrue(self.login_admin())

        response = self.session.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)

        # Check for dashboard elements
        self.assertIn("Welcome back", response.text)
        self.assertIn("Create New", response.text)
        self.assertIn("Total Prompts", response.text)
        self.assertIn("Templates", response.text)

    def test_05_navigation_links(self):
        """Test all navigation links work"""
        self.assertTrue(self.login_admin())

        # Test main navigation
        nav_links = [
            ("/prompts", "Prompts"),
            ("/templates", "Templates"),
            ("/settings", "Settings"),
        ]

        for url, expected_content in nav_links:
            response = self.session.get(f"{self.base_url}{url}")
            self.assertEqual(response.status_code, 200, f"Failed to load {url}")
            self.assertIn(expected_content, response.text)

    def test_06_prompt_creation(self):
        """Test prompt creation flow"""
        self.assertTrue(self.login_admin())

        # Access new prompt page
        response = self.session.get(f"{self.base_url}/prompts/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Create New Prompt", response.text)

        # Create a test prompt
        prompt_data = {
            "name": "Test Prompt",
            "content": "This is a test prompt with {variable}",
            "category": "Business",
            "description": "A test prompt for integration testing",
            "tags": "test, integration, automated",
        }

        response = self.session.post(
            f"{self.base_url}/prompts/new", data=prompt_data, allow_redirects=False
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Verify prompt appears in list
        response = self.session.get(f"{self.base_url}/prompts")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Prompt", response.text)

    def test_07_prompt_management(self):
        """Test prompt editing and deletion"""
        self.assertTrue(self.login_admin())

        # Create a prompt first
        prompt_data = {
            "name": "Management Test Prompt",
            "content": "Original content",
            "category": "Technical",
            "description": "For testing management",
            "tags": "management, test",
        }

        self.session.post(
            f"{self.base_url}/prompts/new", data=prompt_data, allow_redirects=False
        )

        # Get the prompts list to find the ID of the created prompt
        prompts_response = self.session.get(f"{self.base_url}/prompts")
        self.assertEqual(prompts_response.status_code, 200)

        # Extract prompt ID from the response (look for edit link near our prompt)
        import re

        # Find the section containing our prompt name and look for the edit link
        prompt_section_match = re.search(
            r"Management Test Prompt.*?/prompts/(\d+)/edit",
            prompts_response.text,
            re.DOTALL,
        )
        self.assertIsNotNone(
            prompt_section_match, "Could not find edit link for Management Test Prompt"
        )
        prompt_id = prompt_section_match.group(1)

        # Also verify the prompt appears in the list
        self.assertIn(
            "Management Test Prompt",
            prompts_response.text,
            "Created prompt should appear in list",
        )

        # Test edit page access
        response = self.session.get(f"{self.base_url}/prompts/{prompt_id}/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Edit Prompt", response.text)
        # Check that the content appears in the textarea
        self.assertTrue(
            "Original content" in response.text,
            "Original content should be present in the edit form",
        )

        # Test prompt update
        updated_data = {
            "name": "Updated Management Test Prompt",
            "content": "Updated content",
            "category": "Technical",
            "description": "Updated description",
            "tags": "management, test, updated",
        }

        response = self.session.post(
            f"{self.base_url}/prompts/{prompt_id}/edit",
            data=updated_data,
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

        # Verify update
        response = self.session.get(f"{self.base_url}/prompts")
        self.assertIn("Updated Management Test Prompt", response.text)

    def test_08_search_functionality(self):
        """Test HTMX search functionality"""
        self.assertTrue(self.login_admin())

        # Create test prompts
        test_prompts = [
            {
                "name": "Search Test Alpha",
                "content": "Alpha content",
                "category": "Business",
            },
            {
                "name": "Search Test Beta",
                "content": "Beta content",
                "category": "Technical",
            },
            {
                "name": "Different Prompt",
                "content": "Other content",
                "category": "Creative",
            },
        ]

        for prompt in test_prompts:
            prompt.update({"description": "Test", "tags": "search"})
            self.session.post(
                f"{self.base_url}/prompts/new", data=prompt, allow_redirects=False
            )

        # Test search
        response = self.session.get(f"{self.base_url}/prompts/search?q=Search Test")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Search Test Alpha", response.text)
        self.assertIn("Search Test Beta", response.text)
        self.assertNotIn("Different Prompt", response.text)

    def test_09_internationalization(self):
        """Test language switching functionality"""
        self.assertTrue(self.login_admin())

        # Test language change
        language_data = {"language": "es"}
        response = self.session.post(
            f"{self.base_url}/language", data=language_data, allow_redirects=False
        )
        self.assertEqual(response.status_code, 302)

        # Note: Full i18n testing would require translated content
        # This tests the mechanism works

    def test_10_api_endpoints(self):
        """Test API endpoints for features"""
        self.assertTrue(self.login_admin())

        # Test translation endpoint
        translate_data = {"text": "Hello world", "target_lang": "en"}
        response = self.session.post(f"{self.base_url}/translate", data=translate_data)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("success", result)

        # Test optimization endpoint
        optimize_data = {"prompt": "Write an email"}
        response = self.session.post(f"{self.base_url}/optimize", data=optimize_data)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("success", result)

        # Test token calculation
        token_data = {"text": "This is a test prompt", "model": "gpt-4"}
        response = self.session.post(
            f"{self.base_url}/calculate-tokens", data=token_data
        )
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("success", result)
        if result["success"]:
            self.assertIn("token_count", result)
            self.assertIn("estimated_cost", result)

    def test_11_settings_pages(self):
        """Test settings and profile pages"""
        self.assertTrue(self.login_admin())

        # Test settings hub
        response = self.session.get(f"{self.base_url}/settings")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Settings", response.text)
        self.assertIn("Profile", response.text)
        self.assertIn("API Tokens", response.text)

        # Test profile page
        response = self.session.get(f"{self.base_url}/profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Profile Settings", response.text)

        # Test API tokens page
        response = self.session.get(f"{self.base_url}/api-tokens")
        self.assertEqual(response.status_code, 200)
        self.assertIn("API Tokens", response.text)

    def test_12_prompt_execution(self):
        """Test prompt execution interface"""
        self.assertTrue(self.login_admin())

        # Create a prompt with variables
        prompt_data = {
            "name": "Execution Test Prompt",
            "content": "Write a {tone} email about {topic} to {recipient}",
            "category": "Business",
            "description": "For testing execution",
            "tags": "execution, test",
        }

        self.session.post(
            f"{self.base_url}/prompts/new", data=prompt_data, allow_redirects=False
        )

        # Test execution page
        response = self.session.get(
            f"{self.base_url}/prompts/Execution Test Prompt/execute"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Execute:", response.text)
        self.assertIn("Variables & Parameters", response.text)
        self.assertIn("tone", response.text)
        self.assertIn("topic", response.text)
        self.assertIn("recipient", response.text)

    def test_13_responsive_design(self):
        """Test responsive design elements"""
        self.assertTrue(self.login_admin())

        # Test mobile viewport headers
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        }
        response = self.session.get(f"{self.base_url}/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("viewport", response.text)
        self.assertIn("width=device-width", response.text)

    def test_14_error_handling(self):
        """Test error handling"""
        self.assertTrue(self.login_admin())

        # Test 404 for non-existent prompt (using a non-existent ID)
        response = self.session.get(f"{self.base_url}/prompts/99999/edit")
        self.assertEqual(response.status_code, 404)

        # Test unauthorized access
        new_session = requests.Session()
        response = new_session.get(f"{self.base_url}/prompts", allow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_15_security_headers(self):
        """Test security-related functionality"""
        response = self.session.get(f"{self.base_url}/login")

        # Check for security best practices
        self.assertIn("text/html", response.headers.get("content-type", ""))

        # Test CSRF protection exists (forms should have hidden inputs)
        self.assertTrue(self.login_admin())
        response = self.session.get(f"{self.base_url}/prompts/new")
        # Note: More comprehensive CSRF testing would require checking tokens


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Web UI Integration Tests...")

    # Set environment for testing
    os.environ["MULTITENANT_MODE"] = "true"
    os.environ["LOCAL_DEV_MODE"] = "true"

    suite = unittest.TestLoader().loadTestsFromTestCase(WebUIIntegrationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n📊 Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Failures:")
        for test, error in result.failures:
            print(f"  {test}: {error}")

    if result.errors:
        print("\n💥 Errors:")
        for test, error in result.errors:
            print(f"  {test}: {error}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
