#!/usr/bin/env python3
"""
Test the standalone API endpoints
"""

import os
import threading
import time

import requests

# Set environment for testing
os.environ.setdefault("LOCAL_DEV_MODE", "true")


def start_api_server():
    """Start just the API server"""
    try:
        import sys

        import uvicorn

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from api_endpoints import get_api_app

        app = get_api_app()
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=7861,  # Different port to avoid conflicts
            log_level="warning",
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"❌ API Server error: {e}")


def test_standalone_api():
    """Test standalone API"""
    base_url = "http://127.0.0.1:7861"

    print("🧪 Testing Standalone API...")

    # Start API server in background
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("⏳ Waiting for API server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready!")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        print("❌ API server failed to start")
        return False

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test authentication requirement
    print("\n2. Testing authentication...")
    try:
        response = requests.get(f"{base_url}/api/prompts")
        if response.status_code in [401, 403]:
            print("✅ Authentication required")
        else:
            print(f"❌ Expected auth error, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False

    # Test API docs
    print("\n3. Testing API docs...")
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            print("✅ API docs accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

    print("\n🎉 Standalone API tests passed!")
    return True


if __name__ == "__main__":
    test_standalone_api()
