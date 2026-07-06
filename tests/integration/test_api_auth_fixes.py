#!/usr/bin/env python3
"""
Integration tests for REST API authentication fixes.

These tests intentionally exercise the REAL authentication dependencies
(they do NOT mock get_current_user_context / get_data_manager_configured),
so they can catch auth-bypass and always-401 regressions that mocked tests
would hide.

Covered defects:
- prompt_api_endpoints: data manager ignored the bearer token and hardcoded
  tenant_id/user_id="default" (unauthenticated access + broken tenant
  isolation).
- release_api_endpoints: the auth dependency never read the Authorization
  header, so every endpoint always returned 401 even with a valid token.
"""

import os
import sys
import tempfile
import unittest

# Add the project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from api_token_manager import APITokenManager  # noqa: E402
from auth_manager import AuthManager  # noqa: E402
from prompt_api_endpoints import create_prompt_router  # noqa: E402
from prompt_data_manager import PromptDataManager  # noqa: E402
from release_api_endpoints import (  # noqa: E402
    _default_token_manager,
    create_release_router,
)

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


def _make_tenant_user_token(auth_manager, token_manager, subdomain, email):
    """Create a tenant + user + API token, returning (tenant_id, user_id, token)."""
    ok, msg = auth_manager.create_tenant(f"Tenant {subdomain}", subdomain)
    assert ok, msg
    tenant = auth_manager.get_tenant_by_subdomain(subdomain)
    assert tenant is not None
    ok, msg = auth_manager.create_user(
        tenant_id=tenant.id,
        email=email,
        password="password123",
        first_name="Test",
        last_name="User",
        role="user",
    )
    assert ok, msg
    user = auth_manager.get_user_by_email(email, tenant.id)
    assert user is not None
    ok, msg, full_token = token_manager.create_api_token(
        user_id=user.id, tenant_id=tenant.id, name="test-token"
    )
    assert ok, msg
    assert full_token
    return tenant.id, user.id, full_token


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestPromptApiAuth(unittest.TestCase):
    """The prompt API must authenticate and scope to the token's tenant."""

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name

        self.auth_manager = AuthManager(self.db_path)
        self.token_manager = APITokenManager(self.db_path)

        self.tenant_id, self.user_id, self.token = _make_tenant_user_token(
            self.auth_manager, self.token_manager, "tenant-a", "a@example.com"
        )

        app = FastAPI()
        app.include_router(create_prompt_router(self.db_path))
        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_list_prompts_requires_authentication(self):
        """Without a bearer token the endpoint must reject the request."""
        response = self.client.get("/api/prompts/")
        self.assertEqual(response.status_code, 401)

    def test_list_prompts_rejects_invalid_token(self):
        """An invalid bearer token must be rejected."""
        response = self.client.get(
            "/api/prompts/",
            headers={"Authorization": "Bearer apm_not_a_real_token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_token_scopes_to_its_own_tenant(self):
        """A valid token sees its tenant's prompts, never another tenant's."""
        # Prompt owned by tenant A (the token's tenant).
        dm_a = PromptDataManager(
            db_path=self.db_path, tenant_id=self.tenant_id, user_id=self.user_id
        )
        dm_a.add_prompt("mine", "Mine", "content A", "Cat", "")

        # Prompt owned by a different tenant B.
        t_b, u_b, _ = _make_tenant_user_token(
            self.auth_manager, self.token_manager, "tenant-b", "b@example.com"
        )
        dm_b = PromptDataManager(db_path=self.db_path, tenant_id=t_b, user_id=u_b)
        dm_b.add_prompt("theirs", "Theirs", "content B", "Cat", "")

        response = self.client.get(
            "/api/prompts/", headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        names = {p["name"] for p in response.json()["prompts"]}
        self.assertIn("mine", names)
        self.assertNotIn("theirs", names)


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestReleaseApiAuth(unittest.TestCase):
    """The release API must honor a valid bearer token instead of always 401."""

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name

        self.auth_manager = AuthManager(self.db_path)
        self.token_manager = APITokenManager(self.db_path)
        self.tenant_id, self.user_id, self.token = _make_tenant_user_token(
            self.auth_manager, self.token_manager, "rel-tenant", "rel@example.com"
        )

        app = FastAPI()
        app.include_router(create_release_router(self.db_path))
        # Point token validation at the test database (real auth logic still
        # runs: header parsing, bearer check, and token validation).
        app.dependency_overrides[_default_token_manager] = lambda: self.token_manager
        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_list_releases_requires_authentication(self):
        """Without a bearer token the endpoint must reject the request."""
        response = self.client.get("/api/releases/")
        self.assertEqual(response.status_code, 401)

    def test_list_releases_accepts_valid_token(self):
        """A valid bearer token must be accepted (was always 401)."""
        response = self.client.get(
            "/api/releases/", headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


if __name__ == "__main__":
    unittest.main()
