#!/usr/bin/env python3
"""
Integration tests for single-user-mode accessibility of routes that
previously required an authenticated session unconditionally.

In single-user mode there is no login, so ``get_current_user`` always returns
None. Routes that raised 401 / redirected to /login on a None user were
unreachable in single-user mode even though the whole point of single-user
mode is to require no authentication.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from prompt_data_manager import PromptDataManager  # noqa: E402

try:
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestSingleUserRoutes(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name

        self._saved_mt = os.environ.get("MULTITENANT_MODE")
        os.environ["MULTITENANT_MODE"] = "false"

        # A prompt to execute.
        dm = PromptDataManager(
            db_path=self.db_path, tenant_id="default", user_id="default"
        )
        dm.add_prompt("greet", "Greet", "Hello {name}", "Cat", "")

        from web_app import create_web_app

        self.app = create_web_app(db_path=self.db_path)
        self.client = TestClient(self.app)

    def tearDown(self):
        if self._saved_mt is None:
            os.environ.pop("MULTITENANT_MODE", None)
        else:
            os.environ["MULTITENANT_MODE"] = self._saved_mt
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_calculate_tokens_accessible(self):
        """Token calculation must work in single-user mode (was always 401)."""
        resp = self.client.post(
            "/calculate-tokens",
            data={"text": "hello world", "model": "gpt-4"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])

    def test_execute_page_accessible(self):
        """The execute page must render in single-user mode (was /login)."""
        resp = self.client.get("/prompts/greet/execute", follow_redirects=False)
        self.assertEqual(resp.status_code, 200)

    def test_execute_post_accessible(self):
        """The execute action must work in single-user mode (was 401)."""
        resp = self.client.post("/prompts/greet/execute")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])


if __name__ == "__main__":
    unittest.main()
