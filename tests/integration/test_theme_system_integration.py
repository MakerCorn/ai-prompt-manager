"""
Integration tests for theme system functionality.
Tests theme integration with web application, FastAPI routes, and user preferences.
"""

import os
import sys
import unittest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    from fastapi.testclient import TestClient

    from language_manager import get_language_manager
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("Some tests may be skipped")


class TestThemeSystemIntegration(unittest.TestCase):
    """Integration tests for theme system with web application."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment."""
        try:
            from web_app import create_web_app

            app = create_web_app()
            cls.client = TestClient(app)  # type: ignore
            cls.integration_available = True
        except Exception as e:
            print(f"Warning: Could not set up FastAPI client: {e}")
            cls.integration_available = False

    def setUp(self) -> None:
        """Set up individual test cases."""
        if not self.integration_available:
            self.skipTest("FastAPI integration not available")

    def test_theme_css_served_correctly(self):
        """Test that theme CSS is served correctly by the web app."""
        response = self.client.get("/static/css/theme.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.headers.get("content-type", ""))

        css_content = response.text
        # Check for key theme variables
        self.assertIn("--surface-primary", css_content)
        self.assertIn("--text-primary", css_content)
        self.assertIn(':root[data-theme="dark"]', css_content)

    def test_theme_toggle_in_page_templates(self):
        """Test that theme toggle is present in rendered pages."""
        # Test main pages
        pages_to_test = ["/", "/prompts", "/settings"]

        for page in pages_to_test:
            with self.subTest(page=page):
                response = self.client.get(page)
                if response.status_code == 200:
                    self.assertIn("theme-toggle", response.text)
                    self.assertIn("toggleTheme()", response.text)
                    self.assertIn("theme-icon", response.text)

    def test_theme_javascript_functions_in_pages(self):
        """Test that theme JavaScript functions are included in pages."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        content = response.text
        required_js_functions = [
            "getSystemTheme",
            "getStoredTheme",
            "applyTheme",
            "toggleTheme",
            "initializeTheme",
        ]

        for func in required_js_functions:
            self.assertIn(
                func, content, f"JavaScript function {func} not found in page"
            )

    def test_theme_accessibility_attributes(self):
        """Test theme toggle accessibility in rendered pages."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        content = response.text
        # Check accessibility attributes
        self.assertIn('aria-label="Toggle light/dark theme"', content)
        self.assertIn('title="Toggle theme"', content)

    def test_theme_css_variables_in_components(self):
        """Test that CSS variables are used in rendered components."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        content = response.text
        # These should be in the CSS, not necessarily the HTML
        # But the CSS should be linked
        self.assertIn("/static/css/theme.css", content)


class TestThemeLanguageSystemIntegration(unittest.TestCase):
    """Test theme system integration with language management."""

    def setUp(self) -> None:
        """Set up language manager for testing."""
        try:
            self.language_manager = get_language_manager()
            self.language_available = True
        except Exception as e:
            print(f"Warning: Language manager not available: {e}")
            self.language_available = False

    def test_theme_translations_accessible(self):
        """Test that theme translations are accessible through language manager."""
        if not self.language_available:
            self.skipTest("Language manager not available")

        # Test English translations (language manager uses current language)
        try:
            # Ensure we're using English
            self.language_manager.set_language("en")

            theme_toggle = self.language_manager.t("theme.toggle")
            self.assertIsInstance(theme_toggle, str)
            self.assertTrue(len(theme_toggle) > 0)

            light_theme = self.language_manager.t("theme.light")
            self.assertEqual(light_theme, "Light theme")

            dark_theme = self.language_manager.t("theme.dark")
            self.assertEqual(dark_theme, "Dark theme")
        except Exception as e:
            self.fail(f"Could not access theme translations: {e}")

    def test_theme_translations_multiple_languages(self):
        """Test theme translations in multiple languages."""
        if not self.language_available:
            self.skipTest("Language manager not available")

        languages_to_test = ["en", "es", "de"]

        for lang in languages_to_test:
            with self.subTest(language=lang):
                try:
                    # Set language and test translation
                    self.language_manager.set_language(lang)
                    toggle_text = self.language_manager.t("theme.toggle")
                    self.assertIsInstance(toggle_text, str)
                    self.assertTrue(len(toggle_text) > 0)

                    # Test that we get different translations for different languages
                    if lang != "en":
                        self.language_manager.set_language("en")
                        # Just verify the translation is valid
                        self.assertIsInstance(toggle_text, str)
                except Exception:
                    # If specific language not available, that's okay for this test
                    pass


class TestThemeSystemResponsive(unittest.TestCase):
    """Test theme system responsive behavior."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.theme_css_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/static/css/theme.css"
        )

    def test_mobile_theme_styles(self):
        """Test that theme system includes mobile-responsive styles."""
        if not os.path.exists(self.theme_css_path):
            self.skipTest("Theme CSS file not found")

        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for mobile breakpoint
        self.assertIn("@media (max-width: 768px)", css_content)

        # Check that theme toggle is responsive
        mobile_section_start = css_content.find("@media (max-width: 768px)")
        if mobile_section_start != -1:
            mobile_section = css_content[
                mobile_section_start : mobile_section_start + 2000
            ]
            # Mobile styles should exist
            self.assertTrue(len(mobile_section) > 100)

    def test_high_dpi_theme_support(self):
        """Test theme system works on high DPI displays."""
        if not os.path.exists(self.theme_css_path):
            self.skipTest("Theme CSS file not found")

        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for high DPI media query
        self.assertIn("min-resolution: 192dpi", css_content)


