#!/usr/bin/env python3
"""
Unit tests for speech dictation functionality
Testing text enhancement and speech-related utility functions
"""

import os
import sys
import unittest

# Add the project root to the path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from web_app import basic_text_enhancement  # noqa: E402


class TestSpeechDictation(unittest.TestCase):
    """Test suite for speech dictation functionality"""

    def setUp(self):
        """Set up test environment"""
        pass

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_basic_text_enhancement_simple(self):
        """Test basic text enhancement with simple text"""
        input_text = "hello world this is a test"
        expected = "Hello world this is a test."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_with_filler_words(self):
        """Test removal of common filler words"""
        input_text = "um hello uh world you know this is actually a test"
        expected = "Hello world this is a test."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_duplicate_words(self):
        """Test removal of duplicate words"""
        input_text = "hello hello world world test test"
        expected = "Hello world test."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_capitalization(self):
        """Test proper sentence capitalization"""
        input_text = "first sentence. second sentence. third sentence"
        expected = "First sentence. Second sentence. Third sentence."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_whitespace(self):
        """Test whitespace normalization"""
        input_text = "hello    world   with    extra    spaces"
        expected = "Hello world with extra spaces."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_punctuation_cleanup(self):
        """Test cleanup of excessive punctuation"""
        input_text = "hello world... with too many dots,, and commas"
        expected = "Hello world. With too many dots, and commas."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_already_punctuated(self):
        """Test text that already ends with punctuation"""
        input_text = "hello world!"
        expected = "Hello world!"
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_empty_text(self):
        """Test enhancement with empty text"""
        input_text = ""
        expected = ""
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_only_filler_words(self):
        """Test text with only filler words"""
        input_text = "um uh you know like basically"
        expected = ""
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_complex_text(self):
        """Test enhancement with complex dictated text"""
        input_text = (
            "um so basically I want to create a prompt that will help me "
            "write better emails you know"
        )
        expected = "I want to create a prompt that will help me write better emails."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_preserves_meaning(self):
        """Test that enhancement preserves the core meaning"""
        input_text = "please write a uh detailed analysis of the market trends"
        expected = "Please write a detailed analysis of the market trends."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_multiple_sentences(self):
        """Test enhancement with multiple sentences"""
        input_text = (
            "first sentence goes here. um second sentence is different. third one too"
        )
        expected = (
            "First sentence goes here. Second sentence is different. Third one too."
        )
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_case_insensitive_fillers(self):
        """Test case-insensitive filler word removal"""
        input_text = "UM hello UH world YOU KNOW this is BASICALLY a test"
        expected = "Hello world this is a test."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_text_enhancement_preserves_important_words(self):
        """Test that important words are preserved even if they match patterns"""
        input_text = "I mean the average is right around fifty percent"
        expected = "The average is around fifty percent."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)


class TestSpeechDictationIntegration(unittest.TestCase):
    """Integration tests for speech dictation with web application"""

    def test_enhance_text_endpoint_with_ai(self):
        """Test text enhancement endpoint with AI optimization"""
        # This test focuses on the basic enhancement logic
        # AI optimization would be tested in integration tests

        test_text = "um hello world this is a test you know"

        # Test that the enhancement logic works
        enhanced = basic_text_enhancement(test_text)
        self.assertIn("Hello world", enhanced)
        self.assertNotIn("um", enhanced)
        self.assertNotIn("you know", enhanced)

    def test_text_enhancement_fallback(self):
        """Test fallback to basic enhancement when AI fails"""
        test_text = "um this is a test with filler words you know"
        result = basic_text_enhancement(test_text)

        self.assertNotIn("um", result)
        self.assertNotIn("you know", result)
        self.assertTrue(result.endswith("."))
        self.assertTrue(result.startswith("T"))  # Capitalized


class TestSpeechDictationErrorHandling(unittest.TestCase):
    """Test error handling for speech dictation"""

    def test_basic_enhancement_with_special_characters(self):
        """Test enhancement with special characters"""
        input_text = "hello @world #test $money %percent &and *star"
        result = basic_text_enhancement(input_text)

        # Should preserve special characters
        self.assertIn("@world", result)
        self.assertIn("#test", result)
        self.assertIn("$money", result)

    def test_basic_enhancement_with_numbers(self):
        """Test enhancement with numbers"""
        input_text = "the price is um 25 dollars and 50 cents you know"
        expected = "The price is 25 dollars and 50 cents."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)

    def test_basic_enhancement_with_unicode(self):
        """Test enhancement with unicode characters"""
        input_text = "café naïve résumé über"
        expected = "Café naïve résumé über."
        result = basic_text_enhancement(input_text)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
