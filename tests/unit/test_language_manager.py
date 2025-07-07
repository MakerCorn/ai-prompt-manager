"""
Comprehensive unit tests for LanguageManager class
Testing file-based internationalization, dynamic loading, validation, and translation
"""

import json
import os
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from language_manager import (
    LanguageManager,
    get_available_languages,
    get_language_manager,
    set_language,
    t,
)


class TestLanguageManager:
    """Test suite for LanguageManager functionality"""

    @pytest.fixture
    def temp_languages_dir(self):
        """Create temporary directory for language files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_english_data(self):
        """Sample English language data"""
        return {
            "_metadata": {
                "language_code": "en",
                "language_name": "English",
                "native_name": "English",
                "version": "1.0.0",
                "author": "Test Author",
                "created": "2025-01-06",
                "last_updated": "2025-01-06",
            },
            "app": {
                "title": "AI Prompt Manager",
                "subtitle": "Secure AI prompt management",
                "status": {
                    "authenticated": "✅ Authenticated as {user}",
                    "not_authenticated": "❌ Not authenticated",
                },
            },
            "nav": {"home": "Home", "settings": "Settings"},
            "auth": {
                "login": "Login",
                "logout": "Logout",
                "welcome": "Welcome, {name}!",
            },
            "common": {"save": "Save", "cancel": "Cancel", "loading": "Loading..."},
        }

    @pytest.fixture
    def sample_french_data(self):
        """Sample French language data"""
        return {
            "_metadata": {
                "language_code": "fr",
                "language_name": "French",
                "native_name": "Français",
                "version": "1.0.0",
                "author": "Test Author",
                "created": "2025-01-06",
                "last_updated": "2025-01-06",
            },
            "app": {
                "title": "Gestionnaire de Prompts IA",
                "subtitle": "Gestion sécurisée de prompts IA",
                "status": {
                    "authenticated": "✅ Authentifié en tant que {user}",
                    "not_authenticated": "❌ Non authentifié",
                },
            },
            "nav": {"home": "Accueil", "settings": "Paramètres"},
            "auth": {
                "login": "Connexion",
                "logout": "Déconnexion",
                "welcome": "Bienvenue, {name}!",
            },
            "common": {
                "save": "Enregistrer",
                "cancel": "Annuler",
                # Missing "loading" key for testing validation
            },
        }

    @pytest.fixture
    def language_manager(
        self, temp_languages_dir, sample_english_data, sample_french_data
    ):
        """Create LanguageManager instance with sample data"""
        # Create language files
        en_file = Path(temp_languages_dir) / "en.json"
        fr_file = Path(temp_languages_dir) / "fr.json"

        with open(en_file, "w", encoding="utf-8") as f:
            json.dump(sample_english_data, f, indent=2, ensure_ascii=False)

        with open(fr_file, "w", encoding="utf-8") as f:
            json.dump(sample_french_data, f, indent=2, ensure_ascii=False)

        return LanguageManager(
            languages_dir=str(temp_languages_dir), default_language="en"
        )

    def test_initialization(self, temp_languages_dir):
        """Test LanguageManager initialization"""
        manager = LanguageManager(
            languages_dir=str(temp_languages_dir), default_language="en"
        )

        assert manager.languages_dir == Path(temp_languages_dir)
        assert manager.default_language == "en"
        assert manager.current_language == "en"
        assert isinstance(manager._loaded_languages, dict)
        assert isinstance(manager._available_languages, dict)
        assert isinstance(manager._language_cache_lock, type(threading.RLock()))

    def test_discover_available_languages(self, language_manager):
        """Test discovery of available language files"""
        available = language_manager.get_available_languages()

        assert "en" in available
        assert "fr" in available
        assert available["en"]["name"] == "English"
        assert available["en"]["native_name"] == "English"
        assert available["fr"]["name"] == "French"
        assert available["fr"]["native_name"] == "Français"

    def test_load_language_success(self, language_manager):
        """Test successful language loading"""
        # English should be loaded by default
        assert "en" in language_manager._loaded_languages

        # Load French
        result = language_manager._load_language("fr")
        assert result is True
        assert "fr" in language_manager._loaded_languages

        # Verify French translations
        fr_translations = language_manager._loaded_languages["fr"]
        assert fr_translations["app"]["title"] == "Gestionnaire de Prompts IA"
        assert "_metadata" not in fr_translations  # Metadata should be removed

    def test_load_language_nonexistent(self, language_manager):
        """Test loading non-existent language"""
        result = language_manager._load_language("de")
        assert result is False
        assert "de" not in language_manager._loaded_languages

    def test_load_language_thread_safety(self, language_manager):
        """Test thread-safe language loading"""
        results = []
        errors = []

        def load_language_thread():
            try:
                result = language_manager._load_language("fr")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads trying to load the same language
        threads = [threading.Thread(target=load_language_thread) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert all(results)  # All should succeed
        assert "fr" in language_manager._loaded_languages

    def test_set_language_success(self, language_manager):
        """Test successful language switching"""
        # Switch to French
        result = language_manager.set_language("fr")
        assert result is True
        assert language_manager.current_language == "fr"

        # Switch back to English
        result = language_manager.set_language("en")
        assert result is True
        assert language_manager.current_language == "en"

    def test_set_language_same_language(self, language_manager):
        """Test setting the same language (should succeed without loading)"""
        initial_loaded = len(language_manager._loaded_languages)
        result = language_manager.set_language("en")  # Already current

        assert result is True
        assert language_manager.current_language == "en"
        assert len(language_manager._loaded_languages) == initial_loaded

    def test_set_language_nonexistent(self, language_manager):
        """Test setting non-existent language"""
        result = language_manager.set_language("de")
        assert result is False
        assert language_manager.current_language == "en"  # Should remain unchanged

    def test_get_nested_value_simple(self, language_manager):
        """Test getting simple nested values"""
        language_manager._load_language("en")
        translations = language_manager._loaded_languages["en"]

        # Simple key
        result = language_manager._get_nested_value(translations, "app.title")
        assert result == "AI Prompt Manager"

        # Nested key
        result = language_manager._get_nested_value(
            translations, "app.status.authenticated"
        )
        assert result == "✅ Authenticated as {user}"

    def test_get_nested_value_nonexistent(self, language_manager):
        """Test getting non-existent nested values"""
        language_manager._load_language("en")
        translations = language_manager._loaded_languages["en"]

        # Non-existent key
        result = language_manager._get_nested_value(translations, "nonexistent.key")
        assert result is None

        # Partially non-existent key
        result = language_manager._get_nested_value(translations, "app.nonexistent")
        assert result is None

    def test_translation_current_language(self, language_manager):
        """Test translation in current language"""
        # Test English (default)
        result = language_manager.t("app.title")
        assert result == "AI Prompt Manager"

        # Switch to French and test
        language_manager.set_language("fr")
        result = language_manager.t("app.title")
        assert result == "Gestionnaire de Prompts IA"

    def test_translation_with_formatting(self, language_manager):
        """Test translation with parameter formatting"""
        result = language_manager.t("auth.welcome", name="John")
        assert result == "Welcome, John!"

        # Test with multiple parameters
        result = language_manager.t("app.status.authenticated", user="admin@test.com")
        assert result == "✅ Authenticated as admin@test.com"

    def test_translation_fallback_to_default(self, language_manager):
        """Test fallback to default language for missing keys"""
        language_manager.set_language("fr")

        # "common.loading" exists in English but missing in French
        result = language_manager.t("common.loading")
        assert result == "Loading..."  # Should fallback to English

    def test_translation_key_not_found(self, language_manager):
        """Test translation when key doesn't exist in any language"""
        result = language_manager.t("nonexistent.key")
        assert result == "nonexistent.key"  # Should return the key itself

    def test_translation_formatting_error(self, language_manager):
        """Test translation with formatting errors"""
        # Missing required parameter
        result = language_manager.t("auth.welcome")  # Missing 'name' parameter
        assert "Welcome" in result  # Should still return text, unformatted

        # Invalid parameter
        result = language_manager.t("auth.welcome", invalid_param="test")
        assert "Welcome" in result  # Should handle gracefully

    def test_get_all_translation_keys(self, language_manager):
        """Test getting all translation keys"""
        keys = language_manager.get_all_translation_keys("en")

        expected_keys = {
            "app.title",
            "app.subtitle",
            "app.status.authenticated",
            "app.status.not_authenticated",
            "nav.home",
            "nav.settings",
            "auth.login",
            "auth.logout",
            "auth.welcome",
            "common.save",
            "common.cancel",
            "common.loading",
        }

        assert expected_keys.issubset(keys)
        assert len(keys) >= len(expected_keys)

    def test_flatten_keys(self, language_manager):
        """Test key flattening functionality"""
        test_data = {
            "level1": {"level2": {"key": "value"}, "simple": "value"},
            "root": "value",
        }

        keys = language_manager._flatten_keys(test_data)
        expected = {"level1.level2.key", "level1.simple", "root"}

        assert keys == expected

    def test_validate_language_file_complete(self, language_manager):
        """Test validation of complete language file"""
        validation = language_manager.validate_language_file("en")

        assert validation["valid"] is True
        assert len(validation["missing_keys"]) == 0
        assert validation["coverage"] == 100.0
        assert validation["total_keys"] > 0
        assert validation["covered_keys"] == validation["total_keys"]

    def test_validate_language_file_incomplete(self, language_manager):
        """Test validation of incomplete language file"""
        validation = language_manager.validate_language_file("fr")

        assert validation["valid"] is False
        assert len(validation["missing_keys"]) > 0
        assert "common.loading" in validation["missing_keys"]
        assert validation["coverage"] < 100.0
        assert validation["covered_keys"] < validation["total_keys"]

    def test_validate_language_file_nonexistent(self, language_manager):
        """Test validation of non-existent language file"""
        validation = language_manager.validate_language_file("de")

        assert validation["valid"] is False
        assert validation["coverage"] == 0.0
        assert validation["covered_keys"] == 0

    def test_save_language_file_new(self, language_manager):
        """Test saving new language file"""
        translations = {
            "app": {
                "title": "Verwalter für KI-Prompts",
                "subtitle": "Sichere KI-Prompt-Verwaltung",
            },
            "nav": {"home": "Startseite", "settings": "Einstellungen"},
        }

        metadata = {
            "language_name": "German",
            "native_name": "Deutsch",
            "author": "Test User",
        }

        result = language_manager.save_language_file("de", translations, metadata)
        assert result is True

        # Verify file was created and is discoverable
        available = language_manager.get_available_languages()
        assert "de" in available
        assert available["de"]["name"] == "German"
        assert available["de"]["native_name"] == "Deutsch"

    def test_save_language_file_update_existing(self, language_manager):
        """Test updating existing language file"""
        # Update French translations
        updated_translations = {
            "app": {"title": "Nouveau Titre", "subtitle": "Nouveau Sous-titre"}
        }

        result = language_manager.save_language_file("fr", updated_translations)
        assert result is True

        # Verify update
        language_manager._load_language("fr")
        fr_translations = language_manager._loaded_languages["fr"]
        assert fr_translations["app"]["title"] == "Nouveau Titre"

    def test_create_language_template(self, language_manager):
        """Test creating language template"""
        template = language_manager.create_language_template(
            "de", "German", "Deutsch", "Test Author"
        )

        assert "translations" in template
        assert "metadata" in template

        # Verify metadata
        metadata = template["metadata"]
        assert metadata["language_code"] == "de"
        assert metadata["language_name"] == "German"
        assert metadata["native_name"] == "Deutsch"
        assert metadata["author"] == "Test Author"

        # Verify structure matches default language
        translations = template["translations"]
        assert "app" in translations
        assert "nav" in translations
        assert "auth" in translations
        assert "common" in translations

        # All values should be empty strings
        assert translations["app"]["title"] == ""
        assert translations["nav"]["home"] == ""

    def test_create_empty_structure(self, language_manager):
        """Test creating empty structure"""
        test_data = {
            "level1": {"level2": {"key": "value"}, "simple": "value"},
            "root": "value",
        }

        empty = language_manager._create_empty_structure(test_data)

        assert empty["level1"]["level2"]["key"] == ""
        assert empty["level1"]["simple"] == ""
        assert empty["root"] == ""

    def test_delete_language_file_success(self, language_manager):
        """Test successful language file deletion"""
        # Ensure French file exists
        assert "fr" in language_manager.get_available_languages()

        result = language_manager.delete_language_file("fr")
        assert result is True

        # Verify deletion
        available = language_manager.get_available_languages()
        assert "fr" not in available

    def test_delete_language_file_default(self, language_manager):
        """Test deletion of default language (should fail)"""
        result = language_manager.delete_language_file("en")
        assert result is False

        # English should still be available
        assert "en" in language_manager.get_available_languages()

    def test_delete_language_file_current(self, language_manager):
        """Test deletion of current language"""
        # Switch to French
        language_manager.set_language("fr")
        assert language_manager.current_language == "fr"

        # Delete French
        result = language_manager.delete_language_file("fr")
        assert result is True

        # Should switch back to default
        assert language_manager.current_language == "en"

    def test_reload_languages(self, language_manager):
        """Test reloading all languages"""
        # Load some languages
        language_manager._load_language("fr")
        initial_loaded = len(language_manager._loaded_languages)

        # Clear cache and reload
        language_manager.reload_languages()

        # Should have at least default language loaded
        assert len(language_manager._loaded_languages) >= 1
        # Verify reload actually cleared and reloaded languages
        assert len(language_manager._loaded_languages) <= initial_loaded
        assert language_manager.current_language == "en"

    def test_get_language_stats(self, language_manager):
        """Test getting language statistics"""
        stats = language_manager.get_language_stats()

        assert "total_available" in stats
        assert "total_loaded" in stats
        assert "current_language" in stats
        assert "default_language" in stats
        assert "languages" in stats

        assert stats["current_language"] == "en"
        assert stats["default_language"] == "en"
        assert stats["total_available"] >= 2  # en, fr

        # Check per-language stats
        lang_stats = stats["languages"]
        assert "en" in lang_stats
        assert "fr" in lang_stats

        en_stats = lang_stats["en"]
        assert "loaded" in en_stats
        assert "coverage" in en_stats
        assert "total_keys" in en_stats
        assert "missing_keys" in en_stats

        assert en_stats["coverage"] == 100.0  # English should be complete

    def test_malformed_json_handling(self, temp_languages_dir):
        """Test handling of malformed JSON files"""
        # Create malformed JSON file
        bad_file = Path(temp_languages_dir) / "bad.json"
        with open(bad_file, "w") as f:
            f.write("{ invalid json")

        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        # Should not crash, just skip the bad file
        available = manager.get_available_languages()
        assert "bad" not in available

    def test_missing_metadata_handling(self, temp_languages_dir):
        """Test handling of files missing metadata"""
        # Create file without metadata
        no_meta_data = {"app": {"title": "Test App"}}

        no_meta_file = Path(temp_languages_dir) / "nometa.json"
        with open(no_meta_file, "w") as f:
            json.dump(no_meta_data, f)

        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        available = manager.get_available_languages()
        assert "nometa" in available
        # Should use defaults
        assert available["nometa"]["name"] == "NOMETA"
        assert available["nometa"]["native_name"] == "NOMETA"


