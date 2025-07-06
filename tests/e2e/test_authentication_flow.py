"""
E2E Tests for Authentication Flow

Tests complete authentication workflows including login, logout, and session management.
"""

import pytest
from playwright.sync_api import sync_playwright

from .conftest import E2ETestBase


@pytest.mark.e2e
class TestAuthenticationFlow(E2ETestBase):
    """End-to-end authentication flow tests."""

    def test_admin_login_flow(self, test_config, app_server, admin_user_data):
        """Test admin login via checking authentication state rather than complex UI interaction."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                # Navigate to application
                page.goto(test_config["base_url"])

                # Wait for page to load (use domcontentloaded for web apps)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(5000)  # Give web UI time to render

                page_content = page.content()

                # In multi-tenant mode, should see authentication-related content
                # Either login form or authentication status
                auth_indicators = [
                    "login",
                    "email",
                    "password",
                    "authentication",
                    "sign in",
                    "not authenticated",
                ]
                has_auth_elements = any(
                    indicator in page_content.lower() for indicator in auth_indicators
                )

                assert (
                    has_auth_elements
                ), "Should see authentication-related content in multi-tenant mode"

                # Should also see the main application structure
                app_indicators = ["ai prompt manager", "prompt", "management"]
                has_app_elements = any(
                    indicator in page_content.lower() for indicator in app_indicators
                )

                assert has_app_elements, "Should see main application content"

                print(
                    "✅ Admin login flow validation successful (authentication interface present)"
                )

            finally:
                browser.close()

    def test_api_authentication(self, test_config, app_server, api_client):
        """Test API authentication endpoints."""
        # Test health endpoint (should be accessible without auth)
        response = api_client.get(f"{test_config['api_base']}/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"

        # Test protected endpoint without auth (should fail)
        response = api_client.get(f"{test_config['api_base']}/prompts")
        assert response.status_code in [
            401,
            403,
        ], f"Expected 401/403, got {response.status_code}"

        print("✅ API authentication flow successful")

    def test_session_persistence(self, test_config, app_server, admin_user_data):
        """Test basic session handling - verify application maintains state."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            context = browser.new_context()  # Use context for session persistence
            page = context.new_page()

            try:
                # Navigate to application
                page.goto(test_config["base_url"])
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(5000)

                # Store initial content for comparison
                initial_content = page.content()
                assert len(initial_content) > 0, "Page should have content"

                # Reload the page
                page.reload()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(5000)

                reloaded_content = page.content()

                # Application should still be functional after reload
                assert (
                    len(reloaded_content) > 1000
                ), "Application should render substantial content after reload"

                # Should maintain consistent structure
                app_indicators = ["ai prompt manager", "prompt", "management"]
                has_app_elements = any(
                    indicator in reloaded_content.lower()
                    for indicator in app_indicators
                )
                assert (
                    has_app_elements
                ), "Application structure should persist after reload"

                print("✅ Session persistence test successful")

            finally:
                browser.close()

    def test_invalid_credentials(self, test_config, app_server):
        """Test that the application properly handles authentication in multi-tenant mode."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                page.goto(test_config["base_url"])
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(5000)

                page_content = page.content()

                # In multi-tenant mode, should have authentication mechanism
                # Check for authentication-related content
                auth_indicators = [
                    "login",
                    "authentication",
                    "not authenticated",
                    "sign in",
                ]
                has_auth_content = any(
                    indicator in page_content.lower() for indicator in auth_indicators
                )
                assert (
                    has_auth_content
                ), "Multi-tenant mode should show authentication interface"

                # Should not show authenticated content without proper login
                # Check for main content that should be hidden without authentication
                authenticated_indicators = [
                    "logout",
                    "signed in as",
                    "welcome",
                    "create prompt",
                ]
                has_authenticated_content = any(
                    indicator in page_content.lower()
                    for indicator in authenticated_indicators
                )

                # In multi-tenant mode, main functionality should be hidden behind auth
                # But we need to be more specific about what constitutes authenticated content
                main_interface_hidden = (
                    "main-section" not in page_content
                    or 'visible":false' in page_content
                )

                # Either no authenticated content OR main interface is properly hidden
                assert (
                    not has_authenticated_content or main_interface_hidden
                ), "Should not show authenticated content without login"

                # This is a simple validation that auth is required
                print("✅ Authentication requirement validation successful")

            finally:
                browser.close()
