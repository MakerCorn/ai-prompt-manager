#!/usr/bin/env python3
"""
Project Workflow Integration Tests
Tests complete project workflows using single-user mode for easier testing
"""

import json
import os
import random
import re
import subprocess
import sys
import time
from typing import Dict, Optional, Tuple

import requests
from requests.sessions import Session

# Set environment for testing
os.environ.setdefault("LOCAL_DEV_MODE", "true")


def start_single_user_server() -> (
    Tuple[Optional[subprocess.Popen], Optional[int], Optional[int]]
):
    """Start the server in single-user mode with API enabled"""
    try:
        # Use different ports to avoid conflicts
        test_port = random.randint(8000, 8999)
        api_port = test_port + 1

        cmd = [
            sys.executable,
            "run.py",
            "--single-user",
            "--with-api",
            "--host",
            "127.0.0.1",
            "--port",
            str(test_port),
            "--debug",
        ]

        # Set environment variables for single-user mode
        env = os.environ.copy()
        env["MULTITENANT_MODE"] = "false"
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
                print(stdout[-1000:])  # Show last 1000 chars
                return None, None, None

            time.sleep(1)
            startup_time += 1

            if startup_time > 5:
                try:
                    response = requests.get(
                        f"http://127.0.0.1:{api_port}/health", timeout=1
                    )
                    if response.status_code == 200:
                        print(
                            f"✅ Single-user server started after {startup_time} seconds"
                        )
                        return process, test_port, api_port
                except Exception:
                    pass

        print("⚠️  Server taking longer than expected to start...")
        return process, test_port, api_port

    except Exception as e:
        print(f"❌ Server error: {e}")
        return None, None, None


def extract_project_id_from_html(html_content: str, project_name: str) -> Optional[int]:
    """Extract project ID from HTML content"""
    try:
        # Look for project links that contain the project name
        # Pattern: /projects/{id} where the link text or nearby text contains project_name
        patterns = [
            rf"/projects/(\d+).*?{re.escape(project_name)}",
            rf"{re.escape(project_name)}.*?/projects/(\d+)",
            rf'href="[^"]*?/projects/(\d+)[^"]*?"[^>]*>[^<]*{re.escape(project_name)}',
        ]

        for pattern in patterns:
            matches = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                return int(matches.group(1))

        # Fallback: look for any project ID in the HTML
        matches = re.findall(r"/projects/(\d+)", html_content)
        if matches:
            return int(matches[0])  # Return first found ID

        return None
    except Exception:
        return None


def create_test_project(session: Session, base_url: str) -> Optional[int]:
    """Create a test project and return its ID"""
    try:
        project_data = {
            "name": "workflow-test-project",
            "title": "Workflow Test Project",
            "description": "A project created for workflow integration testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
        }

        # Create project
        response = session.post(
            f"{base_url}/projects/new", data=project_data, timeout=10
        )

        if response.status_code not in [200, 201, 302]:
            print(f"❌ Failed to create project: {response.status_code}")
            return None

        # Get project list to find our project ID
        response = session.get(f"{base_url}/projects", timeout=10)

        if response.status_code != 200:
            print(f"❌ Failed to get project list: {response.status_code}")
            return None

        # Extract project ID
        project_id = extract_project_id_from_html(
            response.text, "workflow-test-project"
        )

        if project_id:
            print(f"✅ Created project with ID: {project_id}")
            return project_id
        else:
            print("❌ Could not extract project ID")
            return None

    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None


