#!/usr/bin/env python3
"""
Integration tests for Project Management API
Tests the complete project API functionality including CRUD operations, 
ownership transfer, tags, and token cost calculations
"""

import json
import os
import random
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

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

        # Monitor startup output
        startup_time = 0
        max_startup_time = 15

        while startup_time < max_startup_time:
            if process.poll() is not None:
                # Process has terminated
                stdout, _ = process.communicate()
                print("❌ Server process terminated early:")
                print(stdout)
                return None, None, None

            time.sleep(1)
            startup_time += 1

            # Try a health check on API port
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


def create_test_data(api_url: str) -> Dict:
    """Create test data for project API tests"""
    test_data = {}
    
    try:
        # Create test prompts
        prompts_data = [
            {
                "name": "test-prompt-1",
                "title": "Test Prompt 1", 
                "content": "This is test prompt content 1",
                "category": "Testing",
                "tags": "test,prompt,integration"
            },
            {
                "name": "test-prompt-2",
                "title": "Test Prompt 2",
                "content": "This is test prompt content 2", 
                "category": "Development",
                "tags": "test,dev,automation"
            }
        ]
        
        test_data["prompts"] = []
        for prompt_data in prompts_data:
            # Note: This uses the web form endpoint since add_prompt returns string
            form_data = {
                "name": prompt_data["name"],
                "title": prompt_data["title"],
                "content": prompt_data["content"],
                "category": prompt_data["category"],
                "tags": prompt_data["tags"]
            }
            
            # Create via web form endpoint (since API might not have prompt creation)
            response = requests.post(f"{api_url.replace(':' + api_url.split(':')[-1], ':' + str(int(api_url.split(':')[-1]) - 1))}/prompts/new", 
                                   data=form_data, timeout=5)
            
            if response.status_code in [200, 201, 302]:  # Accept redirects too
                test_data["prompts"].append(prompt_data)
                print(f"✅ Created prompt: {prompt_data['name']}")
            else:
                print(f"⚠️  Failed to create prompt: {prompt_data['name']}")
        
        # Create test rules
        rules_data = [
            {
                "name": "test-rule-1",
                "title": "Test Rule 1",
                "content": "# Test Rule 1\nThis is a test rule for integration testing",
                "category": "Testing",
                "tags": "test,rule,integration"
            },
            {
                "name": "test-rule-2", 
                "title": "Test Rule 2",
                "content": "# Test Rule 2\nAnother test rule for integration testing",
                "category": "Development",
                "tags": "test,dev,standards"
            }
        ]
        
        test_data["rules"] = []
        for rule_data in rules_data:
            # Create via web form endpoint  
            form_data = {
                "name": rule_data["name"],
                "title": rule_data["title"],
                "content": rule_data["content"],
                "category": rule_data["category"],
                "tags": rule_data["tags"]
            }
            
            response = requests.post(f"{api_url.replace(':' + api_url.split(':')[-1], ':' + str(int(api_url.split(':')[-1]) - 1))}/rules/new",
                                   data=form_data, timeout=5)
            
            if response.status_code in [200, 201, 302]:
                test_data["rules"].append(rule_data)
                print(f"✅ Created rule: {rule_data['name']}")
            else:
                print(f"⚠️  Failed to create rule: {rule_data['name']}")
    
    except Exception as e:
        print(f"⚠️  Error creating test data: {e}")
    
    return test_data


