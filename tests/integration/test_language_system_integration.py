"""
Integration tests for the language management system
Testing integration between LanguageManager, web application, and user workflows
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Import components to test
from language_manager import LanguageManager
from text_translator import TextTranslator
from web_app import create_web_app


class TestLanguageSystemIntegration:
    """Integration tests for the complete language management system"""

    @pytest.fixture
    def temp_languages_dir(self):
        """Create temporary directory for language files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def complete_english_data(self):
        """Complete English language data for testing"""
        return {
            "_metadata": {
                "language_code": "en",
                "language_name": "English",
                "native_name": "English",
                "version": "1.0.0",
                "author": "AI Prompt Manager",
                "created": "2025-01-06",
                "last_updated": "2025-01-06",
            },
            "app": {
                "title": "AI Prompt Manager",
                "subtitle": "Secure, multi-tenant AI prompt management",
                "status": {
                    "authenticated": "✅ Authenticated as {user}",
                    "not_authenticated": "❌ Not authenticated",
                },
            },
            "nav": {
                "home": "Home",
                "prompts": "Prompts",
                "builder": "Builder",
                "library": "Library",
                "tokens": "Tokens",
                "services": "Services",
                "settings": "Settings",
                "admin": "Admin",
            },
            "auth": {
                "login": "Login",
                "logout": "Logout",
                "email": "Email",
                "password": "Password",
                "tenant": "Tenant",
                "sso": "SSO Login",
                "welcome": "Welcome, {name}!",
                "invalid": "Invalid credentials",
                "signin": "Sign in to your account",
                "error": "Authentication error",
                "organization": "Organization",
                "organization_placeholder": "Organization subdomain",
                "organization_help": "Enter your organization subdomain (use 'localhost' for local development)",
                "email_placeholder": "you@example.com",
                "password_placeholder": "Enter your password",
                "remember_me": "Remember me",
                "forgot_password": "Forgot your password?",
                "login_button": "Sign In",
                "logout_confirm": "Are you sure you want to logout?",
                "required": "This field is required",
                "login_success": "Login successful",
                "logout_success": "Logout successful",
            },
            "settings": {
                "title": "Settings",
                "languages": "Languages",
                "current_language": "Current Language",
                "language_editor": "Language Editor",
                "new_language": "New Language",
                "edit_language": "Edit Language",
                "language_code": "Language Code",
                "language_name": "Language Name",
                "native_name": "Native Name",
                "author": "Author",
                "save_language": "Save Language",
                "translate_all": "Translate All",
                "missing_keys": "Missing Keys",
                "translate_key": "Translate This Key",
                "validating": "Validating...",
                "translating": "Translating...",
                "language_saved": "Language file saved successfully",
                "cannot_delete_default": "Cannot delete default language",
            },
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "back": "Back",
                "loading": "Loading...",
                "success": "Success",
                "error": "Error",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "english": "English",
                "reference": "Reference",
                "completed": "Completed",
                "total": "Total",
                "current": "Current",
                "switch": "Switch",
            },
            "errors": {
                "general": "An error occurred",
                "network": "Network error",
                "server": "Server error",
                "validation": "Validation error",
                "not_found": "Not found",
            },
        }

    @pytest.fixture
    def setup_test_languages(self, temp_languages_dir, complete_english_data):
        """Setup test language files"""
        # Create English file
        en_file = Path(temp_languages_dir) / "en.json"
        with open(en_file, "w", encoding="utf-8") as f:
            json.dump(complete_english_data, f, indent=2, ensure_ascii=False)

        # Create partial French file for testing
        french_data = {
            "_metadata": {
                "language_code": "fr",
                "language_name": "French",
                "native_name": "Français",
                "version": "1.0.0",
                "author": "AI Prompt Manager",
                "created": "2025-01-06",
                "last_updated": "2025-01-06",
            },
            "app": {
                "title": "Gestionnaire de Prompts IA",
                "subtitle": "Gestion sécurisée et multi-tenant de prompts IA",
            },
            "nav": {"home": "Accueil", "settings": "Paramètres"},
            "common": {"save": "Enregistrer", "cancel": "Annuler"},
        }

        fr_file = Path(temp_languages_dir) / "fr.json"
        with open(fr_file, "w", encoding="utf-8") as f:
            json.dump(french_data, f, indent=2, ensure_ascii=False)

        return temp_languages_dir

    @pytest.fixture
    def language_manager_with_data(self, setup_test_languages):
        """Create LanguageManager with test data"""
        return LanguageManager(
            languages_dir=str(setup_test_languages), default_language="en"
        )

    @pytest.fixture
    def web_app_client(self, language_manager_with_data):
        """Create test client for web application"""
        # Mock the global language manager
        with patch(
            "language_manager.get_language_manager",
            return_value=language_manager_with_data,
        ):
            with patch(
                "web_app.get_language_manager", return_value=language_manager_with_data
            ):
                app = create_web_app()
                return TestClient(app)

    def test_language_manager_web_app_integration(
        self, web_app_client, language_manager_with_data
    ):
        """Test integration between LanguageManager and web application"""
        # Test that language manager is properly integrated
        response = web_app_client.get("/")
        assert response.status_code in [200, 302]  # 302 for redirect to login

        # Test language switching via web interface
        response = web_app_client.post(
            "/settings/language/switch", json={"language": "fr"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        assert result["language"] == "fr"

    def test_language_creation_workflow(
        self, web_app_client, language_manager_with_data
    ):
        """Test complete language creation workflow"""
        # Step 1: Create new language template
        create_data = {
            "language_code": "de",
            "language_name": "German",
            "native_name": "Deutsch",
        }

        response = web_app_client.post("/settings/language/create", json=create_data)
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Step 2: Verify language was created
        available_languages = language_manager_with_data.get_available_languages()
        assert "de" in available_languages
        assert available_languages["de"]["name"] == "German"

        # Step 3: Test validation of new language (should have missing keys)
        response = web_app_client.post(
            "/settings/language/validate", json={"language_code": "de"}
        )
        assert response.status_code == 200

        validation = response.json()
        assert validation["success"] is True
        assert validation["data"]["valid"] is False  # Should have missing keys
        assert len(validation["data"]["missing_keys"]) > 0

    def test_language_editing_workflow(
        self, web_app_client, language_manager_with_data
    ):
        """Test language editing workflow"""
        # Step 1: Get current French translations
        response = web_app_client.get("/settings/language/fr")
        assert response.status_code == 200

        # Step 2: Update translations
        update_data = {
            "translations": {
                "app.title": "Nouveau Gestionnaire IA",
                "nav.home": "Accueil Mis à Jour",
            }
        }

        response = web_app_client.post(
            "/settings/language/save", json={"language_code": "fr", **update_data}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Step 3: Verify updates were applied
        language_manager_with_data.set_language("fr")
        assert language_manager_with_data.t("app.title") == "Nouveau Gestionnaire IA"
        assert language_manager_with_data.t("nav.home") == "Accueil Mis à Jour"

    def test_auto_translation_integration(
        self, web_app_client, language_manager_with_data
    ):
        """Test auto-translation feature integration"""
        # Mock text translator
        mock_translator = MagicMock(spec=TextTranslator)
        mock_translator.translate.return_value = ("Translated Text", True)

        with patch("text_translator.TextTranslator", return_value=mock_translator):
            # Test single key translation
            response = web_app_client.post(
                "/settings/language/translate-key",
                json={
                    "language_code": "fr",
                    "key": "settings.title",
                    "english_text": "Settings",
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["translated_text"] == "Translated Text"

            # Verify translator was called correctly
            mock_translator.translate.assert_called_once_with("Settings", "en", "fr")

    def test_language_validation_integration(
        self, web_app_client, language_manager_with_data
    ):
        """Test language validation integration"""
        # Test validation of existing language
        response = web_app_client.post(
            "/settings/language/validate", json={"language_code": "en"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        validation_data = result["data"]

        # English should be complete
        assert validation_data["valid"] is True
        assert validation_data["coverage"] == 100.0
        assert len(validation_data["missing_keys"]) == 0

        # Test validation of incomplete language
        response = web_app_client.post(
            "/settings/language/validate", json={"language_code": "fr"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        validation_data = result["data"]

        # French should be incomplete
        assert validation_data["valid"] is False
        assert validation_data["coverage"] < 100.0
        assert len(validation_data["missing_keys"]) > 0

    def test_language_deletion_workflow(
        self, web_app_client, language_manager_with_data
    ):
        """Test language deletion workflow"""
        # Verify French exists
        available = language_manager_with_data.get_available_languages()
        assert "fr" in available

        # Delete French language
        response = web_app_client.post(
            "/settings/language/delete", json={"language_code": "fr"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Verify deletion
        available = language_manager_with_data.get_available_languages()
        assert "fr" not in available

        # Try to delete default language (should fail)
        response = web_app_client.post(
            "/settings/language/delete", json={"language_code": "en"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is False
        assert "default" in result["message"].lower()

    def test_concurrent_language_operations(self, language_manager_with_data):
        """Test concurrent language operations"""
        import threading
        import time

        results = []
        errors = []

        def worker_thread(thread_id):
            try:
                manager = language_manager_with_data

                # Mix of operations
                if thread_id % 2 == 0:
                    # Translation operations
                    manager.set_language("fr")
                    text = manager.t("app.title")
                    results.append(f"Thread {thread_id}: {text}")
                else:
                    # Validation operations
                    validation = manager.validate_language_file("fr")
                    results.append(
                        f"Thread {thread_id}: coverage={validation['coverage']}"
                    )

                time.sleep(0.1)  # Simulate work

            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

        # Create multiple worker threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10

    def test_language_persistence(self, language_manager_with_data):
        """Test language file persistence"""
        # Create new language
        translations = {"app": {"title": "Test App"}, "nav": {"home": "Test Home"}}

        metadata = {"language_name": "Test Language", "native_name": "Test Native"}

        # Save language
        result = language_manager_with_data.save_language_file(
            "test", translations, metadata
        )
        assert result is True

        # Create new manager instance to test persistence
        new_manager = LanguageManager(
            languages_dir=str(language_manager_with_data.languages_dir),
            default_language="en",
        )

        # Verify language persisted
        available = new_manager.get_available_languages()
        assert "test" in available
        assert available["test"]["name"] == "Test Language"

        # Verify translations work
        new_manager.set_language("test")
        assert new_manager.t("app.title") == "Test App"

    def test_language_template_generation(self, language_manager_with_data):
        """Test language template generation"""
        # Generate template for new language
        template = language_manager_with_data.create_language_template(
            "es", "Spanish", "Español", "Test Author"
        )

        assert "translations" in template
        assert "metadata" in template

        # Verify structure matches English
        en_keys = language_manager_with_data.get_all_translation_keys("en")
        template_structure = language_manager_with_data._flatten_keys(
            template["translations"]
        )

        # Template should have same structure as English (but empty values)
        assert en_keys == template_structure

        # All values should be empty
        def check_empty_values(data):
            for key, value in data.items():
                if isinstance(value, dict):
                    check_empty_values(value)
                else:
                    assert value == "", f"Non-empty value found: {key}={value}"

        check_empty_values(template["translations"])

    def test_error_handling_integration(self, web_app_client):
        """Test error handling in web integration"""
        # Test invalid language code
        response = web_app_client.post(
            "/settings/language/switch", json={"language": "invalid"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is False

        # Test malformed request
        response = web_app_client.post(
            "/settings/language/create", json={"invalid": "data"}
        )
        assert response.status_code == 422 or response.status_code == 400

        # Test non-existent language validation
        response = web_app_client.post(
            "/settings/language/validate", json={"language_code": "nonexistent"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        assert result["data"]["coverage"] == 0.0

    def test_language_system_performance(self, language_manager_with_data):
        """Test performance of language system operations"""
        import time

        # Test translation performance
        start_time = time.time()
        for i in range(1000):
            text = language_manager_with_data.t("app.title")
            assert text == "AI Prompt Manager"
        translation_time = time.time() - start_time

        # Should be fast (less than 1 second for 1000 translations)
        assert translation_time < 1.0, f"Translation too slow: {translation_time}s"

        # Test language switching performance
        start_time = time.time()
        for i in range(100):
            language_manager_with_data.set_language("fr" if i % 2 == 0 else "en")
        switch_time = time.time() - start_time

        # Should be reasonably fast
        assert switch_time < 2.0, f"Language switching too slow: {switch_time}s"

    def test_memory_usage_stability(self, language_manager_with_data):
        """Test memory usage remains stable during operations"""
        import gc

        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many operations
        for i in range(100):
            # Switch languages
            language_manager_with_data.set_language("fr" if i % 2 == 0 else "en")

            # Translate text
            text = language_manager_with_data.t("app.title")
            assert text  # Ensure translation works

            # Validate languages
            validation = language_manager_with_data.validate_language_file("fr")
            assert validation is not None  # Ensure validation runs

            # Get stats
            stats = language_manager_with_data.get_language_stats()
            assert stats  # Ensure stats are returned

        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory usage should not grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Too many objects created: {object_growth}"


class TestLanguageSystemEdgeCases:
    """Test edge cases and error conditions"""

    def test_corrupted_language_file_handling(self, temp_languages_dir):
        """Test handling of corrupted language files"""
        # Create corrupted file
        corrupted_file = Path(temp_languages_dir) / "corrupted.json"
        with open(corrupted_file, "w") as f:
            f.write('{"incomplete": "json"')  # Missing closing brace

        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        # Should handle gracefully
        available = manager.get_available_languages()
        assert "corrupted" not in available

    def test_empty_language_directory(self):
        """Test behavior with empty language directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LanguageManager(languages_dir=temp_dir, default_language="en")

            # Should handle empty directory gracefully
            available = manager.get_available_languages()
            assert len(available) == 0

            # Translation should return key when no languages available
            text = manager.t("app.title")
            assert text == "app.title"

    def test_very_large_translation_keys(self, language_manager_with_data):
        """Test handling of very large translation keys"""
        # Create very long key
        long_key = (
            "very.long.nested.key.that.goes.on.and.on.with.many.levels.of.nesting"
        )

        # Should handle gracefully
        text = language_manager_with_data.t(long_key)
        assert text == long_key  # Should return key when not found

    def test_unicode_handling(self, language_manager_with_data):
        """Test proper Unicode handling in translations"""
        # Test with emoji and various Unicode characters
        test_translations = {
            "unicode": {
                "emoji": "🚀 Rocket Launch",
                "chinese": "中文测试",
                "arabic": "اختبار عربي",
                "mixed": "Mixed: 中文 + العربية + 🎉",
            }
        }

        # Save with Unicode content
        result = language_manager_with_data.save_language_file(
            "unicode_test", test_translations
        )
        assert result is True

        # Verify Unicode is preserved
        language_manager_with_data.set_language("unicode_test")
        assert language_manager_with_data.t("unicode.emoji") == "🚀 Rocket Launch"
        assert language_manager_with_data.t("unicode.chinese") == "中文测试"
        assert language_manager_with_data.t("unicode.arabic") == "اختبار عربي"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