def create_test_content(session: Session, base_url: str) -> Dict:
    """Create test prompts and rules"""
    content_ids = {"prompts": [], "rules": []}

    try:
        # Create test prompts
        prompts_data = [
            {
                "name": "workflow-prompt-1",
                "title": "Workflow Test Prompt 1",
                "content": "This is test content for workflow prompt 1. "
                + "A" * 200,  # Adds to token count
                "category": "Testing",
                "tags": "workflow,test,integration",
            },
            {
                "name": "workflow-prompt-2",
                "title": "Workflow Test Prompt 2",
                "content": "This is test content for workflow prompt 2. "
                + "B" * 300,  # Adds to token count
                "category": "Development",
                "tags": "workflow,dev,automation",
            },
        ]

        for prompt_data in prompts_data:
            response = session.post(
                f"{base_url}/prompts/new", data=prompt_data, timeout=10
            )

            if response.status_code in [200, 201, 302]:
                print(f"✅ Created prompt: {prompt_data['name']}")
                content_ids["prompts"].append(prompt_data["name"])
            else:
                print(f"⚠️  Failed to create prompt: {prompt_data['name']}")

        # Create test rules
        rules_data = [
            {
                "name": "workflow-rule-1",
                "title": "Workflow Test Rule 1",
                "content": "# Workflow Test Rule 1\n\nThis is test content for workflow rule 1.\n\n"
                + "C" * 400,  # Adds to token count
                "category": "Testing",
                "tags": "workflow,test,validation",
            },
            {
                "name": "workflow-rule-2",
                "title": "Workflow Test Rule 2",
                "content": "# Workflow Test Rule 2\n\nThis is test content for workflow rule 2.\n\n"
                + "D" * 300,  # Adds to token count
                "category": "Development",
                "tags": "workflow,dev,standards",
            },
        ]

        for rule_data in rules_data:
            response = session.post(f"{base_url}/rules/new", data=rule_data, timeout=10)

            if response.status_code in [200, 201, 302]:
                print(f"✅ Created rule: {rule_data['name']}")
                content_ids["rules"].append(rule_data["name"])
            else:
                print(f"⚠️  Failed to create rule: {rule_data['name']}")

    except Exception as e:
        print(f"❌ Error creating test content: {e}")

    return content_ids


def test_project_token_cost_workflow(api_url: str, project_id: int) -> bool:
    """Test project token cost calculation with real data"""
    print(f"\n🧪 Testing Project Token Cost Workflow (Project {project_id})...")

    try:
        # Get token cost for the project
        response = requests.get(
            f"{api_url}/api/projects/{project_id}/token-cost", timeout=10
        )

        if response.status_code == 200:
            try:
                cost_data = response.json()
                if cost_data.get("success"):
                    print("✅ Token cost API returned successful response")
                    print(f"   Total tokens: {cost_data.get('total_tokens', 'N/A')}")
                    print(f"   Prompt tokens: {cost_data.get('prompt_tokens', 'N/A')}")
                    print(f"   Rule tokens: {cost_data.get('rule_tokens', 'N/A')}")
                    print(f"   Total cost: ${cost_data.get('total_cost', 'N/A')}")

                    # Verify expected structure
                    required_fields = [
                        "total_tokens",
                        "prompt_tokens",
                        "rule_tokens",
                        "total_cost",
                    ]
                    if all(field in cost_data for field in required_fields):
                        print("✅ Token cost response has all required fields")
                        return True
                    else:
                        print("❌ Token cost response missing required fields")
                        return False
                else:
                    print(
                        f"❌ Token cost API returned error: {cost_data.get('error', 'Unknown')}"
                    )
                    return False
            except json.JSONDecodeError:
                print("❌ Token cost API response not valid JSON")
                return False
        else:
            print(f"❌ Token cost API failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Token cost workflow test failed: {e}")
        return False


def test_project_tags_workflow(api_url: str, project_id: int) -> bool:
    """Test project tags workflow with real data"""
    print(f"\n🧪 Testing Project Tags Workflow (Project {project_id})...")

    try:
        # Test getting current tags
        response = requests.get(f"{api_url}/api/projects/{project_id}/tags", timeout=10)

        if response.status_code == 200:
            try:
                tags_data = response.json()
                print("✅ Tags GET API successful")
                print(f"   Project tags: {tags_data.get('project_tags', [])}")
                print(f"   Aggregate tags: {tags_data.get('aggregate_tags', [])}")

                # Test updating project tags
                new_tags = "updated,workflow,integration,test"
                update_data = {"tags": new_tags}

                response = requests.put(
                    f"{api_url}/api/projects/{project_id}/tags",
                    json=update_data,
                    timeout=10,
                )

                if response.status_code == 200:
                    update_result = response.json()
                    if update_result.get("success"):
                        print("✅ Tags PUT API successful")

                        # Verify the update by getting tags again
                        response = requests.get(
                            f"{api_url}/api/projects/{project_id}/tags", timeout=10
                        )
                        if response.status_code == 200:
                            updated_tags_data = response.json()
                            project_tags = updated_tags_data.get("project_tags", [])
                            if set(project_tags) == set(new_tags.split(",")):
                                print("✅ Tags update verified successfully")
                                return True
                            else:
                                print(
                                    f"❌ Tags not updated correctly. Expected: {new_tags.split(',')}, Got: {project_tags}"
                                )
                                return False
                    else:
                        print(f"❌ Tags update failed: {update_result.get('error')}")
                        return False
                else:
                    print(f"❌ Tags PUT API failed: {response.status_code}")
                    return False

            except json.JSONDecodeError:
                print("❌ Tags API response not valid JSON")
                return False
        else:
            print(f"❌ Tags GET API failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Tags workflow test failed: {e}")
        return False