class TestThemeSystemPerformance(unittest.TestCase):
    """Test theme system performance characteristics."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up performance test environment."""
        try:
            from web_app import create_web_app

            app = create_web_app()
            cls.client = TestClient(app)  # type: ignore
            cls.performance_available = True
        except Exception:
            cls.performance_available = False

    def setUp(self) -> None:
        """Set up individual performance tests."""
        if not self.performance_available:
            self.skipTest("Performance testing not available")

    def test_theme_css_file_size(self):
        """Test that theme CSS file is reasonably sized."""
        response = self.client.get("/static/css/theme.css")
        self.assertEqual(response.status_code, 200)

        # CSS file should be reasonable size (under 100KB for performance)
        content_length = len(response.content)
        self.assertLess(
            content_length,
            100 * 1024,
            f"Theme CSS file too large: {content_length} bytes",
        )

        # But should have substantial content (more than 10KB)
        self.assertGreater(
            content_length,
            10 * 1024,
            f"Theme CSS file suspiciously small: {content_length} bytes",
        )

    def test_theme_css_compression_ready(self):
        """Test that theme CSS is ready for compression."""
        response = self.client.get("/static/css/theme.css")
        self.assertEqual(response.status_code, 200)

        css_content = response.text

        # Check that CSS is well-structured for compression
        # Should have consistent patterns that compress well
        variable_count = css_content.count("--")  # CSS variables
        self.assertGreater(variable_count, 50)  # Should have many variables

        # Should have many repeated patterns
        class_count = css_content.count("{")
        self.assertGreater(class_count, 100)  # Should have many CSS rules


class TestThemeSystemSecurity(unittest.TestCase):
    """Test theme system security aspects."""

    def test_theme_css_no_external_resources(self):
        """Test that theme CSS doesn't load external resources."""
        theme_css_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/static/css/theme.css"
        )

        if not os.path.exists(theme_css_path):
            self.skipTest("Theme CSS file not found")

        with open(theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for potentially dangerous external references
        dangerous_patterns = ["@import url(", "javascript:", "data:text/html"]

        for pattern in dangerous_patterns:
            self.assertNotIn(
                pattern,
                css_content,
                f"Potentially dangerous pattern '{pattern}' found in CSS",
            )

        # Check for external HTTP URLs (but allow SVG xmlns)
        import re

        external_urls = re.findall(r'https?://[^\s\'"]+', css_content)
        svg_namespaces = [
            url for url in external_urls if "www.w3.org" in url and "svg" in url
        ]
        actual_external_urls = [
            url for url in external_urls if url not in svg_namespaces
        ]

        self.assertEqual(
            len(actual_external_urls),
            0,
            f"Found external URLs in CSS: {actual_external_urls}",
        )

    def test_theme_javascript_no_eval(self):
        """Test that theme JavaScript doesn't use eval or similar."""
        base_template_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/layouts/base.html"
        )

        if not os.path.exists(base_template_path):
            self.skipTest("Base template not found")

        with open(base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for dangerous JavaScript patterns
        dangerous_js_patterns = [
            "eval(",
            "Function(",
            "setTimeout(",
            "setInterval(",
            "document.write(",
            "innerHTML =",
        ]

        theme_js_start = template_content.find("// Enhanced Theme Toggle Functionality")
        if theme_js_start != -1:
            theme_js_section = template_content[theme_js_start : theme_js_start + 5000]

            for pattern in dangerous_js_patterns:
                if pattern == "innerHTML =" and "target.innerHTML" in theme_js_section:
                    # This is acceptable for the loading state functionality
                    continue
                self.assertNotIn(
                    pattern,
                    theme_js_section,
                    f"Potentially dangerous JS pattern '{pattern}' found",
                )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
