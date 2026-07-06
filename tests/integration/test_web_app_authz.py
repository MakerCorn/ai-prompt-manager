#!/usr/bin/env python3
"""
Integration tests for prompt ownership authorization in the web UI.

Public prompts are visible to every user in a tenant. Previously the
edit/update/delete routes located a prompt via the visibility-aware listing
and then mutated it by name (tenant-scoped only), so any tenant user could
modify or delete another user's public prompt. These tests lock in the
ownership guard.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from auth_manager import AuthManager  # noqa: E402
from prompt_data_manager import PromptDataManager  # noqa: E402

try:
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestPromptOwnershipAuthz(unittest.TestCase):
    SUBDOMAIN = "authz"

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name

        # Force multi-tenant mode for the web app under test.
        self._saved_mt = os.environ.get("MULTITENANT_MODE")
        os.environ["MULTITENANT_MODE"] = "true"

        self.auth_manager = AuthManager(self.db_path)
        ok, msg = self.auth_manager.create_tenant("Authz Tenant", self.SUBDOMAIN)
        self.assertTrue(ok, msg)
        self.tenant_id = self.auth_manager.get_tenant_by_subdomain(self.SUBDOMAIN).id

        for email, role in (
            ("a@example.com", "user"),
            ("b@example.com", "user"),
            ("admin@example.com", "admin"),
        ):
            ok, msg = self.auth_manager.create_user(
                tenant_id=self.tenant_id,
                email=email,
                password="password123",
                first_name="U",
                last_name="Ser",
                role=role,
            )
            self.assertTrue(ok, msg)
        self.user_a = self.auth_manager.get_user_by_email(
            "a@example.com", self.tenant_id
        )
        self.user_b = self.auth_manager.get_user_by_email(
            "b@example.com", self.tenant_id
        )

        # User A owns a PUBLIC prompt (visible to B within the tenant).
        dm_a = PromptDataManager(
            db_path=self.db_path, tenant_id=self.tenant_id, user_id=self.user_a.id
        )
        result = dm_a.add_prompt(
            "shared", "Shared", "A's content", "Cat", "", visibility="public"
        )
        self.assertFalse(result.startswith("Error:"), result)
        self.prompt_id = next(
            p["id"] for p in dm_a.get_all_prompts() if p["name"] == "shared"
        )

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

    def _login(self, email):
        resp = self.client.post(
            "/login",
            data={
                "email": email,
                "password": "password123",
                "subdomain": self.SUBDOMAIN,
            },
            follow_redirects=False,
        )
        # 302 on success (redirect to "/").
        self.assertEqual(resp.status_code, 302, resp.text)

    def test_cannot_edit_other_users_public_prompt(self):
        """User B must not be able to update User A's public prompt."""
        self._login("b@example.com")
        resp = self.client.post(
            f"/prompts/{self.prompt_id}/edit",
            data={
                "name": "hijacked",
                "content": "B overwrote this",
                "category": "Cat",
            },
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 403)

        # A's prompt must be untouched.
        dm_a = PromptDataManager(
            db_path=self.db_path, tenant_id=self.tenant_id, user_id=self.user_a.id
        )
        names = {p["name"] for p in dm_a.get_all_prompts()}
        self.assertIn("shared", names)
        self.assertNotIn("hijacked", names)

    def test_cannot_delete_other_users_public_prompt(self):
        """User B must not be able to delete User A's public prompt."""
        self._login("b@example.com")
        resp = self.client.delete(f"/prompts/{self.prompt_id}", follow_redirects=False)
        self.assertEqual(resp.status_code, 403)

        dm_a = PromptDataManager(
            db_path=self.db_path, tenant_id=self.tenant_id, user_id=self.user_a.id
        )
        names = {p["name"] for p in dm_a.get_all_prompts()}
        self.assertIn("shared", names)

    def test_owner_can_edit_own_prompt(self):
        """The owner (A) must still be able to edit their own prompt."""
        self._login("a@example.com")
        resp = self.client.post(
            f"/prompts/{self.prompt_id}/edit",
            data={
                "name": "shared",
                "content": "A edited own content",
                "category": "Cat",
                "visibility": "public",
            },
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)

    def test_non_admin_cannot_mutate_languages(self):
        """A non-admin user must be rejected from global language routes."""
        self._login("b@example.com")
        for path, payload in (
            ("/settings/language/create", {"language_code": "zz"}),
            ("/settings/language/save", {"language_code": "es"}),
            ("/settings/language/delete", {"language_code": "es"}),
            ("/settings/language/translate-key", {"key": "nav.prompts"}),
        ):
            resp = self.client.post(path, json=payload, follow_redirects=False)
            self.assertEqual(resp.status_code, 403, f"{path} -> {resp.status_code}")

    def test_admin_passes_language_gate(self):
        """An admin passes the gate (validation failure, not a 403)."""
        self._login("admin@example.com")
        # Empty body fails validation gracefully (200/success=False) rather
        # than 403, proving the admin was allowed through the gate. No
        # language file is created or deleted.
        resp = self.client.post(
            "/settings/language/create", json={}, follow_redirects=False
        )
        self.assertNotEqual(resp.status_code, 403)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["success"])


if __name__ == "__main__":
    unittest.main()
