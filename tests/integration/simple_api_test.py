#!/usr/bin/env python3
"""
Simple API test - start server manually and test endpoints
"""

import requests
import time

def test_endpoints():
    """Test API endpoints against running server"""
    base_url = "http://127.0.0.1:7860"
    
    print("🧪 Testing API endpoints...")
    print("⚠️  Make sure server is running: poetry run python run_mt_with_api.py")
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        print("   Make sure server is running!")
        return False
    
    # Test 2: Authentication requirement
    print("\n2. Testing authentication requirement...")
    try:
        response = requests.get(f"{base_url}/api/prompts")
        if response.status_code in [401, 403]:
            print("✅ Authentication required (as expected)")
        else:
            print(f"❌ Expected 401/403, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    # Test 3: API documentation
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs test error: {e}")
        return False
    
    # Test 4: Gradio web interface
    print("\n4. Testing Gradio web interface...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Gradio web interface accessible")
        else:
            print(f"❌ Gradio interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gradio interface test error: {e}")
        return False
    
    print("\n🎉 All API tests passed!")
    print("\nNext steps:")
    print("1. Open web UI: http://localhost:7860")
    print("2. Login with: admin@localhost / admin123") 
    print("3. Go to Account Settings → API Tokens")
    print("4. Create a new API token")
    print("5. Test with: curl -H 'Authorization: Bearer apm_your_token' http://localhost:7860/api/prompts")
    
    return True

if __name__ == "__main__":
    test_endpoints()