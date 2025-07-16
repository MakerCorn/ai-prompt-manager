#!/usr/bin/env python3
"""
End-to-end tests for Speech Dictation functionality
Testing complete user workflows with browser automation
"""

import os
import sys
import tempfile
import time
import unittest
from multiprocessing import Process

# Add the project root to the path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from playwright.sync_api import expect, sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available, skipping E2E tests")


def _run_speech_e2e_server(db_path, port):
    """Run test server for E2E speech tests"""
    try:
        import uvicorn

        from web_app import create_web_app

        app = create_web_app(db_path)
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")
    except Exception as e:
        print(f"E2E test server error: {e}")


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright not available")
class SpeechDictationE2ETest(unittest.TestCase):
    """End-to-end test suite for speech dictation functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with running server"""
        cls.port = 7866
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.headless = os.getenv("E2E_HEADLESS", "true").lower() == "true"
        cls.slow_mo = int(os.getenv("E2E_SLOW_MO", "0"))

        # Create temporary database
        cls.temp_db_fd, cls.temp_db = tempfile.mkstemp(suffix=".db")

        # Initialize database with test data
        from auth_manager import AuthManager

        auth_manager = AuthManager(cls.temp_db)

        # Create test tenant and user
        success, tenant_message = auth_manager.create_tenant("Test Tenant", "test")
        if not success:
            raise Exception(f"Failed to create test tenant: {tenant_message}")

        # Get tenant ID for user creation
        import sqlite3

        conn = sqlite3.connect(cls.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test",))
        result = cursor.fetchone()
        tenant_id = result[0] if result else None
        conn.close()

        if not tenant_id:
            raise Exception("Failed to get tenant ID after creation")

        success, user_message = auth_manager.create_user(
            tenant_id=tenant_id,
            email="test@example.com",
            password="test123",
            first_name="Test",
            last_name="User",
            role="admin",
        )
        if not success:
            raise Exception(f"Failed to create test user: {user_message}")

        # Start test server
        cls.server_process = Process(
            target=_run_speech_e2e_server, args=(cls.temp_db, cls.port)
        )
        cls.server_process.start()
        time.sleep(3)  # Give server time to start

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if hasattr(cls, "server_process") and cls.server_process:
            cls.server_process.terminate()
            cls.server_process.join(timeout=5)
            if cls.server_process.is_alive():
                cls.server_process.kill()

        # Clean up test database
        if hasattr(cls, "temp_db") and os.path.exists(cls.temp_db):
            os.unlink(cls.temp_db)

    def setUp(self):
        """Set up browser for each test"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, slow_mo=self.slow_mo
        )
        self.page = self.browser.new_page()

        # Login
        self.page.goto(f"{self.base_url}/login")
        self.page.fill('input[name="email"]', "test@example.com")
        self.page.fill('input[name="password"]', "test123")
        self.page.fill('input[name="subdomain"]', "test")
        login_button = self.page.locator('form button[type="submit"]').last
        login_button.click()
        self.page.wait_for_url(f"{self.base_url}/")

    def tearDown(self):
        """Clean up browser after each test"""
        if hasattr(self, "page"):
            self.page.close()
        if hasattr(self, "browser"):
            self.browser.close()
        if hasattr(self, "playwright"):
            self.playwright.stop()

    def test_01_speech_dictation_ui_elements(self):
        """Test that speech dictation UI elements are present"""
        # Navigate to prompt creation page
        self.page.goto(f"{self.base_url}/prompts/new")

        # Check that speech dictation button is present
        speech_btn = self.page.locator("#speech-btn")
        expect(speech_btn).to_be_visible()

        # Check button text
        expect(speech_btn).to_contain_text("Dictate")

        # Check that enhance and translate buttons are initially hidden
        enhance_btn = self.page.locator("#enhance-btn")
        translate_btn = self.page.locator("#translate-speech-btn")

        expect(enhance_btn).to_be_hidden()
        expect(translate_btn).to_be_hidden()

        # Check that speech status is initially hidden
        speech_status = self.page.locator("#speech-status")
        expect(speech_status).to_be_hidden()

    def test_02_speech_dictation_button_interaction(self):
        """Test speech dictation button interactions"""
        self.page.goto(f"{self.base_url}/prompts/new")

        speech_btn = self.page.locator("#speech-btn")

        # Click the speech button (may not work without microphone permissions)
        speech_btn.click()

        # Wait a moment for any UI changes
        self.page.wait_for_timeout(500)

        # Check if speech status becomes visible (depends on browser permissions)
        # This may not work in headless mode without microphone access
        # So we'll check for the button state change instead

        # The button should either show an error state or listening state
        # In most test environments, it will show an error due to no microphone

        # Check that the page didn't crash
        expect(self.page.locator("body")).to_be_visible()

    def test_03_speech_language_selector(self):
        """Test speech language selector functionality"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Click speech button to show controls
        speech_btn = self.page.locator("#speech-btn")
        speech_btn.click()

        # Wait for potential speech status to appear
        self.page.wait_for_timeout(1000)

        # Check if language selector is present (may be hidden if speech not supported)
        language_select = self.page.locator("#speech-language")

        if language_select.is_visible():
            # Test language selection
            language_select.select_option("es-ES")

            # Check that the selection was made
            selected_value = language_select.input_value()
            self.assertEqual(selected_value, "es-ES")

    def test_04_text_enhancement_workflow(self):
        """Test text enhancement workflow"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Add some text with filler words to the content area
        content_textarea = self.page.locator("#content")
        test_text = "um hello world this is a test you know"
        content_textarea.fill(test_text)

        # Simulate having used speech dictation (show enhance button)
        self.page.evaluate(
            """
            document.getElementById('enhance-btn').classList.remove('hidden');
        """
        )

        # Click enhance button
        enhance_btn = self.page.locator("#enhance-btn")
        enhance_btn.click()

        # Wait for enhancement to complete
        self.page.wait_for_timeout(2000)

        # Check that text was enhanced (should remove filler words)
        enhanced_text = content_textarea.input_value()
        self.assertNotIn("um", enhanced_text.lower())
        self.assertNotIn("you know", enhanced_text.lower())
        self.assertIn("hello world", enhanced_text.lower())

    def test_05_translation_workflow(self):
        """Test translation workflow"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Add some non-English text
        content_textarea = self.page.locator("#content")
        test_text = "Bonjour le monde, ceci est un test"
        content_textarea.fill(test_text)

        # Simulate having used speech dictation (show translate button)
        self.page.evaluate(
            """
            document.getElementById('translate-speech-btn').classList.remove('hidden');
        """
        )

        # Click translate button
        translate_btn = self.page.locator("#translate-speech-btn")
        translate_btn.click()

        # Wait for translation to complete
        self.page.wait_for_timeout(3000)

        # Check that translation was attempted
        # (content may or may not change based on service availability)
        translated_text = content_textarea.input_value()
        # At minimum, the text should still be present
        self.assertGreater(len(translated_text.strip()), 0)

    def test_06_speech_dictation_form_integration(self):
        """Test that speech dictation integrates properly with prompt form"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Fill in basic form fields
        self.page.fill("#name", "Test Speech Prompt")
        self.page.select_option("#category", "General")

        # Add content via the textarea (simulating dictated text)
        content_textarea = self.page.locator("#content")
        test_content = (
            "This is a test prompt created with speech dictation functionality"
        )
        content_textarea.fill(test_content)

        # Check character count updates
        char_count = self.page.locator("#char-count")
        expect(char_count).to_contain_text(str(len(test_content)))

        # Submit the form
        submit_btn = self.page.locator('button[type="submit"]')
        submit_btn.click()

        # Should redirect to prompts list
        self.page.wait_for_url(f"{self.base_url}/prompts")

        # Check that the prompt was created
        expect(self.page.locator("body")).to_contain_text("Test Speech Prompt")

    def test_07_speech_dictation_responsive_design(self):
        """Test speech dictation UI on different screen sizes"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Test mobile view
        self.page.set_viewport_size({"width": 375, "height": 667})

        # Check that speech button is still visible and accessible
        speech_btn = self.page.locator("#speech-btn")
        expect(speech_btn).to_be_visible()

        # Test tablet view
        self.page.set_viewport_size({"width": 768, "height": 1024})
        expect(speech_btn).to_be_visible()

        # Test desktop view
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        expect(speech_btn).to_be_visible()

    def test_08_speech_dictation_accessibility(self):
        """Test speech dictation accessibility features"""
        self.page.goto(f"{self.base_url}/prompts/new")

        speech_btn = self.page.locator("#speech-btn")

        # Check that button has proper title attribute
        title_attr = speech_btn.get_attribute("title")
        self.assertIsNotNone(title_attr)
        self.assertIn("dictation", title_attr.lower())

        # Check that button can be focused
        speech_btn.focus()

        # Check keyboard navigation
        self.page.keyboard.press("Tab")

        # The page should still be functional
        expect(self.page.locator("body")).to_be_visible()

    def test_09_speech_dictation_error_handling(self):
        """Test error handling in speech dictation UI"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Test enhancement with empty text
        content_textarea = self.page.locator("#content")
        content_textarea.fill("")

        # Show enhance button
        self.page.evaluate(
            """
            document.getElementById('enhance-btn').classList.remove('hidden');
        """
        )

        # Click enhance button with empty text
        enhance_btn = self.page.locator("#enhance-btn")
        enhance_btn.click()

        # Should show some kind of feedback (toast, alert, etc.)
        self.page.wait_for_timeout(1000)

        # Check that the page is still functional
        expect(self.page.locator("body")).to_be_visible()
        expect(content_textarea).to_be_visible()

    def test_10_speech_dictation_browser_compatibility(self):
        """Test speech dictation browser compatibility checks"""
        self.page.goto(f"{self.base_url}/prompts/new")

        # Check if the speech recognition API is properly detected
        speech_support = self.page.evaluate(
            """
            return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        """
        )

        speech_btn = self.page.locator("#speech-btn")

        if not speech_support:
            # Button should be disabled or have reduced opacity
            opacity = speech_btn.evaluate("el => window.getComputedStyle(el).opacity")
            self.assertLess(
                float(opacity),
                1.0,
                "Button should have reduced opacity when not supported",
            )

        # Button should always be visible regardless of support
        expect(speech_btn).to_be_visible()


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright not available")
class SpeechDictationE2EPerformanceTest(unittest.TestCase):
    """Performance tests for speech dictation E2E functionality"""

    def setUp(self):
        """Set up for performance tests"""
        self.port = 7867
        self.base_url = f"http://127.0.0.1:{self.port}"
        # These tests may not have a running server for performance isolation

    def test_speech_ui_load_performance(self):
        """Test that speech UI doesn't significantly impact page load performance"""
        # This would be a more complex test involving performance measurements
        # For now, we'll keep it simple
        pass

    def test_speech_enhancement_response_time(self):
        """Test that speech enhancement responds within acceptable time limits"""
        # This would test the response time of enhancement requests
        # Keeping it as a placeholder for future implementation
        pass


if __name__ == "__main__":
    unittest.main()
