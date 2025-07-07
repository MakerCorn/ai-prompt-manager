"""
Unit tests for the theme system functionality.
Tests theme toggle logic, CSS variable application, and system preference detection.
"""

import json
import os
import unittest


class TestThemeSystem(unittest.TestCase):
    """Test cases for theme system functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.theme_css_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/static/css/theme.css"
        )
        self.base_template_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/layouts/base.html"
        )

    def test_theme_css_contains_required_variables(self):
        """Test that theme.css contains all required CSS variables."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Test light theme variables
        light_theme_vars = [
            "--surface-primary",
            "--surface-secondary",
            "--surface-tertiary",
            "--text-primary",
            "--text-secondary",
            "--text-tertiary",
            "--border-light",
            "--border-medium",
            "--border-dark",
        ]

        for var in light_theme_vars:
            self.assertIn(
                var, css_content, f"CSS variable {var} not found in theme.css"
            )

    def test_dark_theme_variables_defined(self):
        """Test that dark theme CSS variables are properly defined."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for dark theme selector
        self.assertIn(':root[data-theme="dark"]', css_content)

        # Check for system preference fallback
        self.assertIn("@media (prefers-color-scheme: dark)", css_content)

    def test_theme_toggle_button_in_base_template(self):
        """Test that theme toggle button is present in base template."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for theme toggle button
        self.assertIn("theme-toggle", template_content)
        self.assertIn('onclick="toggleTheme()"', template_content)
        self.assertIn('id="theme-toggle"', template_content)
        self.assertIn('id="theme-icon"', template_content)

    def test_theme_javascript_functions_present(self):
        """Test that all required JavaScript functions are present."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        required_functions = [
            "function getSystemTheme()",
            "function getStoredTheme()",
            "function setStoredTheme(",
            "function updateThemeIcon(",
            "function applyTheme(",
            "function toggleTheme()",
            "function initializeTheme()",
        ]

        for func in required_functions:
            self.assertIn(
                func, template_content, f"JavaScript function {func} not found"
            )

    def test_theme_css_classes_defined(self):
        """Test that theme-aware CSS classes are defined."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        theme_classes = [
            ".theme-toggle",
            ".text-primary",
            ".text-secondary",
            ".text-tertiary",
            ".bg-primary",
            ".bg-secondary",
            ".border-light",
        ]

        for css_class in theme_classes:
            self.assertIn(css_class, css_content, f"CSS class {css_class} not found")

    def test_transition_properties_defined(self):
        """Test that theme transition properties are defined."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for transition variables
        self.assertIn("--transition-theme:", css_content)

        # Check that body has transition for smooth theme switching
        self.assertIn(
            "transition: background-color var(--transition-theme)", css_content
        )

    def test_accessibility_attributes(self):
        """Test that theme toggle has proper accessibility attributes."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for accessibility attributes
        self.assertIn('aria-label="Toggle light/dark theme"', template_content)
        self.assertIn('title="Toggle theme"', template_content)

    def test_theme_persistence_logic(self):
        """Test theme persistence localStorage logic."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for localStorage usage
        self.assertIn("localStorage.getItem('theme')", template_content)
        self.assertIn("localStorage.setItem('theme'", template_content)

    def test_system_preference_detection(self):
        """Test system preference detection logic."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for media query detection
        self.assertIn(
            "window.matchMedia('(prefers-color-scheme: dark)')", template_content
        )
        self.assertIn(".addEventListener('change'", template_content)

    def test_theme_cycling_logic(self):
        """Test that theme cycling follows the correct order."""
        with open(self.base_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check for theme cycling logic
        self.assertIn("case 'light':", template_content)
        self.assertIn("nextTheme = 'dark';", template_content)
        self.assertIn("case 'dark':", template_content)
        self.assertIn("nextTheme = 'system';", template_content)
        self.assertIn("case 'system':", template_content)
        self.assertIn("nextTheme = 'light';", template_content)


class TestThemeLanguageIntegration(unittest.TestCase):
    """Test theme integration with language system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.languages_dir = os.path.join(os.path.dirname(__file__), "../../languages")

    def test_all_languages_have_theme_keys(self):
        """Test that all language files contain theme translation keys."""
        language_files = [
            "ar.json",
            "de.json",
            "en.json",
            "es.json",
            "hi.json",
            "ja.json",
            "pt.json",
            "ru.json",
            "zh.json",
        ]

        required_theme_keys = [
            "toggle",
            "light",
            "dark",
            "system",
            "switch_to_light",
            "switch_to_dark",
            "switch_to_system",
            "switched_to_light",
            "switched_to_dark",
            "switched_to_system",
            "preference",
            "follows_system",
            "always_light",
            "always_dark",
            "description",
            "auto_detect",
        ]

        for lang_file in language_files:
            lang_path = os.path.join(self.languages_dir, lang_file)
            if os.path.exists(lang_path):
                with open(lang_path, "r", encoding="utf-8") as f:
                    lang_data = json.load(f)

                # Check if theme section exists
                self.assertIn(
                    "theme", lang_data, f"Theme section missing in {lang_file}"
                )

                # Check all required keys
                theme_section = lang_data["theme"]
                for key in required_theme_keys:
                    self.assertIn(
                        key, theme_section, f"Theme key '{key}' missing in {lang_file}"
                    )
                    self.assertTrue(
                        theme_section[key].strip(),
                        f"Theme key '{key}' is empty in {lang_file}",
                    )

    def test_theme_translations_not_empty(self):
        """Test that theme translations are not empty strings."""
        language_files = ["en.json", "es.json", "de.json"]  # Test subset for efficiency

        for lang_file in language_files:
            lang_path = os.path.join(self.languages_dir, lang_file)
            if os.path.exists(lang_path):
                with open(lang_path, "r", encoding="utf-8") as f:
                    lang_data = json.load(f)

                if "theme" in lang_data:
                    for key, value in lang_data["theme"].items():
                        self.assertIsInstance(
                            value,
                            str,
                            f"Theme key '{key}' should be string in {lang_file}",
                        )
                        self.assertTrue(
                            len(value.strip()) > 0,
                            f"Theme key '{key}' should not be empty in {lang_file}",
                        )

    def test_language_files_valid_json(self):
        """Test that all language files are valid JSON."""
        language_files = [
            "ar.json",
            "de.json",
            "en.json",
            "es.json",
            "hi.json",
            "ja.json",
            "pt.json",
            "ru.json",
            "zh.json",
        ]

        for lang_file in language_files:
            lang_path = os.path.join(self.languages_dir, lang_file)
            if os.path.exists(lang_path):
                with open(lang_path, "r", encoding="utf-8") as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in {lang_file}: {e}")


class TestThemeSystemCSS(unittest.TestCase):
    """Test theme system CSS functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.theme_css_path = os.path.join(
            os.path.dirname(__file__), "../../web_templates/static/css/theme.css"
        )

    def test_css_color_scheme_properties(self):
        """Test CSS color-scheme properties for proper rendering."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for color-scheme declarations
        self.assertIn("color-scheme: light;", css_content)
        self.assertIn("color-scheme: dark;", css_content)

    def test_theme_toggle_button_styles(self):
        """Test that theme toggle button has proper styling."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check theme toggle styles
        self.assertIn(".theme-toggle {", css_content)
        self.assertIn(".theme-toggle:hover", css_content)
        self.assertIn(".theme-icon", css_content)

    def test_responsive_theme_support(self):
        """Test that theme system works on mobile devices."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check for mobile responsive styles
        self.assertIn("@media (max-width: 768px)", css_content)

    def test_print_styles_theme_aware(self):
        """Test that print styles handle theme properly."""
        with open(self.theme_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check print media styles
        self.assertIn("@media print", css_content)
        self.assertIn(".theme-toggle", css_content)
        self.assertIn("display: none !important", css_content)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
