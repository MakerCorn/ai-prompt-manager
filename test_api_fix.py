#!/usr/bin/env python3
"""
Test script to verify API endpoints work
"""
import os
import subprocess
import sys
import time
from datetime import datetime

import requests

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")

    # Set environment for testing
    env = os.environ.copy()
    env["MULTITENANT_MODE"] = "false"
    env["ENABLE_API"] = "true"
    env["LOCAL_DEV_MODE"] = "true"

    # Start server in background
    process = None
    try:
        print("🚀 Starting server...")
        cmd = [
            sys.executable,
            "run.py",
            "--with-api",
            "--debug",
            "--host",
            "127.0.0.1",
            "--port",
            "7862",
        ]

        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # Wait for server to start
        print("⏳ Waiting for server startup...")

        # Wait for server to be ready
        max_wait = 30
        wait_time = 0
        server_ready = False

        while wait_time < max_wait:
            time.sleep(2)
            wait_time += 2

            # Check if server is responding
            try:
                response = requests.get(f"http://127.0.0.1:7862/", timeout=3)
                if response.status_code in [200, 404]:  # 404 is ok, means server is up
                    server_ready = True
                    print(f"✅ Server is responding after {wait_time}s")
                    break
            except requests.exceptions.RequestException:
                print(f"⏳ Still waiting... ({wait_time}s)")
                continue

        if not server_ready:
            print("❌ Server failed to start within timeout")
            if process.poll() is not None:
                stdout, _ = process.communicate()
                print("Server output:")
                print(stdout)
            return False

        # Test if process is still running
        if process.poll() is not None:
            stdout, _ = process.communicate()
            print("❌ Server failed to start:")
            print(stdout)
            return False

        # Test API endpoints
        base_url = "http://127.0.0.1:7862"

        print("🔍 Testing /api/health endpoint...")
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check successful: {data}")
            else:
                print(
                    f"❌ Health check failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

        print("🔍 Testing /api/test endpoint...")
        try:
            response = requests.get(f"{base_url}/api/test", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test endpoint successful: {data}")
            else:
                print(
                    f"❌ Test endpoint failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            print(f"❌ Test endpoint error: {e}")
            return False

        print("✅ All API tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        if process:
            print("🛑 Stopping server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