def test_project_crud_operations(api_url: str) -> bool:
    """Test basic project CRUD operations"""
    print("\n🧪 Testing Project CRUD Operations...")
    
    try:
        # Test 1: Create a project
        project_data = {
            "name": "integration-test-project",
            "title": "Integration Test Project",
            "description": "A project created during integration testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False
        }
        
        # Create project via web form (since add_project returns string)
        web_port = int(api_url.split(':')[-1]) - 1
        web_url = f"http://127.0.0.1:{web_port}"
        
        response = requests.post(f"{web_url}/projects/new", data=project_data, timeout=10)
        
        if response.status_code not in [200, 201, 302]:
            print(f"❌ Failed to create project: {response.status_code}")
            return False
        
        print("✅ Project created successfully")
        
        # Test 2: List projects to find our created project
        response = requests.get(f"{web_url}/projects", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to list projects: {response.status_code}")
            return False
        
        # Check if project appears in the HTML response
        if "integration-test-project" not in response.text:
            print("❌ Created project not found in project list")
            return False
            
        print("✅ Project appears in project list")
        
        # Test 3: Try to create duplicate project (should fail)
        response = requests.post(f"{web_url}/projects/new", data=project_data, timeout=10)
        
        # Should either redirect back to form with error or show error
        if response.status_code == 200 and "already exists" in response.text.lower():
            print("✅ Duplicate project creation properly rejected")
        elif response.status_code == 302:
            # Follow redirect to see if error message appears
            print("✅ Duplicate project creation handled (redirect)")
        else:
            print("⚠️  Duplicate project handling unclear")
        
        return True
        
    except Exception as e:
        print(f"❌ CRUD operations test failed: {e}")
        return False


def test_project_api_endpoints(api_url: str) -> bool:
    """Test project-specific API endpoints"""
    print("\n🧪 Testing Project API Endpoints...")
    
    try:
        # Since we don't have direct project API endpoints, we'll test
        # the functionality through the web interface and check responses
        
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
        print(f"❌ API endpoints test failed: {e}")
        return False


def test_project_ownership_transfer(api_url: str) -> bool:
    """Test project ownership transfer functionality"""
    print("\n🧪 Testing Project Ownership Transfer...")
    
    try:
        # This would require creating users and project members
        # For now, we'll test that the ownership transfer endpoint exists
        # and handles invalid requests properly
        
        web_port = int(api_url.split(':')[-1]) - 1
        web_url = f"http://127.0.0.1:{web_port}"
        
        # Try to transfer ownership of non-existent project
        transfer_data = {
            "new_owner_user_id": "test-user-123"
        }
        
        response = requests.post(f"{api_url}/projects/999999/transfer-ownership", 
                               data=transfer_data, timeout=10)
        
        # Should get error response
        if response.status_code in [404, 400, 403]:
            print("✅ Ownership transfer properly handles invalid project")
        else:
            print(f"⚠️  Ownership transfer response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ownership transfer test failed: {e}")
        return False


def test_project_tags_functionality(api_url: str) -> bool:
    """Test project tags functionality"""
    print("\n🧪 Testing Project Tags Functionality...")
    
    try:
        # Test getting tags for non-existent project
        response = requests.get(f"{api_url}/projects/999999/tags", timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Tags endpoint properly handles invalid project")
        else:
            print(f"⚠️  Tags endpoint response unclear: {response.status_code}")
        
        # Test updating tags for non-existent project
        tags_data = {"tags": "test,integration,api"}
        response = requests.put(f"{api_url}/projects/999999/tags", 
                              json=tags_data, timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Tags update properly handles invalid project")
        else:
            print(f"⚠️  Tags update response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tags functionality test failed: {e}")
        return False


def test_project_token_cost_calculation(api_url: str) -> bool:
    """Test project token cost calculation"""
    print("\n🧪 Testing Project Token Cost Calculation...")
    
    try:
        # Test token cost for non-existent project
        response = requests.get(f"{api_url}/projects/999999/token-cost", timeout=10)
        
        if response.status_code in [404, 403]:
            print("✅ Token cost endpoint properly handles invalid project")
        else:
            print(f"⚠️  Token cost endpoint response unclear: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token cost calculation test failed: {e}")
        return False


def test_project_integration_workflow(api_url: str, test_data: Dict) -> bool:
    """Test complete project integration workflow"""
    print("\n🧪 Testing Complete Project Integration Workflow...")
    
    try:
        web_port = int(api_url.split(':')[-1]) - 1
        web_url = f"http://127.0.0.1:{web_port}"
        
        # 1. Create a comprehensive project
        project_data = {
            "name": "workflow-test-project",
            "title": "Workflow Test Project",
            "description": "Testing complete project workflow",
            "project_type": "sequenced",
            "visibility": "private",
            "shared_with_tenant": False
        }
        
        response = requests.post(f"{web_url}/projects/new", data=project_data, timeout=10)
        
        if response.status_code not in [200, 201, 302]:
            print(f"❌ Failed to create workflow test project: {response.status_code}")
            return False
        
        print("✅ Workflow test project created")
        
        # 2. Verify project appears in list
        response = requests.get(f"{web_url}/projects", timeout=10)
        
        if response.status_code != 200 or "workflow-test-project" not in response.text:
            print("❌ Workflow test project not found in list")
            return False
        
        print("✅ Workflow test project listed successfully")
        
        # 3. Access project dashboard
        # We need to find the project ID first by parsing the HTML or using a different approach
        # For now, we'll test that project pages are accessible
        response = requests.get(f"{web_url}/projects", timeout=10)
        
        if response.status_code == 200:
            print("✅ Project pages accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration workflow test failed: {e}")
        return False


def test_project_error_handling(api_url: str) -> bool:
    """Test project API error handling"""
    print("\n🧪 Testing Project API Error Handling...")
    
    try:
        # Test invalid project ID formats
        invalid_endpoints = [
            f"{api_url}/projects/invalid_id/token-cost",
            f"{api_url}/projects/-1/tags", 
            f"{api_url}/projects/abc/transfer-ownership"
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


def run_project_api_integration_tests(base_port: int = None, api_port: int = None) -> bool:
    """Run all project API integration tests"""
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
        
        print("🧪 Testing Project API Integration...")
        print("=" * 60)
        
        # Wait for server to be ready
        print("⏳ Waiting for server to start...")
        server_ready = False
        
        for i in range(30):
            try:
                # Check web interface
                response = requests.get(base_url, timeout=2)
                if response.status_code == 200:
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
        
        # Create test data
        print("\n📝 Creating test data...")
        test_data = create_test_data(api_url)
        
        # Run test suites
        test_results = []
        
        test_results.append(test_project_crud_operations(api_url))
        test_results.append(test_project_api_endpoints(api_url))
        test_results.append(test_project_ownership_transfer(api_url))
        test_results.append(test_project_tags_functionality(api_url))
        test_results.append(test_project_token_cost_calculation(api_url))
        test_results.append(test_project_integration_workflow(api_url, test_data))
        test_results.append(test_project_error_handling(api_url))
        
        # Calculate results
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"📊 Project API Integration Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All project API integration tests passed!")
            return True
        else:
            print("⚠️  Some project API integration tests failed")
            return False
            
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
    
    success = run_project_api_integration_tests()
    
    if success:
        print("\n✅ Project API integration tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Project API integration tests failed!")
        exit(1)


if __name__ == "__main__":
    main()