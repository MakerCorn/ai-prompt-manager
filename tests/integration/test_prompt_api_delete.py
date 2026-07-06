#!/usr/bin/env python3
"""
Integration test for the prompt API delete endpoint's success handling.

delete_prompt returns a status STRING, not a boolean; the endpoint used
``if not success`` which is always False for a non-empty string, so failures
were reported as success. This verifies a genuine delete succeeds and is
reflected via the corrected string-contract check.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from api_token_manager import APITokenManager  # noqa: E402
from auth_manager import AuthManager  # noqa: E402
from prompt_api_endpoints import create_prompt_router  # noqa: E402
from prompt_data_manager import PromptDataManager  # noqa: E402

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestPromptApiDelete(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name
        auth = AuthManager(self.db_path)
        tokens = APITokenManager(self.db_path)
        auth.create_tenant("T", "t")
        tenant = auth.get_tenant_by_subdomain("t")
        auth.create_user(
            tenant_id=tenant.id,
            email="a@x.com",
            password="password123",
            first_name="A",
            last_name="B",
            role="user",
        )
        user = auth.get_user_by_email("a@x.com", tenant.id)
        ok, _, token = tokens.create_api_token(user.id, tenant.id, "t")
        self.token = token
        self.dm = PromptDataManager(
            db_path=self.db_path, tenant_id=tenant.id, user_id=user.id
        )
        self.dm.add_prompt("todelete", "T", "content", "Cat", "")
        self.prompt_id = next(
            p["id"] for p in self.dm.get_all_prompts() if p["name"] == "todelete"
        )
        app = FastAPI()
        app.include_router(create_prompt_router(self.db_path))
        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_delete_succeeds_and_removes_prompt(self):
        resp = self.client.delete(
            f"/api/prompts/{self.prompt_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
        names = {p["name"] for p in self.dm.get_all_prompts()}
        self.assertNotIn("todelete", names)


if __name__ == "__main__":
    unittest.main()
