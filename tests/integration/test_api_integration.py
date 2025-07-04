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

        os.environ["MULTITENANT_MODE"] = "true"
        os.environ["ENABLE_API"] = "true"

        # Import the unified run module
        import argparse

        from run import get_configuration

        # Create mock args for multi-tenant + API mode
        class MockArgs:
            single_user = False
            multi_tenant = True
            with_api = True
            host = "127.0.0.1"
            port = 7860
            debug = True
            share = False

        args = MockArgs()
        config = get_configuration(args)

        # Create the Gradio interface
        from prompt_manager import create_interface

        app = create_interface()

        # Add API integration
        if config["enable_api"]:
            from api_endpoints import APIManager

            api_manager = APIManager()
            api_router = api_manager.get_router()
            app.app.include_router(api_router, prefix="/api")

        # Launch the app
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=False,
            quiet=True,  # Reduce log noise
        )
    except Exception as e:
        print(f"❌ Server error: {e}")


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
    print("1. Start the server: poetry run python run_mt_with_api.py")
    print("2. Open web UI: http://localhost:7860")
    print("3. Login with: admin@localhost / admin123")
    print("4. Create API tokens in Account Settings")
    print("5. Use API: http://localhost:7860/api/docs")

    return True


def main():
    """Main test function"""
    print("🚀 AI Prompt Manager API Integration Test")
    print("=" * 50)

    # Start server in background thread
    server_thread = threading.Thread(target=start_server_background, daemon=True)
    server_thread.start()

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


if __name__ == "__main__":
    exit(main())
