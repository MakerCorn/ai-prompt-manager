#!/usr/bin/env python3
"""
Unit tests for ModelHealthChecker._ollama_tags_url.

The old implementation used ``rstrip('/api/generate')`` which strips a set of
characters, mangling hosts that end in one of them. These tests lock in the
correct suffix-based derivation.
"""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.core.services.ai_model_manager import ModelHealthChecker  # noqa: E402


class TestOllamaTagsUrl(unittest.TestCase):
    def test_standard_endpoint(self):
        self.assertEqual(
            ModelHealthChecker._ollama_tags_url("http://localhost:11434/api/generate"),
            "http://localhost:11434/api/tags",
        )

    def test_host_ending_in_stripped_char_not_mangled(self):
        """A host ending in a char of '/apigenerate' must not be truncated."""
        # 'server' ends in 'r'/'e' which rstrip('/api/generate') would strip.
        self.assertEqual(
            ModelHealthChecker._ollama_tags_url("http://ollama-server/api/generate"),
            "http://ollama-server/api/tags",
        )

    def test_base_endpoint_without_suffix(self):
        self.assertEqual(
            ModelHealthChecker._ollama_tags_url("http://ollama-server"),
            "http://ollama-server/api/tags",
        )


if __name__ == "__main__":
    unittest.main()
