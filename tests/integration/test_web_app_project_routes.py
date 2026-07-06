#!/usr/bin/env python3
"""
Integration tests for project route success/failure handling.

The create/update/delete project routes checked ``result.startswith("Success")``
but the data manager returns messages like "Project '...' created successfully!"
on success and "Error: ..." on failure. The success branch therefore never
fired: successful creates/updates were rendered as form errors and successful
deletes returned HTTP 400. These tests lock in the corrected behavior.
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
class TestProjectRouteSuccessHandling(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name

        # Single-user mode keeps the test focused on success/failure handling.
        self._saved_mt = os.environ.get("MULTITENANT_MODE")
        os.environ["MULTITENANT_MODE"] = "false"

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

    def _dm(self):
        return PromptDataManager(
            db_path=self.db_path, tenant_id="default", user_id="default"
        )

    def _create_project_direct(self, name="Proj"):
        result = self._dm().add_project(
            name=name, title=name, description="d", project_type="general"
        )
        self.assertFalse(result.startswith("Error:"), result)
        return next(p["id"] for p in self._dm().get_projects() if p["name"] == name)

    def test_create_project_success_redirects(self):
        """A successful create must redirect (302), not render a form error."""
        resp = self.client.post(
            "/projects/new",
            data={
                "name": "alpha",
                "title": "Alpha",
                "description": "desc",
                "project_type": "general",
            },
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)
        names = {p["name"] for p in self._dm().get_projects()}
        self.assertIn("alpha", names)

    def test_update_project_success_redirects(self):
        """A successful update must redirect (302), not render a form error."""
        project_id = self._create_project_direct("beta")
        resp = self.client.post(
            f"/projects/{project_id}/edit",
            data={
                "name": "beta",
                "title": "Beta Updated",
                "description": "desc2",
                "project_type": "general",
            },
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)

    def test_delete_project_success_returns_ok(self):
        """A successful delete must return 200, not HTTP 400."""
        project_id = self._create_project_direct("gamma")
        resp = self.client.delete(f"/projects/{project_id}", follow_redirects=False)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
        names = {p["name"] for p in self._dm().get_projects()}
        self.assertNotIn("gamma", names)


if __name__ == "__main__":
    unittest.main()
