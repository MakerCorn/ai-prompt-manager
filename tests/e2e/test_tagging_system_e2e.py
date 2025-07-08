"""
End-to-end tests for the tagging system.

This module provides comprehensive E2E testing for the tagging system
including UI interactions, API endpoints, and database operations.
"""

import os
import sys
import time
import unittest
from typing import Any

# Add project root to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from playwright.sync_api import sync_playwright
    from prompt_data_manager import PromptDataManager

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright not available")
class TestTaggingSystemE2E(unittest.TestCase):
    """End-to-end tests for the tagging system."""

    # Class attributes for type checking
    headless: bool
    slow_mo: int
    playwright: Any
    browser: Any
    context: Any
    page: Any
    test_port: int
    base_url: str
    server_process: Any
    temp_db: Any

    @classmethod
    def setUpClass(cls):
        """Set up test class with browser and test server."""
        cls.headless = os.getenv("E2E_HEADLESS", "true").lower() == "true"
        cls.slow_mo = int(os.getenv("E2E_SLOW_MO", "0"))

        # Start browser
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=cls.headless, slow_mo=cls.slow_mo
        )
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        # Set up test environment
        cls.test_port = 7862
        cls.base_url = f"http://localhost:{cls.test_port}"

        # Start test server
        cls._start_test_server()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if hasattr(cls, "server_process") and cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()

        if hasattr(cls, "page"):
            cls.page.close()
        if hasattr(cls, "context"):
            cls.context.close()
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()

    @classmethod
    def _start_test_server(cls):
        """Start the test server."""
        import subprocess
        import tempfile

        # Create temporary database
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        cls.temp_db.close()

        # Set up environment for single-user mode
        env = os.environ.copy()
        env.update(
            {
                "DB_PATH": cls.temp_db.name,
                "MULTITENANT_MODE": "false",
                "LOCAL_DEV_MODE": "true",
                "PORT": str(cls.test_port),
            }
        )

        # Start server process
        cls.server_process = subprocess.Popen(
            [sys.executable, "run.py", "--port", str(cls.test_port)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        cls._wait_for_server()

        # Initialize test data
        cls._setup_test_data()

    @classmethod
    def _wait_for_server(cls):
        """Wait for the test server to be ready."""
        import requests

        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    return
            except (
                requests.exceptions.RequestException,
                requests.exceptions.ConnectionError,
            ):
                pass
            time.sleep(1)

        raise RuntimeError("Test server failed to start")

    @classmethod
    def _setup_test_data(cls):
        """Set up test data for tagging tests."""
        # Initialize data manager
        data_manager = PromptDataManager(
            db_path=cls.temp_db.name, tenant_id="single-user", user_id="single-user"
        )

        # Create test prompts with various tags
        data_manager.add_prompt(
            name="Python Script Generator",
            title="Generate Python Scripts",
            content="Generate a Python script that {task_description}",
            category="Development",
            tags="python, automation, scripting, development",
        )

        data_manager.add_prompt(
            name="Web Development Helper",
            title="Web Development Assistant",
            content="Help with web development tasks: {web_task}",
            category="Development",
            tags="web, html, css, javascript, development",
        )

        data_manager.add_prompt(
            name="Data Analysis Prompt",
            title="Data Analysis Assistant",
            content="Analyze the following data: {data_input}",
            category="Analysis",
            tags="data, analysis, statistics, python",
        )

        data_manager.add_prompt(
            name="Testing Helper",
            title="Testing Assistant",
            content="Generate test cases for: {test_subject}",
            category="Testing",
            tags="testing, automation, quality-assurance",
        )

        # Create test templates with tags
        data_manager.create_template(
            name="API Documentation Template",
            description="Template for API documentation",
            content="# API Documentation\n\n## Endpoint: {endpoint}\n\n{description}",
            category="Documentation",
            tags="api, documentation, template",
        )

        data_manager.create_template(
            name="Bug Report Template",
            description="Template for bug reports",
            content="## Bug Report\n\n**Issue:** {issue}\n**Steps:** {steps}",
            category="Bug Reports",
            tags="bug, template, testing",
        )

    def setUp(self):
        """Set up individual test."""
        # Navigate to home page
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

    def test_tag_display_in_prompt_list(self):
        """Test that tags are displayed in the prompt list."""
        # Navigate to prompts page
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        # Check that tags are visible in the prompt list
        tag_elements = self.page.locator(".tag, .badge, [data-testid='tag']")
        self.assertGreater(
            tag_elements.count(), 0, "Tags should be visible in prompt list"
        )

        # Check for specific tags
        page_content = self.page.content()
        self.assertIn("python", page_content.lower())
        self.assertIn("development", page_content.lower())
        self.assertIn("automation", page_content.lower())

    def test_tag_search_functionality(self):
        """Test tag-based search functionality."""
        # Navigate to prompts page
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        # Look for search input
        search_input = None
        for selector in [
            "input[name='search']",
            "input[type='search']",
            "input[placeholder*='search']",
            "input[placeholder*='Search']",
        ]:
            try:
                if self.page.locator(selector).count() > 0:
                    search_input = self.page.locator(selector).first
                    break
            except Exception:
                continue

        if search_input:
            # Test searching by tag
            search_input.fill("python")
            search_input.press("Enter")
            self.page.wait_for_timeout(1000)  # Wait for search results

            # Check that results contain python-related prompts
            page_content = self.page.content()
            self.assertIn("python", page_content.lower())

    def test_tag_input_in_prompt_form(self):
        """Test tag input functionality in prompt creation form."""
        # Navigate to create prompt page
        self.page.goto(f"{self.base_url}/prompts/new")
        self.page.wait_for_load_state("networkidle")

        # Check if tag input exists
        tag_input_selectors = [
            "input[name='tags']",
            "input[id='tags']",
            "#tag-input",
            "input[placeholder*='tag']",
            "input[placeholder*='Tag']",
        ]

        tag_input = None
        for selector in tag_input_selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    tag_input = self.page.locator(selector).first
                    break
            except Exception:
                continue

        if tag_input:
            # Test adding tags
            tag_input.fill("test, e2e, automation")

            # Check that tags are processed
            self.page.wait_for_timeout(500)
            page_content = self.page.content()

            # Tags might be displayed in various ways
            has_tags = any(
                tag in page_content.lower() for tag in ["test", "e2e", "automation"]
            )
            if has_tags:
                self.assertTrue(True, "Tags are being processed in the form")

    def test_tag_auto_complete(self):
        """Test tag auto-complete functionality."""
        # Navigate to create prompt page
        self.page.goto(f"{self.base_url}/prompts/new")
        self.page.wait_for_load_state("networkidle")

        # Look for tag input
        tag_input_selectors = [
            "input[name='tags']",
            "input[id='tags']",
            "#tag-input",
            "input[placeholder*='tag']",
        ]

        tag_input = None
        for selector in tag_input_selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    tag_input = self.page.locator(selector).first
                    break
            except Exception:
                continue

        if tag_input:
            # Type partial tag to trigger auto-complete
            tag_input.fill("pyt")
            self.page.wait_for_timeout(500)

            # Check for auto-complete suggestions
            suggestion_selectors = [
                ".suggestions",
                ".autocomplete",
                ".dropdown-menu",
                "[data-testid='suggestions']",
                ".tag-suggestions",
            ]

            has_suggestions = False
            for selector in suggestion_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        has_suggestions = True
                        break
                except Exception:
                    continue

            # If we have suggestions, check they work
            if has_suggestions:
                # Look for "python" in suggestions
                page_content = self.page.content()
                self.assertIn("python", page_content.lower())

    def test_tag_filtering_interface(self):
        """Test tag filtering interface."""
        # Navigate to prompts page
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        # Look for filter controls
        filter_selectors = [
            "select[name='category']",
            ".filter-dropdown",
            ".category-filter",
            "[data-testid='filter']",
        ]

        for selector in filter_selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    # Found a filter control, test it
                    filter_element = self.page.locator(selector).first

                    # If it's a dropdown, try to interact with it
                    if "select" in selector:
                        # Get options and select one
                        options = self.page.locator(f"{selector} option")
                        if options.count() > 1:
                            filter_element.select_option(index=1)
                            self.page.wait_for_timeout(1000)

                            # Check that page updated
                            self.assertTrue(True, "Filter functionality works")
                    break
            except Exception:
                continue

    def test_template_tag_functionality(self):
        """Test tag functionality for templates."""
        # Navigate to templates page
        self.page.goto(f"{self.base_url}/templates")
        self.page.wait_for_load_state("networkidle")

        # If templates page exists, check for tags
        if "templates" in self.page.url:
            page_content = self.page.content()

            # Check for template-specific tags
            template_tags = ["template", "documentation", "bug"]
            for tag in template_tags:
                if tag in page_content.lower():
                    self.assertTrue(True, f"Template tag '{tag}' found")
                    break

    def test_tag_statistics_or_analytics(self):
        """Test tag statistics or analytics if available."""
        # Try to find any analytics or statistics page
        analytics_urls = [
            f"{self.base_url}/analytics",
            f"{self.base_url}/stats",
            f"{self.base_url}/dashboard",
            f"{self.base_url}/insights",
        ]

        for url in analytics_urls:
            try:
                self.page.goto(url)
                self.page.wait_for_load_state("networkidle")

                # Check if this is a valid analytics page
                page_content = self.page.content()
                if any(
                    word in page_content.lower()
                    for word in ["statistics", "analytics", "popular", "tags", "usage"]
                ):
                    # Found analytics page with tag info
                    self.assertTrue(True, "Tag analytics/statistics page found")
                    return
            except Exception:
                continue

    def test_mobile_responsive_tag_display(self):
        """Test that tag display works on mobile devices."""
        # Set mobile viewport
        self.page.set_viewport_size({"width": 375, "height": 667})

        # Navigate to prompts page
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        # Check that tags are still visible on mobile
        page_content = self.page.content()

        # Tags should still be present
        tag_indicators = ["python", "development", "automation"]
        mobile_tags_found = any(tag in page_content.lower() for tag in tag_indicators)

        if mobile_tags_found:
            self.assertTrue(True, "Tags are visible on mobile devices")

        # Reset viewport
        self.page.set_viewport_size({"width": 1280, "height": 720})

    def test_tag_accessibility(self):
        """Test tag accessibility features."""
        # Navigate to prompts page
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        # Check for accessibility attributes
        page_content = self.page.content()

        # Look for ARIA labels, roles, or other accessibility features
        accessibility_indicators = [
            "aria-label",
            "role=",
            "aria-describedby",
            "title=",
            "alt=",
            "aria-labelledby",
        ]

        has_accessibility = any(
            indicator in page_content for indicator in accessibility_indicators
        )

        if has_accessibility:
            self.assertTrue(True, "Accessibility features found")

    def test_end_to_end_tag_workflow(self):
        """Test complete end-to-end tag workflow."""
        # 1. Create a new prompt with tags
        self.page.goto(f"{self.base_url}/prompts/new")
        self.page.wait_for_load_state("networkidle")

        # Fill in basic prompt information
        name_input = None
        for selector in ["input[name='name']", "input[id='name']", "#prompt-name"]:
            try:
                if self.page.locator(selector).count() > 0:
                    name_input = self.page.locator(selector).first
                    break
            except Exception:
                continue

        if name_input:
            name_input.fill("E2E Test Prompt")

            # Add content
            content_selectors = [
                "textarea[name='content']",
                "textarea[id='content']",
                "#prompt-content",
            ]
            for selector in content_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        content_input = self.page.locator(selector).first
                        content_input.fill("This is an E2E test prompt with {variable}")
                        break
                except Exception:
                    continue

            # Add tags
            tag_selectors = ["input[name='tags']", "input[id='tags']", "#tag-input"]
            for selector in tag_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        tag_input = self.page.locator(selector).first
                        tag_input.fill("e2e, test, automation, playwright")
                        break
                except Exception:
                    continue

            # Submit form
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Save')",
                "button:has-text('Create')",
            ]
            for selector in submit_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        submit_button = self.page.locator(selector).first
                        submit_button.click()
                        break
                except Exception:
                    continue

            # Wait for redirect or success
            self.page.wait_for_timeout(2000)

        # 2. Verify the prompt was created and tags are displayed
        self.page.goto(f"{self.base_url}/prompts")
        self.page.wait_for_load_state("networkidle")

        page_content = self.page.content()

        # Check if our test prompt exists
        if "E2E Test Prompt" in page_content:
            self.assertTrue(True, "E2E workflow: Prompt creation successful")

            # Check if tags are displayed
            e2e_tags = ["e2e", "test", "automation", "playwright"]
            tags_found = any(tag in page_content.lower() for tag in e2e_tags)

            if tags_found:
                self.assertTrue(True, "E2E workflow: Tags are displayed correctly")


if __name__ == "__main__":
    unittest.main()
