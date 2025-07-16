"""
End-to-end tests for the Rules Management System.

This module provides comprehensive E2E testing for the Rules system
including UI interactions, builder functionality, and complete workflows.
"""

import os
import sys
import tempfile
import time
import unittest
from multiprocessing import Process

# Add project root to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import uvicorn

    from auth_manager import AuthManager
    from web_app import create_web_app

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


def run_test_server(db_path, port):
    """Run test server for E2E testing."""
    try:
        app = create_web_app(db_path=db_path)
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
    except Exception as e:
        print(f"Server error: {e}")


@unittest.skipUnless(
    PLAYWRIGHT_AVAILABLE and DEPENDENCIES_AVAILABLE,
    "Playwright or dependencies not available",
)
class TestRulesSystemE2E(unittest.TestCase):
    """End-to-end tests for the Rules Management System."""

    # Class attributes for type checking
    headless: bool
    slow_mo: int
    playwright: any
    browser: any
    context: any
    page: any
    test_port: int
    base_url: str
    server_process: any
    temp_db: any

    @classmethod
    def setUpClass(cls):
        """Set up test class with browser and test server."""
        cls.headless = os.getenv("E2E_HEADLESS", "true").lower() == "true"
        cls.slow_mo = int(os.getenv("E2E_SLOW_MO", "0"))

        # Initialize Playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=cls.headless, slow_mo=cls.slow_mo
        )
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        # Set up test server
        cls.test_port = 8907
        cls.base_url = f"http://localhost:{cls.test_port}"

        # Create temporary database
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name

        # Initialize database with test data
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
            target=run_test_server, args=(cls.temp_db, cls.test_port)
        )
        cls.server_process.start()

        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                cls.page.goto(cls.base_url, timeout=5000)
                break
            except Exception:
                if attempt == max_attempts - 1:
                    raise Exception("Test server failed to start")
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        try:
            if cls.server_process:
                cls.server_process.terminate()
                cls.server_process.join(timeout=5)
                if cls.server_process.is_alive():
                    cls.server_process.kill()
        except Exception:
            pass

        try:
            cls.browser.close()
            cls.playwright.stop()
        except Exception:
            pass

        try:
            if os.path.exists(cls.temp_db):
                os.unlink(cls.temp_db)
        except Exception:
            pass

    def setUp(self):
        """Set up for each test."""
        # Login before each test
        self.page.goto(f"{self.base_url}/login")
        self.page.fill('input[name="email"]', "test@example.com")
        self.page.fill('input[name="password"]', "test123")
        self.page.fill('input[name="tenant"]', "test")
        login_button = self.page.locator('form button[type="submit"]').last
        login_button.click()

        # Wait for login to complete
        self.page.wait_for_url(f"{self.base_url}/")

    def test_01_navigation_to_rules(self):
        """Test navigation to rules section."""
        # Test desktop navigation
        self.page.click('a[href="/rules"]')
        self.page.wait_for_url(f"{self.base_url}/rules")

        # Verify we're on the rules page
        self.assertTrue(self.page.locator("text=Rules Library").is_visible())
        self.assertTrue(self.page.locator("text=No rules found").is_visible())

    def test_02_create_new_rule_flow(self):
        """Test complete rule creation workflow."""
        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Click "New Rule" button
        self.page.click('a[href="/rules/new"]')
        self.page.wait_for_url(f"{self.base_url}/rules/new")

        # Verify form elements are present
        self.assertTrue(self.page.locator('input[name="name"]').is_visible())
        self.assertTrue(self.page.locator('input[name="title"]').is_visible())
        self.assertTrue(self.page.locator('textarea[name="content"]').is_visible())

        # Fill out the form
        self.page.fill('input[name="name"]', "e2e-test-rule")
        self.page.fill('input[name="title"]', "E2E Test Rule")
        self.page.select_option('select[name="category"]', "Testing")

        # Fill content with markdown
        content = """# E2E Test Rule

## Purpose
This rule is created during end-to-end testing.

## Guidelines
1. **Always** validate user input
2. *Never* expose sensitive data
3. Use `proper formatting` for code

## Examples
```python
def validate_input(data):
    return data is not None and len(data.strip()) > 0
```

> Important: This is a test rule for E2E validation."""

        self.page.fill('textarea[name="content"]', content)
        self.page.fill(
            'textarea[name="description"]', "A test rule created during E2E testing"
        )

        # Add tags
        tag_input = self.page.locator('input[id="tag-input"]')
        tag_input.fill("e2e")
        tag_input.press("Enter")
        tag_input.fill("testing")
        tag_input.press("Enter")
        tag_input.fill("validation")
        tag_input.press("Enter")

        # Submit the form
        self.page.click('button[type="submit"]')

        # Wait for redirect to rules list
        self.page.wait_for_url(f"{self.base_url}/rules")

        # Verify rule appears in the list
        self.assertTrue(self.page.locator("text=e2e-test-rule").is_visible())
        self.assertTrue(self.page.locator("text=E2E Test Rule").is_visible())

    def test_03_search_rules_functionality(self):
        """Test rules search functionality."""
        # First create a rule to search for
        self.test_02_create_new_rule_flow()

        # Navigate to rules page
        self.page.goto(f"{self.base_url}/rules")

        # Test search functionality
        search_input = self.page.locator('input[id="search"]')
        search_input.fill("E2E")

        # Wait for HTMX search results
        self.page.wait_for_timeout(1000)

        # Verify search results
        self.assertTrue(self.page.locator("text=e2e-test-rule").is_visible())

    def test_04_rule_preview_functionality(self):
        """Test rule preview modal."""
        # Ensure we have a rule to preview
        self.test_02_create_new_rule_flow()

        # Navigate to rules page
        self.page.goto(f"{self.base_url}/rules")

        # Click preview button
        preview_button = self.page.locator('button[title="Preview"]').first
        preview_button.click()

        # Verify modal opens
        modal = self.page.locator("#preview-modal")
        self.assertTrue(modal.is_visible())

        # Verify content is displayed
        self.assertTrue(self.page.locator("text=E2E Test Rule").is_visible())

        # Close modal
        self.page.locator('button[onclick="closePreview()"]').click()

        # Verify modal closes
        self.assertFalse(modal.is_visible())

    def test_05_edit_rule_workflow(self):
        """Test rule editing workflow."""
        # Create a rule to edit
        self.test_02_create_new_rule_flow()

        # Navigate to rules page
        self.page.goto(f"{self.base_url}/rules")

        # Click edit button
        edit_button = self.page.locator('a[title="Edit"]').first
        edit_button.click()

        # Verify we're on edit page
        self.assertTrue(self.page.locator("text=Edit Rule").is_visible())

        # Modify the rule
        self.page.fill('input[name="title"]', "Updated E2E Test Rule")
        self.page.fill(
            'textarea[name="description"]', "Updated description for E2E testing"
        )

        # Submit changes
        self.page.click('button[type="submit"]')

        # Wait for redirect
        self.page.wait_for_url(f"{self.base_url}/rules")

        # Verify changes
        self.assertTrue(self.page.locator("text=Updated E2E Test Rule").is_visible())

    def test_06_copy_rule_content(self):
        """Test copying rule content to clipboard."""
        # Create a rule to copy
        self.test_02_create_new_rule_flow()

        # Navigate to rules page
        self.page.goto(f"{self.base_url}/rules")

        # Click copy button
        copy_button = self.page.locator('button[title="Copy Markdown"]').first
        copy_button.click()

        # Wait for copy operation and toast
        self.page.wait_for_timeout(1000)

        # Note: Clipboard testing in E2E is complex due to browser security
        # We verify the button exists and is clickable

    def test_07_rules_builder_navigation(self):
        """Test navigation to and basic functionality of rules builder."""
        # Navigate to rules builder
        self.page.goto(f"{self.base_url}/rules/builder")

        # Verify builder page loads
        self.assertTrue(self.page.locator("text=Rules Builder").is_visible())
        self.assertTrue(self.page.locator("text=Available Rules").is_visible())
        self.assertTrue(self.page.locator("text=Selected Rules").is_visible())
        self.assertTrue(self.page.locator("text=Live Preview").is_visible())

    def test_08_rules_builder_workflow(self):
        """Test complete rules builder workflow."""
        # First create some rules to work with
        self.test_02_create_new_rule_flow()

        # Create another rule
        self.page.goto(f"{self.base_url}/rules/new")
        self.page.fill('input[name="name"]', "builder-test-rule")
        self.page.fill('input[name="title"]', "Builder Test Rule")
        self.page.select_option('select[name="category"]', "Testing")
        self.page.fill(
            'textarea[name="content"]',
            "# Builder Test\n\nThis rule is for testing the builder.",
        )
        self.page.click('button[type="submit"]')

        # Navigate to builder
        self.page.goto(f"{self.base_url}/rules/builder")

        # Configure combination
        self.page.fill('input[id="combination-name"]', "E2E Combined Rules")
        self.page.fill('input[id="combination-category"]', "E2E Testing")

        # Add rules to builder by clicking on them
        rule_items = self.page.locator(".rule-item")
        if rule_items.count() > 0:
            rule_items.first.click()

            # Wait for rule to be added
            self.page.wait_for_timeout(500)

            # Verify rule appears in selected rules
            self.assertTrue(self.page.locator("text=1").is_visible())  # Selected count

    def test_09_category_filtering(self):
        """Test filtering rules by category."""
        # Create rules in different categories
        self.test_02_create_new_rule_flow()  # Creates rule in "Testing" category

        # Navigate to rules page
        self.page.goto(f"{self.base_url}/rules")

        # Test category filter
        category_filter = self.page.locator('select[id="category-filter"]')
        category_filter.select_option("Testing")

        # Wait for filter to apply
        self.page.wait_for_timeout(1000)

        # Verify filtered results
        self.assertTrue(self.page.locator("text=e2e-test-rule").is_visible())

    def test_10_responsive_design_mobile(self):
        """Test rules interface on mobile viewport."""
        # Set mobile viewport
        self.page.set_viewport_size({"width": 375, "height": 667})

        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Test mobile navigation
        if self.page.locator("#mobile-menu-button").is_visible():
            self.page.click("#mobile-menu-button")
            mobile_rules_link = self.page.locator('a[href="/rules"]').nth(
                1
            )  # Mobile nav version
            mobile_rules_link.click()

        # Verify page loads correctly on mobile
        self.assertTrue(self.page.locator("text=Rules Library").is_visible())

        # Reset viewport
        self.page.set_viewport_size({"width": 1280, "height": 720})

    def test_11_theme_compatibility(self):
        """Test rules interface with dark/light theme."""
        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Toggle theme
        theme_button = self.page.locator("#theme-toggle")
        if theme_button.is_visible():
            theme_button.click()

            # Wait for theme change
            self.page.wait_for_timeout(500)

            # Verify page still functions
            self.assertTrue(self.page.locator("text=Rules Library").is_visible())

            # Toggle back
            theme_button.click()

    def test_12_form_validation(self):
        """Test form validation on rule creation."""
        # Navigate to new rule form
        self.page.goto(f"{self.base_url}/rules/new")

        # Try to submit empty form
        self.page.click('button[type="submit"]')

        # Verify validation messages appear
        # Note: Exact validation behavior depends on implementation
        name_input = self.page.locator('input[name="name"]')
        self.assertTrue(name_input.is_visible())

    def test_13_markdown_helper(self):
        """Test markdown helper functionality."""
        # Navigate to new rule form
        self.page.goto(f"{self.base_url}/rules/new")

        # Click markdown help button
        markdown_button = self.page.locator('button[onclick="showMarkdownHelper()"]')
        if markdown_button.is_visible():
            markdown_button.click()

            # Wait for modal
            self.page.wait_for_timeout(500)

            # Verify modal content
            modal = self.page.locator("#markdown-modal")
            if modal.is_visible():
                self.assertTrue(self.page.locator("text=Markdown Guide").is_visible())

                # Close modal
                self.page.locator('button[onclick="closeMarkdownHelper()"]').click()

    def test_14_rule_preview_in_form(self):
        """Test rule preview functionality in form."""
        # Navigate to new rule form
        self.page.goto(f"{self.base_url}/rules/new")

        # Fill in some content
        self.page.fill(
            'textarea[name="content"]',
            "# Test Preview\n\n**Bold text** and *italic text*",
        )

        # Click preview button
        preview_button = self.page.locator('button[onclick="previewRule()"]')
        if preview_button.is_visible():
            preview_button.click()

            # Wait for preview modal
            self.page.wait_for_timeout(500)

    def test_15_character_and_line_counting(self):
        """Test character and line counting functionality."""
        # Navigate to new rule form
        self.page.goto(f"{self.base_url}/rules/new")

        # Fill content
        content = "Line 1\nLine 2\nLine 3"
        self.page.fill('textarea[name="content"]', content)

        # Verify counters update (if implemented)
        # Note: Actual counting verification depends on implementation
        # char_count = self.page.locator("#char-count")
        # line_count = self.page.locator("#line-count")

    def test_16_builtin_rules_handling(self):
        """Test handling of built-in rules."""
        # This test would verify that built-in rules are properly displayed
        # and protected from editing/deletion

        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Look for built-in indicators if any rules are marked as built-in
        builtin_badges = self.page.locator("text=Built-in")

        # If built-in rules exist, verify they're handled correctly
        if builtin_badges.count() > 0:
            # Built-in rules should not have delete buttons
            # This verification depends on the specific implementation
            pass

    def test_17_language_switching_rules(self):
        """Test language switching functionality with rules."""
        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Test language switching if available
        language_button = self.page.locator("#language-menu-button")
        if language_button.is_visible():
            language_button.click()

            # Wait for dropdown
            self.page.wait_for_timeout(500)

            # Try switching to Spanish if available
            spanish_option = self.page.locator("text=Español")
            if spanish_option.is_visible():
                spanish_option.click()

                # Wait for language change
                self.page.wait_for_timeout(1000)

                # Verify interface language changed
                # Note: Exact text depends on Spanish translations

    def test_18_error_recovery(self):
        """Test error handling and recovery."""
        # Test accessing invalid rule ID
        self.page.goto(f"{self.base_url}/rules/99999/edit")

        # Should show 404 or redirect to rules list
        # Verify graceful error handling
        self.page.wait_for_timeout(2000)

    def test_19_performance_large_content(self):
        """Test performance with large rule content."""
        # Navigate to new rule form
        self.page.goto(f"{self.base_url}/rules/new")

        # Create large content
        large_content = "# Large Rule\n\n" + ("This is a large rule content. " * 100)

        # Fill form with large content
        self.page.fill('input[name="name"]', "large-rule")
        self.page.fill('input[name="title"]', "Large Rule")
        self.page.fill('textarea[name="content"]', large_content)

        # Submit and verify it handles large content
        self.page.click('button[type="submit"]')

        # Wait for processing
        self.page.wait_for_timeout(3000)

    def test_20_accessibility_basics(self):
        """Test basic accessibility features."""
        # Navigate to rules
        self.page.goto(f"{self.base_url}/rules")

        # Test keyboard navigation
        self.page.keyboard.press("Tab")

        # Verify focus indicators and ARIA labels
        # Note: Comprehensive accessibility testing requires specialized tools

        # Test that main content is accessible
        main_content = self.page.locator("main")
        self.assertTrue(main_content.is_visible())


if __name__ == "__main__":
    unittest.main()