class TestGlobalFunctions:
    """Test global convenience functions"""

    @pytest.fixture(autouse=True)
    def reset_global_manager(self):
        """Reset global manager before each test"""
        import language_manager

        language_manager._language_manager = None
        yield
        language_manager._language_manager = None

    def test_get_language_manager_singleton(self):
        """Test singleton behavior of get_language_manager"""
        manager1 = get_language_manager()
        manager2 = get_language_manager()

        assert manager1 is manager2  # Same instance

    def test_convenience_functions(self):
        """Test convenience functions"""
        # Test translation function
        result = t("app.title")
        assert isinstance(result, str)

        # Test set language function
        result = set_language("en")
        assert isinstance(result, bool)

        # Test get available languages function
        result = get_available_languages()
        assert isinstance(result, dict)

    @patch.dict(os.environ, {"DEFAULT_LANGUAGE": "fr"})
    def test_default_language_from_env(self):
        """Test setting default language from environment"""
        manager = get_language_manager()
        assert manager.default_language == "fr"

    def test_thread_safety_global_manager(self):
        """Test thread safety of global manager creation"""
        managers = []
        errors = []

        def get_manager_thread():
            try:
                manager = get_language_manager()
                managers.append(manager)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=get_manager_thread) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(managers) == 10
        # All should be the same instance
        assert all(manager is managers[0] for manager in managers)


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def temp_languages_dir(self):
        """Create temporary directory for language files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_permission_error_handling(self, temp_languages_dir):
        """Test handling of permission errors"""
        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        # Mock file operations to raise permission error
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = manager.save_language_file("test", {"app": {"title": "Test"}})
            assert result is False

    def test_disk_full_error_handling(self, temp_languages_dir):
        """Test handling of disk full errors"""
        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        # Mock file operations to raise OSError (disk full)
        with patch("builtins.open", side_effect=OSError("No space left on device")):
            result = manager.save_language_file("test", {"app": {"title": "Test"}})
            assert result is False

    def test_concurrent_access_handling(self, temp_languages_dir):
        """Test handling of concurrent file access"""
        # Create a simple language manager for this test
        manager = LanguageManager(languages_dir=str(temp_languages_dir))

        results = []
        errors = []

        def concurrent_operation():
            try:
                # Mix of read and write operations
                manager.set_language("en")
                stats = manager.get_language_stats()
                validation = manager.validate_language_file("en")
                results.append((stats, validation))
            except Exception as e:
                errors.append(e)

        # Create multiple threads with concurrent operations
        threads = [threading.Thread(target=concurrent_operation) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
