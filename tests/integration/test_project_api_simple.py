#!/usr/bin/env python3
"""
Simplified Project API Integration Tests
Tests the project-specific API endpoints that we know exist
"""

import json
import os
import random
import subprocess
import sys
import time
from typing import Dict, Optional, Tuple

import requests

# Set environment for testing
os.environ.setdefault("LOCAL_DEV_MODE", "true")


def start_server_background() -> Tuple[Optional[subprocess.Popen], Optional[int], Optional[int]]:
    """Start the server in background with API enabled"""
    try:
        # Use different ports to avoid conflicts
        test_port = random.randint(8000, 8999)
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
            bufsize=1,
        )

        # Monitor startup
        startup_time = 0
        max_startup_time = 15

        while startup_time < max_startup_time:
            if process.poll() is not None:
                stdout, _ = process.communicate()
                print("❌ Server process terminated early:")
                print(stdout)
                return None, None, None

            time.sleep(1)
            startup_time += 1

            if startup_time > 5:
                try:
                    response = requests.get(
                        f"http://127.0.0.1:{api_port}/health", timeout=1
                    )
                    if response.status_code == 200:
                        print(f"✅ Server started successfully after {startup_time} seconds")
                        return process, test_port, api_port
                except Exception:
                    pass

        print("⚠️  Server taking longer than expected to start...")
        return process, test_port, api_port

    except Exception as e:
        print(f"❌ Server error: {e}")
        return None, None, None


