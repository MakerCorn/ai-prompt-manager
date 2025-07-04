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
        import sys
        import subprocess

        # Use the unified run.py launcher directly
        # This is more reliable than trying to replicate the logic
        cmd = [
            sys.executable, "run.py",
            "--with-api",
            "--host", "127.0.0.1", 
            "--port", "7860",
            "--debug"
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
            universal_newlines=True
        )
        
        # Give it time to start
        import time
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        return None


def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://127.0.0.1:7860"

    print("🧪 Testing API Integration...")
    print("=" * 50)

    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        print("❌ Server failed to start within 30 seconds")
        return False

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test 2: Try to access API without authentication (should fail)
    print("\n2. Testing authentication requirement...")
    try:
        response = requests.get(f"{base_url}/api/prompts")
        if response.status_code in [401, 403]:  # Both are valid for auth failure
            print("✅ Authentication required (as expected)")
        else:
            print(f"❌ Expected 401 or 403, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

    # Test 3: Check API documentation is available
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs test error: {e}")
        return False

    # Test 4: Check Gradio web interface is available
    print("\n4. Testing Gradio web interface...")
    try:
        response = requests.get(base_url, timeout=5)
        if (
            response.status_code == 200
            and "Multi-Tenant AI Prompt Manager" in response.text
        ):
            print("✅ Gradio web interface is accessible")
        else:
            print(f"❌ Gradio interface test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gradio interface test error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All tests passed! API integration is working correctly.")
    print()
    print("Next steps:")
    print("1. Start the server: poetry run python run.py --with-api")
    print("2. Open web UI: http://localhost:7860")
    print("3. Login with: admin@localhost / admin123")
    print("4. Create API tokens in Account Settings")
    print("5. Use API: http://localhost:7860/api/docs")

    return True


def main():
    """Main test function"""
    print("🚀 AI Prompt Manager API Integration Test")
    print("=" * 50)

    # Start server process
    server_process = start_server_background()
    if not server_process:
        print("❌ Failed to start server process")
        return False

    try:
        # Run tests
        success = test_api_endpoints()

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
