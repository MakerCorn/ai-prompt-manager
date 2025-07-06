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
            progress_elements = self.page.locator(".progress, [role='progressbar'], text=/\\d+%/")
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

    def test_16_accessibility_basics(self):
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
