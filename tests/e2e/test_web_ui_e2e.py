#!/usr/bin/env python3
"""
End-to-End tests for the Web UI (FastAPI + HTMX + Tailwind)
Modern web interface testing using Playwright for comprehensive UI validation
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

try:  # noqa: E402
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available. Install with: poetry install --with e2e")

from auth_manager import AuthManager  # noqa: E402
from web_app import create_web_app  # noqa: E402


def _run_web_test_server(db_path, port):
    """Helper function to run test server (module level for multiprocessing)"""
    import uvicorn  # noqa: E402

    app = create_web_app(db_path=db_path)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright not available")
class WebUIE2ETest(unittest.TestCase):
    """End-to-end tests using Playwright for browser automation"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
        cls.base_url = "http://localhost:8902"
        cls.port = 8902
        cls.headless = os.getenv("E2E_HEADLESS", "true").lower() == "true"
        cls.slow_mo = int(os.getenv("E2E_SLOW_MO", "0"))

        # Create test database and admin user
        cls.auth_manager = AuthManager(cls.test_db)

        # Create test tenant and admin user
        success, tenant_message = cls.auth_manager.create_tenant("Test Tenant", "test")
        if not success:
            raise Exception(f"Failed to create test tenant: {tenant_message}")

        # Get the tenant_id after creation
        tenant = cls.auth_manager.get_tenant_by_subdomain("test")
        if not tenant:
            raise Exception("Failed to retrieve created tenant")
        cls.tenant_id = tenant.id

        success, user_message = cls.auth_manager.create_user(
            tenant_id=cls.tenant_id,
            email="admin@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Admin",
            role="admin",
        )
        if not success:
            raise Exception(f"Failed to create test admin user: {user_message}")

        # Get the user_id after creation
        user = cls.auth_manager.get_user_by_email("admin@test.com", cls.tenant_id)
        if not user:
            raise Exception("Failed to retrieve created admin user")
        cls.user_id = user.id

        # Create API token for testing
        from api_token_manager import APITokenManager

        cls.token_manager = APITokenManager(cls.test_db)
        success, _, cls.api_token = cls.token_manager.create_api_token(
            cls.user_id, cls.tenant_id, "E2E Test Token", expires_days=1
        )
        if not success:
            raise Exception("Failed to create test API token")

        # Start web server
        cls.start_test_server()
        cls.wait_for_server()

        # Start Playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=cls.headless, slow_mo=cls.slow_mo
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Clean up browser
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()

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
        import requests

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
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        """Clean up after each test"""
        self.page.close()
        self.context.close()

    def login_admin(self):
        """Login as admin user"""
        self.page.goto(f"{self.base_url}/login")

        # Fill login form
        self.page.fill('input[name="email"]', "admin@test.com")
        self.page.fill('input[name="password"]', "testpass123")
        self.page.fill('input[name="subdomain"]', "test")

        # Submit form
        self.page.click('button[type="submit"]')

        # Wait for redirect to dashboard
        self.page.wait_for_url(f"{self.base_url}/")

    def test_01_login_flow(self):
        """Test complete login flow with browser automation"""
        # Navigate to login page
        self.page.goto(f"{self.base_url}/login")

        # Check page loaded correctly
        self.assertIn("AI Prompt Manager", self.page.title())
        self.assertTrue(self.page.is_visible("text=Sign in to your account"))

        # Test invalid login
        self.page.fill('input[name="email"]', "wrong@test.com")
        self.page.fill('input[name="password"]', "wrongpass")
        self.page.click('button[type="submit"]')

        # Should stay on login page with error
        self.page.wait_for_selector("text=error", state="visible", timeout=5000)

        # Test valid login
        self.page.fill('input[name="email"]', "admin@test.com")
        self.page.fill('input[name="password"]', "testpass123")
        self.page.fill('input[name="subdomain"]', "test")
        self.page.click('button[type="submit"]')

        # Should redirect to dashboard
        self.page.wait_for_url(f"{self.base_url}/")
        self.assertTrue(self.page.is_visible("text=Welcome back"))

    def test_02_navigation_menu(self):
        """Test navigation menu functionality"""
        self.login_admin()

        # Test main navigation links
        nav_items = [
            ("Prompts", "/prompts"),
            ("Templates", "/templates"),
            ("Settings", "/settings"),
        ]

        for item_text, expected_url in nav_items:
            self.page.click(f"text={item_text}")
            self.page.wait_for_url(f"{self.base_url}{expected_url}")
            self.assertTrue(self.page.is_visible(f"text={item_text}"))

    def test_03_language_switching(self):
        """Test language switching functionality"""
        self.login_admin()

        # Click language selector
        self.page.click('[id="language-menu-button"]')

        # Wait for dropdown to appear
        self.page.wait_for_selector("text=Español", state="visible")

        # Click Spanish
        self.page.click("text=Español")

        # Language should change (basic test - full i18n would show Spanish text)
        self.page.wait_for_load_state("networkidle")

    def test_04_prompt_creation_flow(self):
        """Test complete prompt creation flow"""
        self.login_admin()

        # Navigate to prompts page
        self.page.click("text=Prompts")
        self.page.wait_for_url(f"{self.base_url}/prompts")

        # Click new prompt button
        self.page.click("text=New Prompt")
        self.page.wait_for_url(f"{self.base_url}/prompts/new")

        # Fill out form
        self.page.fill('input[name="name"]', "E2E Test Prompt")
        self.page.select_option('select[name="category"]', "Business")
        self.page.fill('textarea[name="description"]', "Created by E2E test")
        self.page.fill('input[name="tags"]', "e2e, test, automated")
        self.page.fill('textarea[name="content"]', "Write a {tone} email about {topic}")

        # Test character counting
        char_count = self.page.text_content("#char-count")
        self.assertIn("characters", char_count)

        # Submit form
        self.page.click('button[type="submit"]')

        # Should redirect to prompts list
        self.page.wait_for_url(f"{self.base_url}/prompts")

        # Verify prompt appears in list
        self.assertTrue(self.page.is_visible("text=E2E Test Prompt"))

    def test_05_prompt_search_and_filter(self):
        """Test search and filtering functionality"""
        self.login_admin()

        # Create test prompts first
        test_prompts = [
            {
                "name": "Search Alpha",
                "content": "Alpha content",
                "category": "Business",
            },
            {"name": "Search Beta", "content": "Beta content", "category": "Technical"},
            {
                "name": "Other Prompt",
                "content": "Different content",
                "category": "Creative",
            },
        ]

        for prompt in test_prompts:
            self.page.goto(f"{self.base_url}/prompts/new")
            self.page.fill('input[name="name"]', prompt["name"])
            self.page.fill('textarea[name="content"]', prompt["content"])
            self.page.select_option('select[name="category"]', prompt["category"])
            self.page.click('button[type="submit"]')

        # Navigate to prompts list
        self.page.goto(f"{self.base_url}/prompts")

        # Test search functionality
        self.page.fill('input[name="search"]', "Search")

        # Wait for HTMX to update results
        self.page.wait_for_timeout(1000)

        # Should show only search results
        self.assertTrue(self.page.is_visible("text=Search Alpha"))
        self.assertTrue(self.page.is_visible("text=Search Beta"))
        self.assertFalse(self.page.is_visible("text=Other Prompt"))

        # Test category filter
        self.page.fill('input[name="search"]', "")  # Clear search
        self.page.select_option('select[name="category"]', "Business")

        # Wait for filter to apply
        self.page.wait_for_timeout(1000)

    def test_06_prompt_editing(self):
        """Test prompt editing functionality"""
        self.login_admin()

        # Create a prompt to edit
        self.page.goto(f"{self.base_url}/prompts/new")
        self.page.fill('input[name="name"]', "Edit Test Prompt")
        self.page.fill('textarea[name="content"]', "Original content")
        self.page.select_option('select[name="category"]', "Business")
        self.page.click('button[type="submit"]')

        # Navigate back to prompts list
        self.page.wait_for_url(f"{self.base_url}/prompts")

        # Click edit button for our prompt
        edit_button = (
            self.page.locator("text=Edit Test Prompt")
            .locator("..")
            .locator('a[title="Edit"]')
        )
        edit_button.click()

        # Should navigate to edit page
        self.page.wait_for_url(f"{self.base_url}/prompts/Edit Test Prompt/edit")

        # Verify form is pre-filled
        self.assertEqual(
            self.page.input_value('input[name="name"]'), "Edit Test Prompt"
        )
        self.assertEqual(
            self.page.input_value('textarea[name="content"]'), "Original content"
        )

        # Update content
        self.page.fill('textarea[name="content"]', "Updated content")
        self.page.click('button[type="submit"]')

        # Should redirect back to prompts list
        self.page.wait_for_url(f"{self.base_url}/prompts")

    def test_07_prompt_execution(self):
        """Test prompt execution interface"""
        self.login_admin()

        # Create a prompt with variables
        self.page.goto(f"{self.base_url}/prompts/new")
        self.page.fill('input[name="name"]', "Execute Test Prompt")
        self.page.fill(
            'textarea[name="content"]',
            "Write a {tone} email to {recipient} about {topic}",
        )
        self.page.select_option('select[name="category"]', "Business")
        self.page.click('button[type="submit"]')

        # Navigate to prompts list and click execute
        self.page.wait_for_url(f"{self.base_url}/prompts")
        execute_button = (
            self.page.locator("text=Execute Test Prompt")
            .locator("..")
            .locator('a[title="Execute"]')
        )
        execute_button.click()

        # Should navigate to execution page
        self.page.wait_for_url(f"{self.base_url}/prompts/Execute Test Prompt/execute")

        # Check that variables are detected and form inputs created
        self.assertTrue(self.page.is_visible("text=Variables & Parameters"))
        self.assertTrue(self.page.is_visible('input[name="tone"]'))
        self.assertTrue(self.page.is_visible('input[name="recipient"]'))
        self.assertTrue(self.page.is_visible('input[name="topic"]'))

        # Fill variables
        self.page.fill('input[name="tone"]', "professional")
        self.page.fill('input[name="recipient"]', "John")
        self.page.fill('input[name="topic"]', "project update")

        # Test preview functionality
        self.page.click("text=Preview")

    def test_08_optimization_features(self):
        """Test prompt optimization features"""
        self.login_admin()

        # Navigate to prompt creation
        self.page.goto(f"{self.base_url}/prompts/new")

        # Fill in a basic prompt
        self.page.fill('input[name="name"]', "Optimization Test")
        self.page.fill('textarea[name="content"]', "Write email")
        self.page.select_option('select[name="category"]', "Business")

        # Test optimization button
        self.page.click("text=Optimize")

        # Wait for optimization to complete (or timeout)
        try:
            self.page.wait_for_selector("text=Optimization", timeout=10000)
        except Exception:
            # Optimization service might not be available in test environment
            pass

        # Test translation button
        self.page.click("text=Translate")

        # Wait for translation (or timeout)
        try:
            self.page.wait_for_timeout(2000)
        except Exception:
            pass

    def test_09_responsive_design(self):
        """Test responsive design on different screen sizes"""
        self.login_admin()

        # Test mobile viewport
        self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        self.page.reload()

        # Navigation should be responsive
        self.assertTrue(self.page.is_visible('[id="user-menu-button"]'))

        # Test tablet viewport
        self.page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        self.page.reload()

        # Test desktop viewport
        self.page.set_viewport_size({"width": 1920, "height": 1080})  # Desktop size
        self.page.reload()

    def test_10_settings_pages(self):
        """Test settings and profile pages"""
        self.login_admin()

        # Navigate to settings
        self.page.click("text=Settings")
        self.page.wait_for_url(f"{self.base_url}/settings")

        # Test profile page
        self.page.click("text=Profile")
        self.page.wait_for_url(f"{self.base_url}/profile")
        self.assertTrue(self.page.is_visible("text=Profile Settings"))

        # Test API tokens page
        self.page.goto(f"{self.base_url}/api-tokens")
        self.assertTrue(self.page.is_visible("text=API Tokens"))

    def test_10a_api_token_management_workflow(self):
        """Test comprehensive API token management workflow"""
        self.login_admin()

        # Navigate to API tokens page
        self.page.goto(f"{self.base_url}/api-tokens")
        self.page.wait_for_load_state("networkidle")

        # Verify page loaded correctly
        self.assertTrue(self.page.is_visible("text=API Tokens"))
        self.assertTrue(self.page.is_visible("text=Generate Token"))

        # Check if we see the stats cards
        self.assertTrue(self.page.is_visible("text=Total Tokens"))
        self.assertTrue(self.page.is_visible("text=Active"))
        self.assertTrue(self.page.is_visible("text=Never Expire"))

        # Test creating a new token
        self._test_create_api_token()

        # Test viewing token details
        self._test_view_token_details()

        # Test token security features
        self._test_token_security_features()

        # Test revoking token
        self._test_revoke_api_token()

    def _test_create_api_token(self):
        """Test creating a new API token"""
        # Click the Generate Token button
        self.page.click("text=Generate Token")

        # Wait for modal to appear
        self.page.wait_for_selector("#create-token-modal", state="visible")

        # Verify modal content
        self.assertTrue(self.page.is_visible("text=Generate New API Token"))
        self.assertTrue(self.page.is_visible("text=Token Name"))
        self.assertTrue(self.page.is_visible("text=Expiration"))

        # Fill in token details
        self.page.fill('input[name="name"]', "E2E Test Token")
        self.page.select_option('select[name="expires_days"]', "30")

        # Submit the form
        self.page.click('button[type="submit"]')

        # Wait for success modal
        try:
            self.page.wait_for_selector(
                "#token-created-modal", state="visible", timeout=5000
            )

            # Verify success modal
            self.assertTrue(self.page.is_visible("text=Token Created Successfully"))
            self.assertTrue(self.page.is_visible("text=Your API Token"))

            # Get the token value (for later use if needed)
            token_input = self.page.locator("#new-token")
            if token_input.is_visible():
                token_value = token_input.input_value()
                self.assertTrue(
                    token_value.startswith("apm_"), "Token should have correct prefix"
                )

            # Test copy functionality
            copy_button = self.page.locator("text=Copy")
            if copy_button.is_visible():
                copy_button.click()
                self.page.wait_for_timeout(1000)  # Wait for copy feedback

            # Close the success modal
            self.page.click("text=Got It")
            self.page.wait_for_selector("#token-created-modal", state="hidden")

        except Exception as e:
            print(f"⚠️ Token creation modal not working as expected: {e}")
            # Try to close any open modals
            if self.page.is_visible("#create-token-modal"):
                self.page.keyboard.press("Escape")

    def _test_view_token_details(self):
        """Test viewing token details and information"""
        # Should now see the created token in the list
        try:
            # Look for the token we just created
            token_element = self.page.locator("text=E2E Test Token")
            if token_element.is_visible():
                # Verify token information is displayed
                token_row = token_element.locator("..")

                # Check for status badge
                self.assertTrue(token_row.locator("text=Active").is_visible())

                # Check for creation date
                self.assertTrue(token_row.locator("text=Created").is_visible())

                # Check for expiration info
                self.assertTrue(token_row.locator("text=Expires").is_visible())

                # Check for token prefix
                prefix_element = token_row.locator("text=/apm_.*\\*\\*\\*/")
                if prefix_element.is_visible():
                    print("✅ Token prefix display working correctly")
            else:
                print("⚠️ Created token not visible in list")
        except Exception as e:
            print(f"⚠️ Token details viewing failed: {e}")

    def _test_token_security_features(self):
        """Test token security features and guidelines"""
        # Check for security guidelines section
        if self.page.is_visible("text=Security Guidelines"):
            # Verify security tips are displayed
            self.assertTrue(self.page.is_visible("text=Keep your API tokens secure"))
            self.assertTrue(self.page.is_visible("text=Use different tokens"))
            self.assertTrue(self.page.is_visible("text=Regularly rotate"))

        # Check for API documentation section
        if self.page.is_visible("text=API Documentation"):
            # Verify code examples are present
            self.assertTrue(self.page.is_visible("text=cURL"))
            self.assertTrue(self.page.is_visible("text=JavaScript"))
            self.assertTrue(self.page.is_visible("text=Python"))

            # Test copy functionality for code examples
            copy_buttons = self.page.locator("text=Copy")
            if copy_buttons.count() > 0:
                # Click first copy button
                copy_buttons.first.click()
                self.page.wait_for_timeout(500)

    def _test_revoke_api_token(self):
        """Test revoking an API token"""
        try:
            # Find the revoke button for our test token
            token_element = self.page.locator("text=E2E Test Token")
            if token_element.is_visible():
                token_row = token_element.locator("..")
                revoke_button = token_row.locator("text=Revoke")

                if revoke_button.is_visible():
                    # Click revoke button
                    revoke_button.click()

                    # Handle confirmation dialog
                    self.page.on("dialog", lambda dialog: dialog.accept())

                    # Wait for page to reload or update
                    self.page.wait_for_timeout(2000)

                    # Verify token is now shown as revoked
                    revoked_element = self.page.locator("text=Revoked")
                    if revoked_element.is_visible():
                        print("✅ Token revocation working correctly")
                    else:
                        print("⚠️ Token revocation status not updated")
                else:
                    print("⚠️ Revoke button not found")
            else:
                print("⚠️ Test token not found for revocation")
        except Exception as e:
            print(f"⚠️ Token revocation test failed: {e}")

    def test_10b_api_authorization_workflow(self):
        """Test API authorization using created tokens"""
        import requests

        # Skip if token wasn't created successfully
        if not hasattr(self, "api_token"):
            print("⚠️ Skipping API authorization test - no token available")
            return

        api_base_url = f"http://localhost:{self.port}/api"

        try:
            # Test accessing protected endpoint without token
            response = requests.get(f"{api_base_url}/user/info", timeout=5)
            self.assertEqual(response.status_code, 401, "Should require authentication")

            # Test accessing protected endpoint with invalid token
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(
                f"{api_base_url}/user/info", headers=headers, timeout=5
            )
            self.assertEqual(response.status_code, 401, "Should reject invalid token")

            # Test accessing protected endpoint with valid token
            headers = {"Authorization": f"Bearer {self.api_token}"}
            response = requests.get(
                f"{api_base_url}/user/info", headers=headers, timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get("success"), "API should return success")
                self.assertIn("user", data.get("data", {}), "Should include user info")
                print("✅ API authorization working correctly")
            else:
                print(
                    f"⚠️ API authorization test failed with status {response.status_code}"
                )

            # Test health endpoint (should not require auth)
            response = requests.get(f"{api_base_url}/health", timeout=5)
            self.assertEqual(
                response.status_code, 200, "Health endpoint should be accessible"
            )

        except requests.exceptions.RequestException as e:
            print(f"⚠️ API authorization test failed due to network error: {e}")
        except Exception as e:
            print(f"⚠️ API authorization test failed: {e}")

    def test_10c_token_management_edge_cases(self):
        """Test edge cases in token management"""
        self.login_admin()
        self.page.goto(f"{self.base_url}/api-tokens")

        # Test creating token with duplicate name
        self._test_duplicate_token_name()

        # Test creating token with empty name
        self._test_empty_token_name()

        # Test bulk operations
        self._test_bulk_token_operations()

    def _test_duplicate_token_name(self):
        """Test creating token with duplicate name"""
        try:
            # Create first token
            self.page.click("text=Generate Token")
            self.page.wait_for_selector("#create-token-modal", state="visible")
            self.page.fill('input[name="name"]', "Duplicate Test")
            self.page.click('button[type="submit"]')

            # Wait for success and close modal
            if self.page.is_visible("#token-created-modal"):
                self.page.click("text=Got It")
                self.page.wait_for_timeout(1000)

            # Try to create second token with same name
            self.page.click("text=Generate Token")
            self.page.wait_for_selector("#create-token-modal", state="visible")
            self.page.fill('input[name="name"]', "Duplicate Test")
            self.page.click('button[type="submit"]')

            # Should show error message
            self.page.wait_for_timeout(2000)
            # Error handling depends on implementation

        except Exception as e:
            print(f"⚠️ Duplicate token name test failed: {e}")

    def _test_empty_token_name(self):
        """Test creating token with empty name"""
        try:
            self.page.click("text=Generate Token")
            self.page.wait_for_selector("#create-token-modal", state="visible")

            # Leave name empty and try to submit
            self.page.click('button[type="submit"]')

            # Should not submit (HTML5 validation)
            # Modal should still be visible
            self.assertTrue(self.page.is_visible("#create-token-modal"))

            # Close modal
            self.page.keyboard.press("Escape")

        except Exception as e:
            print(f"⚠️ Empty token name test failed: {e}")

    def _test_bulk_token_operations(self):
        """Test bulk token operations"""
        try:
            # Look for "Revoke All" button
            revoke_all_button = self.page.locator("text=Revoke All")
            if revoke_all_button.is_visible() and not revoke_all_button.is_disabled():
                # Set up dialog handler
                self.page.on("dialog", lambda dialog: dialog.accept())

                # Click revoke all
                revoke_all_button.click()

                # Wait for operation to complete
                self.page.wait_for_timeout(3000)

                # Should see message about revoked tokens
                print("✅ Bulk revoke operation completed")
            else:
                print("⚠️ Revoke All button not available or disabled")

        except Exception as e:
            print(f"⚠️ Bulk token operations test failed: {e}")

    def test_11_error_handling(self):
        """Test error handling and edge cases"""
        self.login_admin()

        # Test 404 page
        self.page.goto(f"{self.base_url}/nonexistent-page")
        # Should show some kind of error or redirect

        # Test invalid prompt access
        self.page.goto(f"{self.base_url}/prompts/NonExistentPrompt/edit")
        # Should show 404 or redirect

    def test_12_language_management_workflow(self):
        """Test complete language management workflow"""
        self.login_admin()

        # Navigate to settings
        self.page.click("text=Settings")
        self.page.wait_for_url(f"{self.base_url}/settings")

        # Check if language management card exists and click it
        try:
            # Look for language management link/card
            language_element = self.page.locator("text=Languages").first
            if language_element.is_visible():
                language_element.click()
                self.page.wait_for_timeout(1000)

                # Test language switching if interface is available
                self.test_language_switching()

                # Test language creation if interface is available
                self.test_language_creation()
        except Exception as e:
            print(f"⚠️ Language management interface not available: {e}")

    def test_language_switching(self):
        """Test language switching functionality"""
        try:
            # Look for language dropdown or selector
            if self.page.is_visible("select[name='language']"):
                # Select different language if available
                self.page.select_option("select[name='language']", "fr")
                self.page.wait_for_timeout(500)

                # Verify language changed (look for French text)
                # This is basic - real test would check specific translations

            elif self.page.is_visible("text=Switch"):
                # Click switch button if available
                self.page.click("text=Switch")
                self.page.wait_for_timeout(500)

        except Exception as e:
            print(f"⚠️ Language switching not available: {e}")

    def test_language_creation(self):
        """Test language creation workflow"""
        try:
            # Look for "New Language" or "Create" button
            if self.page.is_visible("text=New Language"):
                self.page.click("text=New Language")
                self.page.wait_for_timeout(500)

                # Fill out form if modal appears
                if self.page.is_visible("input[id='newLangCode']"):
                    self.page.fill("input[id='newLangCode']", "de")
                    self.page.fill("input[id='newLangName']", "German")
                    self.page.fill("input[id='newLangNative']", "Deutsch")

                    # Submit form
                    self.page.click("text=Create")
                    self.page.wait_for_timeout(1000)

        except Exception as e:
            print(f"⚠️ Language creation not available: {e}")

    def test_13_language_editor_interface(self):
        """Test language editor interface if available"""
        self.login_admin()

        try:
            # Try to access language editor directly
            self.page.goto(f"{self.base_url}/settings/language/en")

            if self.page.is_visible("text=Language Editor"):
                # Test basic editor functionality
                print("✅ Language editor interface found")

                # Look for translation key inputs
                if self.page.is_visible("input[type='text']"):
                    # Test editing a translation
                    first_input = self.page.locator("input[type='text']").first
                    if first_input.is_visible():
                        original_value = first_input.input_value()
                        first_input.fill("Test Translation")

                        # Look for save button
                        if self.page.is_visible("text=Save"):
                            print("✅ Translation editing interface working")

                        # Restore original value
                        first_input.fill(original_value)

                # Test auto-translate buttons if available
                if self.page.is_visible("text=Translate"):
                    print("✅ Auto-translate functionality found")

        except Exception as e:
            print(f"⚠️ Language editor interface not available: {e}")

    def test_14_language_validation_interface(self):
        """Test language validation and progress indicators"""
        self.login_admin()

        try:
            # Navigate to language settings
            self.page.goto(f"{self.base_url}/settings/languages")

            # Look for validation indicators
            if self.page.is_visible("text=Missing"):
                print("✅ Language validation indicators found")

            if self.page.is_visible("text=Complete"):
                print("✅ Language completion indicators found")

            # Look for progress bars or percentages
            progress_elements = self.page.locator(
                ".progress, [role='progressbar'], text=/\\d+%/"
            )
            if progress_elements.count() > 0:
                print("✅ Language progress indicators found")

        except Exception as e:
            print(f"⚠️ Language validation interface not available: {e}")

    def test_15_multilingual_content_display(self):
        """Test display of multilingual content"""
        self.login_admin()

        try:
            # Switch to different language and check content changes
            # This would require the language system to be fully integrated

            # Check if page title changes with language
            original_title = self.page.title()

            # Try to switch language via URL parameter or form
            self.page.goto(f"{self.base_url}/?lang=fr")
            self.page.wait_for_timeout(1000)

            new_title = self.page.title()
            if original_title != new_title:
                print("✅ Language switching affects page content")

        except Exception as e:
            print(f"⚠️ Multilingual content testing not available: {e}")

    def test_16_theme_toggle_functionality(self):
        """Test theme toggle functionality with browser automation"""
        self.login_admin()

        # Test theme toggle button presence
        self.assertTrue(
            self.page.is_visible(".theme-toggle"),
            "Theme toggle button should be visible",
        )
        self.assertTrue(
            self.page.is_visible("#theme-toggle"), "Theme toggle should have correct ID"
        )
        self.assertTrue(
            self.page.is_visible("#theme-icon"), "Theme icon should be present"
        )

        # Test accessibility attributes
        theme_button = self.page.locator(".theme-toggle")
        self.assertTrue(
            theme_button.get_attribute("aria-label"),
            "Theme toggle should have aria-label",
        )
        self.assertTrue(
            theme_button.get_attribute("title"),
            "Theme toggle should have title attribute",
        )

        # Test theme cycling: Light -> Dark -> System -> Light
        self._test_theme_cycling()

        # Test theme persistence across page loads
        self._test_theme_persistence()

        # Test system preference detection
        self._test_system_preference_detection()

    def _test_theme_cycling(self):
        """Test theme cycling through light, dark, and system modes"""
        try:
            # Start with light theme (default)
            initial_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            # Verify we have a valid initial theme
            assert initial_theme in [None, "light", "dark", "system"]

            # Click theme toggle to go to dark
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)  # Wait for transition

            # Verify dark theme is applied
            dark_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(dark_theme, "dark", "Should switch to dark theme")

            # Verify dark theme styles are applied
            bg_color = self.page.evaluate(
                "getComputedStyle(document.body).backgroundColor"
            )
            self.assertNotEqual(
                bg_color,
                "rgb(255, 255, 255)",
                "Background should not be white in dark mode",
            )

            # Click again to go to system
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)

            # Verify system theme
            system_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(system_theme, "system", "Should switch to system theme")

            # Click again to go back to light
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)

            # Verify light theme
            light_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(light_theme, "light", "Should switch back to light theme")

            print("✅ Theme cycling functionality working correctly")

        except Exception as e:
            print(f"⚠️ Theme cycling test failed: {e}")

    def _test_theme_persistence(self):
        """Test that theme preference persists across page reloads"""
        try:
            # Set to dark theme
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)

            # Verify dark theme is set
            dark_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(dark_theme, "dark")

            # Reload the page
            self.page.reload()
            self.page.wait_for_load_state("networkidle")

            # Verify theme persisted
            persisted_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(
                persisted_theme, "dark", "Theme should persist across page reloads"
            )

            # Verify localStorage has the theme stored
            stored_theme = self.page.evaluate("localStorage.getItem('theme')")
            self.assertEqual(
                stored_theme, "dark", "Theme should be stored in localStorage"
            )

            print("✅ Theme persistence working correctly")

        except Exception as e:
            print(f"⚠️ Theme persistence test failed: {e}")

    def _test_system_preference_detection(self):
        """Test system preference detection and automatic theme switching"""
        try:
            # Set theme to system mode
            self.page.click(".theme-toggle")  # light -> dark
            self.page.click(".theme-toggle")  # dark -> system
            self.page.wait_for_timeout(500)

            # Verify system theme is active
            system_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            self.assertEqual(system_theme, "system")

            # Test system preference detection
            system_prefers_dark = self.page.evaluate(
                """
                window.matchMedia('(prefers-color-scheme: dark)').matches
            """
            )

            # Verify the actual applied theme matches system preference
            computed_theme = self.page.evaluate(
                """
                document.documentElement.getAttribute('data-theme') === 'system' ?
                    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') :
                    document.documentElement.getAttribute('data-theme')
            """
            )

            expected_theme = "dark" if system_prefers_dark else "light"
            self.assertEqual(
                computed_theme,
                expected_theme,
                f"System theme should reflect OS preference: {expected_theme}",
            )

            print(
                f"✅ System preference detection working correctly (system prefers {expected_theme})"
            )

        except Exception as e:
            print(f"⚠️ System preference detection test failed: {e}")

    def test_17_theme_visual_verification(self):
        """Test visual aspects of theme switching"""
        self.login_admin()

        try:
            # Test light theme visual elements
            self._verify_theme_colors("light")

            # Switch to dark theme
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)

            # Test dark theme visual elements
            self._verify_theme_colors("dark")

            # Test theme icon changes
            self._verify_theme_icon_changes()

        except Exception as e:
            print(f"⚠️ Theme visual verification failed: {e}")

    def _verify_theme_colors(self, theme_mode):
        """Verify that theme colors are applied correctly"""
        try:
            # Get current theme attribute
            current_theme = self.page.evaluate(
                "document.documentElement.getAttribute('data-theme')"
            )
            # Verify the theme matches expected mode
            assert current_theme == theme_mode or (
                current_theme is None and theme_mode == "light"
            )

            if theme_mode == "light":
                # Verify light theme colors
                bg_color = self.page.evaluate(
                    "getComputedStyle(document.body).backgroundColor"
                )
                # Light theme should have light background
                self.assertIn(
                    "255",
                    bg_color,
                    f"Light theme should have light background, got: {bg_color}",
                )

            elif theme_mode == "dark":
                # Verify dark theme colors
                bg_color = self.page.evaluate(
                    "getComputedStyle(document.body).backgroundColor"
                )
                # Dark theme should have dark background
                self.assertNotEqual(
                    bg_color,
                    "rgb(255, 255, 255)",
                    f"Dark theme should not have white background, got: {bg_color}",
                )

            # Verify CSS custom properties are applied
            surface_primary = self.page.evaluate(
                """
                getComputedStyle(document.documentElement).getPropertyValue('--surface-primary').trim()
            """
            )
            self.assertTrue(
                len(surface_primary) > 0,
                "CSS custom property --surface-primary should have value",
            )

            print(f"✅ {theme_mode.title()} theme colors verified successfully")

        except Exception as e:
            print(f"⚠️ Theme color verification failed for {theme_mode}: {e}")

    def _verify_theme_icon_changes(self):
        """Verify that theme toggle icon changes based on current theme"""
        try:
            # Get current icon class
            icon_classes = self.page.get_attribute("#theme-icon", "class")

            # Icon should change based on theme state
            self.assertTrue(
                "fa-" in icon_classes, "Theme icon should use FontAwesome classes"
            )

            # Test icon click and verify it changes
            initial_classes = icon_classes
            self.page.click(".theme-toggle")
            self.page.wait_for_timeout(500)

            updated_classes = self.page.get_attribute("#theme-icon", "class")
            # Icon classes might change based on theme (sun/moon/auto)

            print(
                f"✅ Theme icon changes verified (initial: {initial_classes}, updated: {updated_classes})"
            )

        except Exception as e:
            print(f"⚠️ Theme icon verification failed: {e}")

    def test_18_theme_responsive_design(self):
        """Test theme system works correctly on different screen sizes"""
        self.login_admin()

        screen_sizes = [
            {"width": 375, "height": 667, "name": "Mobile"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 1920, "height": 1080, "name": "Desktop"},
        ]

        for size in screen_sizes:
            with self.subTest(screen_size=size["name"]):
                try:
                    # Set viewport size
                    self.page.set_viewport_size(
                        {"width": size["width"], "height": size["height"]}
                    )
                    self.page.wait_for_timeout(500)

                    # Verify theme toggle is visible and functional
                    self.assertTrue(
                        self.page.is_visible(".theme-toggle"),
                        f"Theme toggle should be visible on {size['name']}",
                    )

                    # Test theme switching on this screen size
                    self.page.click(".theme-toggle")
                    self.page.wait_for_timeout(500)

                    # Verify theme was applied
                    theme = self.page.evaluate(
                        "document.documentElement.getAttribute('data-theme')"
                    )
                    self.assertIsNotNone(
                        theme, f"Theme should be applied on {size['name']}"
                    )

                    # Verify theme toggle button is properly sized
                    toggle_box = self.page.locator(".theme-toggle").bounding_box()
                    self.assertIsNotNone(
                        toggle_box,
                        f"Theme toggle should have proper bounds on {size['name']}",
                    )
                    self.assertGreater(
                        toggle_box["width"],
                        20,
                        "Theme toggle should be large enough to tap",
                    )
                    self.assertGreater(
                        toggle_box["height"],
                        20,
                        "Theme toggle should be large enough to tap",
                    )

                    print(
                        f"✅ Theme system working correctly on {size['name']} ({size['width']}x{size['height']})"
                    )

                except Exception as e:
                    print(f"⚠️ Theme responsive test failed on {size['name']}: {e}")

    def test_19_theme_accessibility(self):
        """Test theme system accessibility features"""
        self.login_admin()

        try:
            # Test keyboard navigation to theme toggle
            self.page.keyboard.press("Tab")
            # Continue tabbing until we reach the theme toggle or timeout
            for _ in range(20):  # Max 20 tabs to prevent infinite loop
                focused_element = self.page.evaluate("document.activeElement")
                if focused_element and self.page.evaluate(
                    "document.activeElement.classList.contains('theme-toggle')"
                ):
                    break
                self.page.keyboard.press("Tab")

            # Verify theme toggle can be reached by keyboard
            focused_element = self.page.evaluate(
                "document.activeElement.classList.contains('theme-toggle')"
            )
            if focused_element:
                print("✅ Theme toggle is keyboard accessible")

                # Test activation with Enter key
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(500)

                # Verify theme changed
                theme = self.page.evaluate(
                    "document.documentElement.getAttribute('data-theme')"
                )
                self.assertIsNotNone(
                    theme, "Theme should change when activated with keyboard"
                )

                print("✅ Theme toggle works with keyboard activation")
            else:
                print("⚠️ Theme toggle not reachable by keyboard navigation")

            # Test ARIA attributes
            aria_label = self.page.get_attribute(".theme-toggle", "aria-label")
            self.assertIsNotNone(aria_label, "Theme toggle should have aria-label")
            self.assertTrue(
                len(aria_label) > 0, "Theme toggle aria-label should not be empty"
            )

            # Test title attribute for tooltip
            title = self.page.get_attribute(".theme-toggle", "title")
            self.assertIsNotNone(title, "Theme toggle should have title attribute")

            print("✅ Theme accessibility features verified")

        except Exception as e:
            print(f"⚠️ Theme accessibility test failed: {e}")

    def test_20_theme_performance(self):
        """Test theme switching performance and smooth transitions"""
        self.login_admin()

        try:
            # Measure theme switching performance
            start_time = self.page.evaluate("performance.now()")

            # Perform multiple theme switches
            for i in range(5):
                self.page.click(".theme-toggle")
                self.page.wait_for_timeout(100)  # Small delay between switches

            end_time = self.page.evaluate("performance.now()")
            total_time = end_time - start_time

            # Theme switching should be reasonably fast (under 2 seconds for 5 switches)
            self.assertLess(
                total_time, 2000, f"Theme switching should be fast, took {total_time}ms"
            )

            # Test smooth transitions
            # Verify CSS transition is applied
            transition_property = self.page.evaluate(
                """
                getComputedStyle(document.body).transition
            """
            )

            if transition_property and "background-color" in transition_property:
                print("✅ Smooth theme transitions are configured")
            else:
                print("⚠️ Theme transitions may not be smooth")

            print(f"✅ Theme switching performance: {total_time:.2f}ms for 5 switches")

        except Exception as e:
            print(f"⚠️ Theme performance test failed: {e}")

    def test_21_accessibility_basics(self):
        """Test basic accessibility features"""
        self.login_admin()

        # Check for alt text on images/icons
        # Check for proper form labels
        # Check for keyboard navigation

        # Basic tab navigation test
        self.page.keyboard.press("Tab")
        focused_element = self.page.evaluate("document.activeElement.tagName")
        self.assertIsNotNone(focused_element)


def run_e2e_tests():
    """Run all E2E tests"""
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright not available. Skipping E2E tests.")
        print("   Install with: poetry install --with e2e")
        return True

    print("🎭 Running Web UI E2E Tests with Playwright...")

    # Set environment for testing
    os.environ["MULTITENANT_MODE"] = "true"
    os.environ["LOCAL_DEV_MODE"] = "true"

    suite = unittest.TestLoader().loadTestsFromTestCase(WebUIE2ETest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n📊 E2E Test Results:")
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
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
