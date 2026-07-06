#!/usr/bin/env python3
"""
Integration tests for Release Management API

Tests include:
- API endpoint functionality
- Authentication and authorization
- Multi-tenant data isolation
- Database integration
- Error handling
- Performance testing
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from api_token_manager import APITokenManager  # noqa: E402
from auth_manager import AuthManager  # noqa: E402
from release_api_endpoints import (  # noqa: E402
    _default_token_manager,
    create_admin_release_router,
    create_release_router,
)
from release_manager import ReleaseManager  # noqa: E402


def _bearer(token_manager, user_id, tenant_id, name="test-token"):
    """Create a real API token and return an Authorization header dict."""
    ok, msg, full_token = token_manager.create_api_token(
        user_id=user_id, tenant_id=tenant_id, name=name
    )
    assert ok, msg
    return {"Authorization": f"Bearer {full_token}"}


try:
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestReleaseAPIIntegration(unittest.TestCase):
    """Integration tests for release API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize managers
        self.auth_manager = AuthManager(self.db_path)
        self.release_manager = ReleaseManager(self.db_path)

        # Create test tenant and user
        tenant_success, tenant_message = self.auth_manager.create_tenant(
            "Test Tenant", "test-tenant"
        )
        self.assertTrue(
            tenant_success, f"Tenant creation should succeed: {tenant_message}"
        )

        # Get tenant ID
        tenant = self.auth_manager.get_tenant_by_subdomain("test-tenant")
        self.assertIsNotNone(tenant)
        self.tenant_id = tenant.id

        # Create test user
        user_success, user_message = self.auth_manager.create_user(
            tenant_id=self.tenant_id,
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="user",
        )
        self.assertTrue(user_success)

        # Get user ID
        user = self.auth_manager.get_user_by_email("test@example.com", self.tenant_id)
        self.assertIsNotNone(user)
        self.user_id = user.id

        # Create FastAPI app with release routes
        from fastapi import FastAPI

        self.app = FastAPI()

        release_router = create_release_router(self.db_path)
        admin_router = create_admin_release_router(self.db_path)

        self.app.include_router(release_router)
        self.app.include_router(admin_router)

        # Real authentication against the test database: issue a genuine API
        # token and point the auth dependency's token manager at this DB.
        self.token_manager = APITokenManager(self.db_path)
        self.app.dependency_overrides[_default_token_manager] = (
            lambda: self.token_manager
        )
        self.auth_headers = _bearer(self.token_manager, self.user_id, self.tenant_id)

        self.client = TestClient(self.app)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_list_releases_empty(self):
        """Test listing releases when none exist"""
        response = self.client.get("/api/releases/", headers=self.auth_headers)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_create_and_list_releases(self):
        """Test creating and listing releases"""
        # Create release via API
        release_data = {
            "version": "1.0.0",
            "title": "First Release",
            "description": "Initial release with basic features",
            "is_major": True,
            "is_featured": True,
            "changelog_url": "https://github.com/test/repo/releases/tag/v1.0.0",
        }

        response = self.client.post(
            "/api/releases/", json=release_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("message", result)
        self.assertIn("created successfully", result["message"])

        # List releases
        response = self.client.get("/api/releases/", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

        releases = response.json()
        self.assertEqual(len(releases), 1)

        release = releases[0]
        self.assertEqual(release["version"], "1.0.0")
        self.assertEqual(release["title"], "First Release")
        self.assertTrue(release["is_major"])
        self.assertTrue(release["is_featured"])

    def test_unread_count(self):
        """Test unread count endpoint"""
        # Initially no releases
        response = self.client.get(
            "/api/releases/unread-count", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["unread_count"], 0)

        # Create a release
        self.release_manager.create_release_announcement(
            version="1.0.0", title="Test Release", description="Test description"
        )

        # Should have 1 unread
        response = self.client.get(
            "/api/releases/unread-count", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["unread_count"], 1)

    def test_mark_release_viewed(self):
        """Test marking releases as viewed"""
        # Create a release
        success, _ = self.release_manager.create_release_announcement(
            version="1.0.0", title="Test Release", description="Test description"
        )
        self.assertTrue(success)

        releases = self.release_manager.get_releases(limit=1)
        release_id = releases[0].id

        # Mark as viewed
        view_data = {"release_id": release_id, "is_dismissed": False}

        response = self.client.post(
            "/api/releases/mark-viewed", json=view_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("message", result)

        # Mark as dismissed
        view_data["is_dismissed"] = True
        response = self.client.post(
            "/api/releases/mark-viewed", json=view_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

    def test_release_stats(self):
        """Test release statistics endpoint"""
        # Create test releases
        releases_data = [
            ("1.0.0", "Release 1", False, False),
            ("2.0.0", "Release 2", True, True),
            ("2.1.0", "Release 3", False, True),
        ]

        for version, title, is_major, is_featured in releases_data:
            self.release_manager.create_release_announcement(
                version=version,
                title=title,
                description=f"Description for {title}",
                is_major=is_major,
                is_featured=is_featured,
            )

        response = self.client.get("/api/releases/stats", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["total_releases"], 3)
        self.assertEqual(data["major_releases"], 1)
        self.assertEqual(data["featured_releases"], 2)
        self.assertEqual(data["unread_releases"], 3)
        self.assertEqual(data["latest_version"], "2.1.0")  # Most recent by creation

    @patch("requests.get")
    def test_github_sync(self, mock_get):
        """Test GitHub sync endpoint"""
        # Mock GitHub API response
        mock_response_data = [
            {
                "tag_name": "v1.0.0",
                "name": "Release 1.0.0",
                "body": "Test release from API",
                "published_at": "2024-01-01T00:00:00Z",
                "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
                "tarball_url": "https://github.com/test/repo/archive/v1.0.0.tar.gz",
                "id": 12345,
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test sync
        sync_data = {"source": "github", "force": False}

        response = self.client.post(
            "/api/releases/sync", json=sync_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("message", result)
        self.assertIn("Synced", result["message"])

        # Verify release was created
        releases = self.release_manager.get_releases(limit=10)
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0].version, "1.0.0")

    def test_invalid_sync_source(self):
        """Test invalid sync source handling"""
        sync_data = {"source": "invalid_source", "force": False}

        response = self.client.post(
            "/api/releases/sync", json=sync_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

        error = response.json()
        self.assertIn("detail", error)
        self.assertIn("Invalid sync source", error["detail"])

    def test_health_endpoint(self):
        """Test release system health endpoint"""
        response = self.client.get("/api/releases/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertIn("configuration", data)

    def test_duplicate_version_error(self):
        """Test duplicate version handling via API"""
        release_data = {
            "version": "1.0.0",
            "title": "First Release",
            "description": "Initial release",
        }

        # Create first release
        response = self.client.post(
            "/api/releases/", json=release_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        # Try to create duplicate
        release_data["title"] = "Duplicate Release"
        response = self.client.post(
            "/api/releases/", json=release_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

        error = response.json()
        self.assertIn("detail", error)

    def test_pagination_limits(self):
        """Test pagination and limits"""
        # Create multiple releases
        for i in range(15):
            self.release_manager.create_release_announcement(
                version=f"1.{i}.0", title=f"Release {i}", description=f"Description {i}"
            )

        # Test default limit
        response = self.client.get("/api/releases/", headers=self.auth_headers)
        releases = response.json()
        self.assertEqual(len(releases), 10)  # Default limit

        # Test custom limit
        response = self.client.get("/api/releases/?limit=5", headers=self.auth_headers)
        releases = response.json()
        self.assertEqual(len(releases), 5)

        # Test maximum limit
        response = self.client.get(
            "/api/releases/?limit=100", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_unauthorized_access(self):
        """Test unauthorized access handling with the real auth dependency."""
        # Test without authorization header
        response = self.client.get("/api/releases/")
        self.assertEqual(response.status_code, 401)

        # Test with an invalid (non-existent) bearer token
        invalid_headers = {"Authorization": "Bearer apm_invalid_token"}
        response = self.client.get("/api/releases/", headers=invalid_headers)
        self.assertEqual(response.status_code, 401)


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestAdminReleaseAPI(unittest.TestCase):
    """Test admin-specific release API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize managers
        self.auth_manager = AuthManager(self.db_path)
        self.release_manager = ReleaseManager(self.db_path)

        # Create test tenant and admin user
        tenant_success, _ = self.auth_manager.create_tenant(
            "Admin Tenant", "admin-tenant"
        )
        self.assertTrue(tenant_success)

        tenant = self.auth_manager.get_tenant_by_subdomain("admin-tenant")
        self.tenant_id = tenant.id

        user_success, _ = self.auth_manager.create_user(
            tenant_id=self.tenant_id,
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        self.assertTrue(user_success)

        user = self.auth_manager.get_user_by_email("admin@example.com", self.tenant_id)
        self.user_id = user.id

        # Create FastAPI app with admin routes
        from fastapi import FastAPI

        self.app = FastAPI()

        admin_router = create_admin_release_router(self.db_path)
        self.app.include_router(admin_router)

        # Real authentication: verify_admin_user currently authorizes any
        # authenticated user, so a genuine token for the admin user suffices.
        self.token_manager = APITokenManager(self.db_path)
        self.app.dependency_overrides[_default_token_manager] = (
            lambda: self.token_manager
        )
        self.auth_headers = _bearer(self.token_manager, self.user_id, self.tenant_id)

        self.client = TestClient(self.app)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_list_all_releases(self):
        """Test admin endpoint to list all releases"""
        # Create test releases
        for i in range(3):
            self.release_manager.create_release_announcement(
                version=f"1.{i}.0", title=f"Release {i}", description=f"Description {i}"
            )

        response = self.client.get("/api/admin/releases/all", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

        releases = response.json()
        self.assertEqual(len(releases), 3)

        # Check structure
        release = releases[0]
        self.assertIn("id", release)
        self.assertIn("version", release)
        self.assertIn("title", release)
        self.assertIn("description", release)
        self.assertIn("release_date", release)

    def test_delete_release(self):
        """Test admin endpoint to delete releases"""
        # Create a release
        success, _ = self.release_manager.create_release_announcement(
            version="1.0.0", title="Test Release", description="Test description"
        )
        self.assertTrue(success)

        releases = self.release_manager.get_releases(limit=1)
        release_id = releases[0].id

        # Delete via API
        response = self.client.delete(
            f"/api/admin/releases/{release_id}", headers=self.auth_headers
        )

        # Note: Delete functionality returns "not yet implemented" message
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("message", result)

    @patch("requests.get")
    def test_bulk_sync(self, mock_get):
        """Test admin bulk sync endpoint"""
        # Mock GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock changelog file
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open_changelog()),
        ):

            response = self.client.post(
                "/api/admin/releases/bulk-sync", headers=self.auth_headers
            )
            self.assertEqual(response.status_code, 200)

            result = response.json()
            self.assertIn("sync_results", result)
            self.assertIsInstance(result["sync_results"], list)

    def test_cleanup_cache(self):
        """Test admin cache cleanup endpoint"""
        # Add some cache data
        self.release_manager._cache_data("test_key", {"data": "test"})

        response = self.client.post(
            "/api/admin/releases/cleanup-cache", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("message", result)
        self.assertIn("cleanup completed", result["message"])


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI not available")
class TestMultiTenantIsolation(unittest.TestCase):
    """Test multi-tenant data isolation in release system"""

    def setUp(self):
        """Set up multi-tenant test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        self.auth_manager = AuthManager(self.db_path)
        self.release_manager = ReleaseManager(self.db_path)

        # Create two tenants
        tenant1_success, _ = self.auth_manager.create_tenant("Tenant 1", "tenant1")
        tenant2_success, _ = self.auth_manager.create_tenant("Tenant 2", "tenant2")
        self.assertTrue(tenant1_success and tenant2_success)

        self.tenant1 = self.auth_manager.get_tenant_by_subdomain("tenant1")
        self.tenant2 = self.auth_manager.get_tenant_by_subdomain("tenant2")

        # Create users for each tenant
        user1_success, _ = self.auth_manager.create_user(
            tenant_id=self.tenant1.id,
            email="user1@tenant1.com",
            password="password123",
            first_name="User",
            last_name="One",
            role="user",
        )

        user2_success, _ = self.auth_manager.create_user(
            tenant_id=self.tenant2.id,
            email="user2@tenant2.com",
            password="password123",
            first_name="User",
            last_name="Two",
            role="user",
        )

        self.assertTrue(user1_success and user2_success)

        self.user1 = self.auth_manager.get_user_by_email(
            "user1@tenant1.com", self.tenant1.id
        )
        self.user2 = self.auth_manager.get_user_by_email(
            "user2@tenant2.com", self.tenant2.id
        )

        # Create FastAPI app
        from fastapi import FastAPI

        self.app = FastAPI()

        release_router = create_release_router(self.db_path)
        self.app.include_router(release_router)

        # Real per-tenant tokens against the test database.
        self.token_manager = APITokenManager(self.db_path)
        self.app.dependency_overrides[_default_token_manager] = (
            lambda: self.token_manager
        )
        self.headers1 = _bearer(
            self.token_manager, self.user1.id, self.tenant1.id, "token1"
        )
        self.headers2 = _bearer(
            self.token_manager, self.user2.id, self.tenant2.id, "token2"
        )

        self.client = TestClient(self.app)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_user_view_isolation(self):
        """Test that user views are isolated between tenants"""
        # Create a release
        success, _ = self.release_manager.create_release_announcement(
            version="1.0.0",
            title="Shared Release",
            description="This release is visible to all tenants",
        )
        self.assertTrue(success)

        releases = self.release_manager.get_releases(limit=1)
        release_id = releases[0].id

        # User 1 marks as viewed (authenticated as user1 via a real token)
        view_data = {"release_id": release_id, "is_dismissed": False}
        response = self.client.post(
            "/api/releases/mark-viewed",
            json=view_data,
            headers=self.headers1,
        )
        self.assertEqual(response.status_code, 200)

        # Check unread counts
        count1 = self.release_manager.get_unread_count(self.user1.id)
        count2 = self.release_manager.get_unread_count(self.user2.id)

        # User1 should have 0 unread (marked as viewed), User2 should have 1 unread
        self.assertEqual(count1, 0)
        self.assertEqual(count2, 1)

    def test_release_access_across_tenants(self):
        """Test that releases are accessible across tenants but views are isolated"""
        # Create releases (releases are global, not tenant-specific)
        self.release_manager.create_release_announcement(
            version="1.0.0",
            title="Global Release",
            description="Available to all tenants",
        )

        # Both users should see the release (each with their own real token)
        response1 = self.client.get("/api/releases/", headers=self.headers1)
        response2 = self.client.get("/api/releases/", headers=self.headers2)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        releases1 = response1.json()
        releases2 = response2.json()

        # Both should see the same releases
        self.assertEqual(len(releases1), 1)
        self.assertEqual(len(releases2), 1)
        self.assertEqual(releases1[0]["version"], releases2[0]["version"])


def mock_open_changelog():
    """Mock function to simulate changelog file content"""
    changelog_content = """# Changelog

## [1.0.0] - 2024-01-01

Initial release
"""
    from unittest.mock import mock_open

    return mock_open(read_data=changelog_content)


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["GITHUB_RELEASES_ENABLED"] = "true"
    os.environ["CHANGELOG_ENABLED"] = "true"

    # Run tests
    unittest.main(verbosity=2)
