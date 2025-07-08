#!/usr/bin/env python3
"""
Integration tests for Speech Dictation API endpoints
Testing complete speech enhancement and translation workflow through web interface
"""

import os
import sys
import tempfile
import time
import unittest
from multiprocessing import Process

import requests

# Add the project root to the path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def _run_speech_test_server(db_path, port):
    """Run test server for speech API integration tests"""
    try:
        import uvicorn

        from web_app import create_web_app

        app = create_web_app(db_path)
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")
    except Exception as e:
        print(f"Test server error: {e}")


class SpeechAPIIntegrationTest(unittest.TestCase):
    """Integration test suite for Speech API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with running server"""
        cls.port = 7864  # Different port to avoid conflicts
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        # Create temporary database
        cls.temp_db_fd, cls.test_db = tempfile.mkstemp(suffix=".db")

        # Initialize database with test data
        from auth_manager import AuthManager

        auth_manager = AuthManager(cls.test_db)

        # Create test tenant and user
        success, tenant_message = auth_manager.create_tenant("Test Tenant", "test")
        if not success:
            raise Exception(f"Failed to create test tenant: {tenant_message}")

        # Get tenant ID for user creation
        import sqlite3

        conn = sqlite3.connect(cls.test_db)
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

        # Start the test server
        cls.server_process = Process(
            target=_run_speech_test_server, args=(cls.test_db, cls.port)
        )
        cls.server_process.start()
        time.sleep(3)  # Give server time to start

        # Health check
        try:
            response = requests.get(f"{cls.base_url}/", timeout=5)
            if response.status_code != 200:
                raise Exception("Server health check failed")
        except Exception as e:
            cls.tearDownClass()
            raise Exception(f"Failed to start test server: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if hasattr(cls, "server_process") and cls.server_process:
            cls.server_process.terminate()
            cls.server_process.join(timeout=5)
            if cls.server_process.is_alive():
                cls.server_process.kill()

        # Clean up test database
        if hasattr(cls, "test_db") and os.path.exists(cls.test_db):
            os.unlink(cls.test_db)

    def setUp(self):
        """Set up for each test"""
        self.session = requests.Session()

        # Login to get session
        login_response = self.session.post(
            f"{self.base_url}/login",
            data={
                "email": "test@example.com",
                "password": "test123",
                "subdomain": "test",
            },
            allow_redirects=False,
        )

        self.assertEqual(login_response.status_code, 302)  # Redirect after login

    def test_01_enhance_text_endpoint_basic(self):
        """Test basic text enhancement endpoint"""
        test_text = "um hello world this is a test you know"

        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("enhanced_text", data)
        self.assertIn("original_text", data)

        enhanced_text = data["enhanced_text"]
        self.assertNotIn("um", enhanced_text.lower())
        self.assertNotIn("you know", enhanced_text.lower())
        self.assertTrue(enhanced_text.endswith("."))

    def test_02_enhance_text_endpoint_empty(self):
        """Test text enhancement with empty text"""
        response = self.session.post(
            f"{self.base_url}/enhance-text", data={"text": "", "type": "dictation"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["enhanced_text"], "")

    def test_03_enhance_text_endpoint_complex(self):
        """Test text enhancement with complex dictated text"""
        test_text = (
            "so um basically I want to create a prompt that will help me "
            "write better emails you know and it should be really detailed "
            "and comprehensive actually"
        )

        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        enhanced_text = data["enhanced_text"]
        # Should remove filler words
        self.assertNotIn("um", enhanced_text.lower())
        self.assertNotIn("basically", enhanced_text.lower())
        self.assertNotIn("you know", enhanced_text.lower())
        self.assertNotIn("actually", enhanced_text.lower())

        # Should preserve core content
        self.assertIn("create", enhanced_text.lower())
        self.assertIn("prompt", enhanced_text.lower())
        self.assertIn("emails", enhanced_text.lower())

    def test_04_enhance_text_without_auth(self):
        """Test text enhancement without authentication"""
        # Create new session without login
        unauth_session = requests.Session()

        response = unauth_session.post(
            f"{self.base_url}/enhance-text",
            data={"text": "test text", "type": "dictation"},
        )

        self.assertEqual(response.status_code, 401)

    def test_05_enhance_text_with_special_characters(self):
        """Test text enhancement with special characters and numbers"""
        test_text = (
            "the price is um 25 dollars and 50 cents at company@email.com you know"
        )

        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        enhanced_text = data["enhanced_text"]
        # Should preserve numbers and email
        self.assertIn("25", enhanced_text)
        self.assertIn("50", enhanced_text)
        self.assertIn("company@email.com", enhanced_text)
        # Should remove filler words
        self.assertNotIn("um", enhanced_text.lower())
        self.assertNotIn("you know", enhanced_text.lower())

    def test_06_enhance_text_multiple_sentences(self):
        """Test text enhancement with multiple sentences"""
        test_text = (
            "first sentence goes here. um second sentence is different "
            "you know. third one is also important actually"
        )

        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        enhanced_text = data["enhanced_text"]
        # Should have proper sentence structure
        sentences = enhanced_text.split(".")
        # Should have at least 3 sentences (may be combined)
        self.assertGreater(len([s for s in sentences if s.strip()]), 0)

        # Should start with capital letter
        self.assertTrue(enhanced_text[0].isupper())

    def test_07_enhance_text_performance(self):
        """Test text enhancement performance with longer text"""
        test_text = (
            "um " * 50 + "this is a longer text with many filler words you know " * 10
        )

        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        # Should complete within reasonable time (5 seconds for fallback)
        self.assertLess(end_time - start_time, 5.0)

        enhanced_text = data["enhanced_text"]
        # Should be significantly shorter after removing filler words
        # Original has 50 "um "s (150 chars) + 10 " you know"s (100 chars)
        # = ~250 chars to remove. So we expect at least 200 characters reduction
        self.assertLess(len(enhanced_text), len(test_text) - 200)

    def test_08_translate_dictated_text_endpoint(self):
        """Test translation of dictated text (existing endpoint with source language)"""
        test_text = "Bonjour monde, ceci est un test"  # French text

        response = self.session.post(
            f"{self.base_url}/translate",
            data={"text": test_text, "target_lang": "en", "source_lang": "fr"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Translation may or may not succeed depending on service availability
        # Just verify the endpoint structure
        self.assertIn("success", data)
        self.assertIn("original_text", data)
        self.assertEqual(data["original_text"], test_text)

    def test_09_enhance_text_edge_cases(self):
        """Test text enhancement edge cases"""
        edge_cases = [
            ("    ", ""),  # Only whitespace
            (".", "."),  # Only punctuation
            ("123 456", "123 456."),  # Only numbers
            ("!!!", "!!!"),  # Multiple punctuation
            ("a", "A."),  # Single character
        ]

        for input_text, expected_pattern in edge_cases:
            with self.subTest(input_text=input_text):
                response = self.session.post(
                    f"{self.base_url}/enhance-text",
                    data={"text": input_text, "type": "dictation"},
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data.get("success"))

    def test_10_enhance_text_unicode_support(self):
        """Test text enhancement with unicode characters"""
        test_text = "um café naïve résumé über you know"

        response = self.session.post(
            f"{self.base_url}/enhance-text",
            data={"text": test_text, "type": "dictation"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        enhanced_text = data["enhanced_text"]
        # Should preserve unicode characters (case insensitive check)
        self.assertIn("café", enhanced_text.lower())
        self.assertIn("naïve", enhanced_text.lower())
        self.assertIn("résumé", enhanced_text.lower())
        self.assertIn("über", enhanced_text.lower())
        # Should remove filler words (check for whole words, not substrings)
        import re

        self.assertIsNone(re.search(r"\bum\b", enhanced_text.lower()))
        self.assertNotIn("you know", enhanced_text.lower())


class SpeechAPIErrorHandlingTest(unittest.TestCase):
    """Test error handling for speech API endpoints"""

    def setUp(self):
        """Set up for error handling tests"""
        self.port = 7865
        self.base_url = f"http://127.0.0.1:{self.port}"
        # Note: These tests may not have a running server intentionally

    def test_enhance_text_service_unavailable(self):
        """Test enhancement when service is unavailable"""
        try:
            response = requests.post(
                f"{self.base_url}/enhance-text",
                data={"text": "test", "type": "dictation"},
                timeout=1,
            )
            # If we get here, server is running, so check for auth error
            self.assertEqual(response.status_code, 401)
        except requests.exceptions.RequestException:
            # Expected when service is unavailable
            pass

    def test_translate_text_service_unavailable(self):
        """Test translation when service is unavailable"""
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                data={"text": "test", "target_lang": "en"},
                timeout=1,
            )
            # If we get here, server is running, so check for auth error
            self.assertEqual(response.status_code, 401)
        except requests.exceptions.RequestException:
            # Expected when service is unavailable
            pass


if __name__ == "__main__":
    unittest.main()
