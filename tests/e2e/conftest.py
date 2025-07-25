"""
E2E Test Configuration and Fixtures

Provides shared fixtures and configuration for end-to-end testing.
"""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
import requests
from playwright.sync_api import sync_playwright

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def find_free_port():
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Configuration for E2E tests."""
    # Use environment variable or find a free port
    if "E2E_TEST_PORT" in os.environ:
        port = int(os.environ["E2E_TEST_PORT"])
    else:
        port = find_free_port()

    return {
        "base_url": f"http://localhost:{port}",
        "api_base": f"http://localhost:{port + 1}",  # API runs on port+1
        "timeout": 60,  # Increased timeout for startup
        "db_path": "e2e_test.db",
        "headless": os.getenv("E2E_HEADLESS", "true").lower() == "true",
        "slow_mo": int(os.getenv("E2E_SLOW_MO", "0")),
        "port": port,
        "api_port": port + 1,  # Add API port to config
    }


@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for E2E tests."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def app_server(
    test_config: Dict[str, Any], temp_dir: str
) -> Generator[Dict[str, subprocess.Popen], None, None]:
    """Start web app server with API for E2E testing."""
    print("\n🚀 Starting E2E test servers...")

    # Set environment variables for E2E testing
    env = os.environ.copy()
    env.update(
        {
            "MULTITENANT_MODE": "true",
            "SERVER_HOST": "127.0.0.1",
            "SERVER_PORT": str(test_config["port"]),
            "DB_TYPE": "sqlite",
            "DB_PATH": os.path.join(temp_dir, test_config["db_path"]),
            "LOCAL_DEV_MODE": "true",
            "SECRET_KEY": "e2e-test-secret-key",
            "PYTHONPATH": f"{os.getcwd()}/src:{os.getcwd()}",
        }
    )

    # Create log files
    web_log_path = os.path.join(temp_dir, "web_server.log")
    api_log_path = os.path.join(temp_dir, "api_server.log")

    # Start web server with API integration
    print(f"🌐 Starting web server with API on {test_config['base_url']}")
    web_cmd = [
        sys.executable,
        "run.py",
        "--with-api",
        "--port",
        str(test_config["port"]),
        "--host",
        "127.0.0.1",
    ]
    with open(web_log_path, "w") as log_file:
        web_process = subprocess.Popen(
            web_cmd,
            env=env,
            cwd=os.getcwd(),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

    # API endpoints run in separate thread within the same process
    print("🔌 API server runs as separate thread in web process")

    # Wait for both servers to be ready
    print("⏱️ Waiting for servers to start...")

    # Wait for web server
    web_ready = False
    start_time = time.time()
    while time.time() - start_time < test_config["timeout"]:
        try:
            response = requests.get(test_config["base_url"], timeout=5)
            if response.status_code == 200:
                web_ready = True
                print(f"✅ Web server ready at {test_config['base_url']}")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

    # Wait for API server (dual-server architecture)
    # Give the web server a bit more time to start the API thread
    time.sleep(3)

    api_ready = False
    api_base_url = f"http://localhost:{test_config['api_port']}"
    start_time = time.time()
    while time.time() - start_time < test_config["timeout"]:
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                api_ready = True
                print(f"✅ API server ready at {api_base_url}")
                break
        except requests.exceptions.RequestException as e:
            print(f"⏳ API server not ready yet: {e}")
        time.sleep(2)  # Wait a bit longer between attempts

    if not web_ready or not api_ready:
        print(f"❌ Server startup failed - Web: {web_ready}, API: {api_ready}")

        # Show logs
        try:
            with open(web_log_path, "r") as f:
                print("Web server output:", f.read())
        except Exception as e:
            print(f"Could not read web log: {e}")

        try:
            with open(api_log_path, "r") as f:
                print("API server output:", f.read())
        except Exception as e:
            print(f"Could not read API log: {e}")

        # Cleanup
        for proc in [web_process]:
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

        pytest.fail("E2E test servers failed to start")

    # Update test config with API server info (dual-server architecture)
    test_config["api_base"] = (
        api_base_url  # API endpoints are directly on the API server
    )

    processes = {"web": web_process}  # API runs in thread within web process

    yield processes

    # Cleanup
    print("\n🛑 Stopping E2E test servers")
    for name, process in processes.items():
        print(f"Stopping {name} server...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


@pytest.fixture
def api_client(test_config: Dict[str, Any], app_server) -> requests.Session:
    """HTTP client for API testing."""
    session = requests.Session()
    # Note: timeout is handled per-request, not at session level
    return session


@pytest.fixture
def admin_user_data() -> Dict[str, str]:
    """Default admin user credentials for testing."""
    return {"email": "admin@localhost", "password": "admin123", "tenant": "localhost"}


@pytest.fixture(scope="session")
def browser_context(test_config: Dict[str, Any]):
    """Shared browser context for E2E tests."""
    import asyncio
    import threading

    # Check if we're in an asyncio loop
    try:
        loop = asyncio.get_running_loop()
        # If we're in an asyncio loop, run Playwright in a separate thread
        if loop.is_running():
            playwright_data = {}

            def run_playwright():
                playwright = sync_playwright().start()
                browser = playwright.chromium.launch(
                    headless=test_config["headless"], slow_mo=test_config["slow_mo"]
                )
                context = browser.new_context()
                playwright_data.update(
                    {"playwright": playwright, "browser": browser, "context": context}
                )

            thread = threading.Thread(target=run_playwright)
            thread.start()
            thread.join()

            yield playwright_data["context"]

            # Cleanup in thread
            def cleanup():
                playwright_data["context"].close()
                playwright_data["browser"].close()
                playwright_data["playwright"].stop()

            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.start()
            cleanup_thread.join()
        else:
            # No asyncio loop, run normally
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=test_config["headless"], slow_mo=test_config["slow_mo"]
            )
            context = browser.new_context()

            yield context

            # Cleanup
            context.close()
            browser.close()
            playwright.stop()
    except RuntimeError:
        # No asyncio loop, run normally
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=test_config["headless"], slow_mo=test_config["slow_mo"]
        )
        context = browser.new_context()

        yield context

        # Cleanup
        context.close()
        browser.close()
        playwright.stop()


@pytest.fixture
def page(browser_context):
    """Create a new page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture
