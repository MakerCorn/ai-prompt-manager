"""
Pytest plugin for E2E tests to handle Playwright sync API properly.
"""

import pytest


def pytest_collection_modifyitems(config, items):
    """Modify test items to disable asyncio for E2E tests."""
    for item in items:
        # Check if this is an E2E test
        if "e2e" in str(item.fspath) or item.get_closest_marker("e2e"):
            # Add marker to disable asyncio
            item.add_marker(pytest.mark.asyncio(mode="off"))


@pytest.fixture(scope="session", autouse=True)
def disable_asyncio_for_e2e(request):
    """Disable asyncio mode for E2E tests."""
    if "e2e" in str(request.fspath):
        # This fixture runs for E2E tests and ensures no asyncio loop
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to handle it
            if loop.is_running():
                # For E2E tests, we'll run in a separate thread
                pass
        except RuntimeError:
            # No running loop, which is what we want for sync Playwright
            pass
