#!/usr/bin/env python3
"""
Unit test for LanguageManager.t empty-string fallback.

An empty-string translation is an untranslated placeholder. It must trigger
the same default-language fallback as a missing key, rather than rendering a
blank string in the UI.
"""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from language_manager import LanguageManager  # noqa: E402


class TestEmptyTranslationFallback(unittest.TestCase):
    def setUp(self):
        self.lm = LanguageManager(default_language="en")
        # Inject a controlled language state.
        self.lm._loaded_languages["en"] = {"greeting": "Hello"}
        self.lm._loaded_languages["xx"] = {"greeting": ""}  # untranslated
        self.lm.current_language = "xx"

    def test_empty_translation_falls_back_to_default(self):
        self.assertEqual(self.lm.t("greeting"), "Hello")

    def test_present_translation_is_used(self):
        self.lm._loaded_languages["xx"]["greeting"] = "Bonjour"
        self.assertEqual(self.lm.t("greeting"), "Bonjour")

    def test_missing_everywhere_returns_key(self):
        self.assertEqual(self.lm.t("no.such.key"), "no.such.key")


if __name__ == "__main__":
    unittest.main()
