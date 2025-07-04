#!/usr/bin/env python3
"""
Test script for API integration
Tests the combined Gradio + FastAPI application
"""

import os
import threading
import time

import requests

# Set environment for testing
os.environ.setdefault("LOCAL_DEV_MODE", "true")


def start_server_background():
    """Start the server in background"""
    try:
        # Set environment for multi-tenant mode with API
        import os

        # Use the unified run.py launcher directly
        # This is more reliable than trying to replicate the logic
        # Use different ports to avoid conflicts
        import random
        import subprocess
        import sys

        test_port = random.randint(8000, 8999)
        # API runs on separate port (port + 1)
        api_port = test_port + 1

        cmd = [
            sys.executable,
            "run.py",
            "--with-api",
            "--host",
            "127.0.0.1",
            "--port",
            str(test_port),
            "--debug",
        ]

        # Set environment variables
        env = os.environ.copy()
        env["MULTITENANT_MODE"] = "true"
        env["ENABLE_API"] = "true"
        env["LOCAL_DEV_MODE"] = "true"

        # Start the process
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )

        # Monitor startup output
        import time

        startup_time = 0
        max_startup_time = 15

        while startup_time < max_startup_time:
            if process.poll() is not None:
                # Process has terminated
                stdout, _ = process.communicate()
                print(f"❌ Server process terminated early:")
                print(stdout)
                return None, None, None

            time.sleep(1)
            startup_time += 1

            # Try a quick health check on separate API port
            if startup_time > 5:  # Give it at least 5 seconds
                try:
                    import requests

                    response = requests.get(
                        f"http://127.0.0.1:{api_port}/health", timeout=1
                    )
                    if response.status_code == 200:
                        print(
                            f"✅ Server started successfully after {startup_time} seconds"
                        )
                        return process, test_port, api_port
                except:
                    pass  # Continue waiting

        print(f"⚠️  Server taking longer than expected to start...")
        return process, test_port, api_port

    except Exception as e:
        print(f"❌ Server error: {e}")
        return None, None, None


def test_api_endpoints(base_port, api_port):
    """Test API endpoints"""
    base_url = f"http://127.0.0.1:{base_port}"
    # API is on separate port
    api_url = f"http://127.0.0.1:{api_port}"

    print("🧪 Testing API Integration...")
    print("=" * 50)

    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    server_ready = False

    for i in range(30):  # Wait up to 30 seconds
        try:
            # First check if basic Gradio server is up
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                print(f"📱 Gradio interface is up (attempt {i+1})")

                # Now check API health endpoint on separate port
                try:
                    api_response = requests.get(f"{api_url}/health", timeout=2)
                    if api_response.status_code == 200:
                        print("✅ Server and API are ready!")
                        server_ready = True
                        break
                    else:
                        print(f"⏳ API not ready yet: {api_response.status_code}")
                except requests.exceptions.RequestException as api_e:
                    print(f"⏳ API endpoint not available yet: {api_e}")
            else:
                print(f"⏳ Server not ready: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"⏳ Connection attempt {i+1}: {type(e).__name__}")

        time.sleep(1)

    if not server_ready:
        print("❌ Server failed to start within 30 seconds")
        return False

    # Test 1: Basic server connectivity
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Gradio server is accessible")
        else:
            print(f"❌ Server check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connectivity error: {e}")
        return False

    # Test 2: Check if application is in correct mode
    print("\n2. Testing application mode...")
    try:
        response = requests.get(base_url)
        if "AI Prompt Manager" in response.text:
            print("✅ Application title found")

            # Check for login form presence (indicates multi-tenant mode)
            if "login" in response.text.lower() or "password" in response.text.lower():
                print("✅ Multi-tenant mode detected (login form present)")
            else:
                print("ℹ️  Single-user mode detected (no login form)")
        else:
            print("❌ Application doesn't appear to be AI Prompt Manager")
            return False
    except Exception as e:
        print(f"❌ Mode detection error: {e}")
        return False

    # Test 3: API health check
    print("\n3. Testing API health endpoint...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health check passed")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

    # Test 4: API info endpoint
    print("\n4. Testing API info endpoint...")
    try:
        response = requests.get(f"{api_url}/info", timeout=5)
        if response.status_code == 200:
            print("✅ API info endpoint accessible")
            data = response.json()
            print(f"   Service: {data.get('service', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ Basic server integration test completed!")
    print()
    print("Summary:")
    print("- ✅ Unified launcher (run.py) works correctly")
    print("- ✅ Server starts and responds to requests")
    print("- ✅ Application loads with correct title")
    print("- ✅ API integration with dual-server architecture")
    print(f"- ✅ API server runs on port 7861 (main port + 1)")
    print()
    print("API Endpoints Available:")
    print(f"- Health: {api_url}/health")
    print(f"- Info: {api_url}/info")
    print(f"- Docs: {api_url}/docs")
    print(f"- Root: {api_url}/")

    return True


def main():
    """Main test function"""
    print("🚀 AI Prompt Manager API Integration Test")
    print("=" * 50)

    # Start server process
    server_process, base_port, api_port = start_server_background()
    if not server_process:
        print("❌ Failed to start server process")
        return False

    try:
        # Run tests
        success = test_api_endpoints(base_port, api_port)

        if success:
            print("\n✅ Integration test completed successfully!")
            return 0
        else:
            print("\n❌ Integration test failed!")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return 1
    finally:
        # Clean up server process
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
                print("🧹 Server process cleaned up")
            except:
                server_process.kill()
                print("🧹 Server process forcefully terminated")


if __name__ == "__main__":
    exit(main())