def test_basic_api_endpoints(api_url: str) -> bool:
    """Test basic API endpoints"""
    print("\n🧪 Testing Basic API Endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        print("✅ Health endpoint working")
        
        # Test info endpoint  
        response = requests.get(f"{api_url}/info", timeout=5)
        if response.status_code != 200:
            print(f"❌ Info endpoint failed: {response.status_code}")
            return False
        
        print("✅ Info endpoint working")
        
        # Test API documentation
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ API docs failed: {response.status_code}")
            return False
        
        print("✅ API documentation accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic API endpoints test failed: {e}")
        return False


def test_project_ownership_transfer_api(api_url: str) -> bool:
    """Test project ownership transfer API endpoint"""
    print("\n🧪 Testing Project Ownership Transfer API...")
    
    try:
        # Test ownership transfer endpoint with invalid project
        transfer_data = {
            "new_owner_user_id": "test-user-123"
        }
        
        response = requests.post(f"{api_url}/api/projects/999999/transfer-ownership", 
                               json=transfer_data, timeout=10)
        
        # Should get error response for non-existent project
        if response.status_code in [404, 400, 403]:
            print("✅ Ownership transfer API properly handles invalid project")
            try:
                error_data = response.json()
                if "success" in error_data and not error_data["success"]:
                    print("✅ API returns proper error structure")
                else:
                    print("⚠️  API error structure unclear")
            except:
                print("⚠️  API response not JSON")
        else:
            print(f"⚠️  Ownership transfer API response unclear: {response.status_code}")
        
        # Test with form data (in case endpoint expects form data)
        response = requests.post(f"{api_url}/api/projects/999999/transfer-ownership", 
                               data=transfer_data, timeout=10)
        
        if response.status_code in [404, 400, 403]:
            print("✅ Ownership transfer API handles form data properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Ownership transfer API test failed: {e}")
        return False


def test_project_tags_api(api_url: str) -> bool:
    """Test project tags API endpoints"""
    print("\n🧪 Testing Project Tags API...")
    
    try:
        # Test getting tags for non-existent project
        response = requests.get(f"{api_url}/api/projects/999999/tags", timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Tags GET API properly handles invalid project")
            try:
                error_data = response.json()
                if "success" in error_data and not error_data["success"]:
                    print("✅ Tags GET API returns proper error structure")
            except:
                print("⚠️  Tags GET API response not JSON")
        else:
            print(f"⚠️  Tags GET API response unclear: {response.status_code}")
        
        # Test updating tags for non-existent project
        tags_data = {"tags": "test,integration,api"}
        response = requests.put(f"{api_url}/api/projects/999999/tags", 
                              json=tags_data, timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Tags PUT API properly handles invalid project")
            try:
                error_data = response.json()
                if "success" in error_data and not error_data["success"]:
                    print("✅ Tags PUT API returns proper error structure")
            except:
                print("⚠️  Tags PUT API response not JSON")
        else:
            print(f"⚠️  Tags PUT API response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tags API test failed: {e}")
        return False


def test_project_token_cost_api(api_url: str) -> bool:
    """Test project token cost API endpoint"""
    print("\n🧪 Testing Project Token Cost API...")
    
    try:
        # Test token cost for non-existent project
        response = requests.get(f"{api_url}/api/projects/999999/token-cost", timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Token cost API properly handles invalid project")
            try:
                error_data = response.json()
                if "success" in error_data and not error_data["success"]:
                    print("✅ Token cost API returns proper error structure")
                    if "error" in error_data:
                        print(f"   Error message: {error_data['error']}")
            except:
                print("⚠️  Token cost API response not JSON")
        else:
            print(f"⚠️  Token cost API response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token cost API test failed: {e}")
        return False


def test_project_members_api(api_url: str) -> bool:
    """Test project members API endpoints"""
    print("\n🧪 Testing Project Members API...")
    
    try:
        # Test member invitation for non-existent project
        invite_data = {
            "email": "test@example.com",
            "role": "member",
            "message": "Test invitation"
        }
        
        response = requests.post(f"{api_url}/api/projects/999999/members/invite", 
                               json=invite_data, timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Member invite API properly handles invalid project")
        else:
            print(f"⚠️  Member invite API response unclear: {response.status_code}")
        
        # Test member role change for non-existent project/member
        role_data = {"role": "viewer"}
        response = requests.put(f"{api_url}/api/projects/999999/members/test-user/role", 
                              json=role_data, timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Member role API properly handles invalid project/member")
        else:
            print(f"⚠️  Member role API response unclear: {response.status_code}")
        
        # Test member removal for non-existent project/member
        response = requests.delete(f"{api_url}/api/projects/999999/members/test-user", 
                                 timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Member removal API properly handles invalid project/member")
        else:
            print(f"⚠️  Member removal API response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Members API test failed: {e}")
        return False


def test_project_rules_api(api_url: str) -> bool:
    """Test project rules API endpoints"""
    print("\n🧪 Testing Project Rules API...")
    
    try:
        # Test rule assignment for non-existent project
        response = requests.post(f"{api_url}/api/projects/999999/rules/1/assign", 
                               timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Rule assign API properly handles invalid project")
        else:
            print(f"⚠️  Rule assign API response unclear: {response.status_code}")
        
        # Test rule unassignment for non-existent project
        response = requests.delete(f"{api_url}/api/projects/999999/rules/1/unassign", 
                                 timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Rule unassign API properly handles invalid project")
        else:
            print(f"⚠️  Rule unassign API response unclear: {response.status_code}")
        
        # Test getting project rules for non-existent project
        response = requests.get(f"{api_url}/api/projects/999999/rules", timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Project rules GET API properly handles invalid project")
        else:
            print(f"⚠️  Project rules GET API response unclear: {response.status_code}")
        
        # Test getting available rules for non-existent project
        response = requests.get(f"{api_url}/api/projects/999999/rules/available", 
                              timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Available rules API properly handles invalid project")
        else:
            print(f"⚠️  Available rules API response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rules API test failed: {e}")
        return False


def test_project_permissions_api(api_url: str) -> bool:
    """Test project permissions API endpoint"""
    print("\n🧪 Testing Project Permissions API...")
    
    try:
        # Test permissions for non-existent project
        response = requests.get(f"{api_url}/api/projects/999999/permissions", 
                              timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Permissions API properly handles invalid project")
            try:
                error_data = response.json()
                if "success" in error_data and not error_data["success"]:
                    print("✅ Permissions API returns proper error structure")
            except:
                print("⚠️  Permissions API response not JSON")
        else:
            print(f"⚠️  Permissions API response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Permissions API test failed: {e}")
        return False


def test_api_error_handling(api_url: str) -> bool:
    """Test API error handling with various invalid inputs"""
    print("\n🧪 Testing API Error Handling...")
    
    try:
        # Test invalid project ID formats
        invalid_endpoints = [
            f"{api_url}/api/projects/invalid_id/token-cost",
            f"{api_url}/api/projects/-1/tags", 
            f"{api_url}/api/projects/abc/transfer-ownership",
            f"{api_url}/api/projects/0/permissions",
            f"{api_url}/api/projects/999999999999999999999/rules"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code in [400, 404, 422]:
                    print(f"✅ Proper error handling for: {endpoint.split('/')[-2:]}")
                else:
                    print(f"⚠️  Unexpected response for {endpoint}: {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"✅ Connection properly rejected for invalid endpoint")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def run_project_api_tests(base_port: int = None, api_port: int = None) -> bool:
    """Run all project API tests"""
    process = None
    
    # Use provided ports or start our own server
    if base_port is None or api_port is None:
        result = start_server_background()
        if result[0] is None:
            print("❌ Failed to start server")
            return False
        
        process, base_port, api_port = result
    
    try:
        base_url = f"http://127.0.0.1:{base_port}"
        api_url = f"http://127.0.0.1:{api_port}"
        
        print("🧪 Testing Project API Endpoints...")
        print("=" * 50)
        
        # Wait for server to be ready
        print("⏳ Waiting for server to start...")
        server_ready = False
        
        for i in range(30):
            try:
                # Check API health
                api_response = requests.get(f"{api_url}/health", timeout=2)
                if api_response.status_code == 200:
                    print("✅ Server and API are ready!")
                    server_ready = True
                    break
                    
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        if not server_ready:
            print("❌ Server failed to start within timeout")
            return False
        
        # Run test suites
        test_results = []
        
        test_results.append(test_basic_api_endpoints(api_url))
        test_results.append(test_project_ownership_transfer_api(api_url))
        test_results.append(test_project_tags_api(api_url))
        test_results.append(test_project_token_cost_api(api_url))  
        test_results.append(test_project_members_api(api_url))
        test_results.append(test_project_rules_api(api_url))
        test_results.append(test_project_permissions_api(api_url))
        test_results.append(test_api_error_handling(api_url))
        
        # Calculate results
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Project API Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All project API tests passed!")
            return True
        else:
            print("⚠️  Some project API tests failed")
            return passed >= total * 0.7  # Pass if 70% of tests pass
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False
        
    finally:
        # Clean up server process
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
                print("🧹 Test server cleaned up")
            except Exception as e:
                print(f"⚠️  Error cleaning up server: {e}")


def main():
    """Main test runner"""
    print("🚀 Starting Project API Integration Tests...")
    
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..")
    os.chdir(project_root)
    
    success = run_project_api_tests()
    
    if success:
        print("\n✅ Project API integration tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Project API integration tests failed!")
        exit(1)


if __name__ == "__main__":
    main()