def sample_prompt_data() -> Dict[str, Any]:
    """Sample prompt data for testing."""
    return {
        "name": "e2e_test_prompt",
        "title": "E2E Test Prompt",
        "content": (
            "You are a helpful AI assistant for E2E testing. Please respond "
            "with 'E2E Test Successful' to verify the workflow."
        ),
        "category": "Testing",
        "tags": "e2e,testing,automation",
    }


class E2ETestBase:
    """Base class for E2E tests with common utilities."""

    def wait_for_element(self, page, selector: str, timeout: int = 10000):
        """Wait for an element to be visible."""
        return page.wait_for_selector(selector, timeout=timeout)

    def fill_form_field(self, page, selector: str, value: str):
        """Fill a form field with proper waiting."""
        element = self.wait_for_element(page, selector)
        element.clear()
        element.fill(value)

    def click_button(self, page, selector: str):
        """Click a button with proper waiting."""
        button = self.wait_for_element(page, selector)
        button.click()

    def assert_text_contains(self, page, selector: str, expected_text: str):
        """Assert that an element contains expected text."""
        element = self.wait_for_element(page, selector)
        actual_text = element.text_content()
        assert (
            expected_text in actual_text
        ), f"Expected '{expected_text}' in '{actual_text}'"

    def wait_for_api_response(
        self,
        api_client: requests.Session,
        url: str,
        expected_status: int = 200,
        timeout: int = 30,
    ):
        """Wait for API endpoint to return expected status."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = api_client.get(url)
                if response.status_code == expected_status:
                    return response
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise TimeoutError(
            f"API endpoint {url} did not return status {expected_status} within {timeout} seconds"
        )