def test_complete_project_workflow(base_url: str, api_url: str) -> bool:
    """Test the complete project workflow from creation to API operations"""
    print("\n🧪 Testing Complete Project Workflow...")

    try:
        # Create a session to maintain cookies
        session = requests.Session()

        # Step 1: Create test content (prompts and rules)
        print("\n📝 Step 1: Creating test content...")
        content_ids = create_test_content(session, base_url)

        if not content_ids["prompts"] or not content_ids["rules"]:
            print("⚠️  Some test content creation failed, continuing anyway...")

        # Step 2: Create a project
        print("\n📁 Step 2: Creating test project...")
        project_id = create_test_project(session, base_url)

        if not project_id:
            print("❌ Failed to create project for workflow test")
            return False

        # Step 3: Test project API endpoints with real data
        print(f"\n🔧 Step 3: Testing API endpoints with project {project_id}...")

        # Test token cost calculation
        token_cost_success = test_project_token_cost_workflow(api_url, project_id)

        # Test tags functionality
        tags_success = test_project_tags_workflow(api_url, project_id)

        # Step 4: Test other API endpoints
        print(f"\n📋 Step 4: Testing additional API endpoints...")

        # Test permissions endpoint
        response = requests.get(
            f"{api_url}/api/projects/{project_id}/permissions", timeout=10
        )
        permissions_success = response.status_code == 200
        if permissions_success:
            print("✅ Permissions API working with real project")
        else:
            print(f"❌ Permissions API failed: {response.status_code}")

        # Calculate overall success
        workflow_success = token_cost_success and tags_success and permissions_success

        if workflow_success:
            print("✅ Complete project workflow test successful")
        else:
            print("❌ Some workflow steps failed")

        return workflow_success

    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False


def run_project_workflow_tests() -> bool:
    """Run all project workflow integration tests"""
    process = None

    try:
        # Start single-user server
        result = start_single_user_server()
        if result[0] is None:
            print("❌ Failed to start single-user server")
            return False

        process, base_port, api_port = result

        base_url = f"http://127.0.0.1:{base_port}"
        api_url = f"http://127.0.0.1:{api_port}"

        print("🧪 Testing Project Workflow Integration...")
        print("=" * 60)

        # Wait for server to be ready
        print("⏳ Waiting for server to start...")
        server_ready = False

        for i in range(30):
            try:
                # Check both web and API
                web_response = requests.get(base_url, timeout=2)
                api_response = requests.get(f"{api_url}/health", timeout=2)

                if web_response.status_code == 200 and api_response.status_code == 200:
                    print("✅ Single-user server and API are ready!")
                    server_ready = True
                    break

            except requests.exceptions.RequestException:
                pass

            time.sleep(1)

        if not server_ready:
            print("❌ Server failed to start within timeout")
            return False

        # Run workflow test
        workflow_success = test_complete_project_workflow(base_url, api_url)

        print("\n" + "=" * 60)
        if workflow_success:
            print("🎉 Project workflow integration tests passed!")
            return True
        else:
            print("❌ Project workflow integration tests failed!")
            return False

    except Exception as e:
        print(f"❌ Workflow integration test error: {e}")
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
    print("🚀 Starting Project Workflow Integration Tests...")

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..")
    os.chdir(project_root)

    success = run_project_workflow_tests()

    if success:
        print("\n✅ Project workflow integration tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Project workflow integration tests failed!")
        exit(1)


if __name__ == "__main__":
    main()
