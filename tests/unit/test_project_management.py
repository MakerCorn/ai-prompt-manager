"""
Comprehensive unit tests for Project Management functionality
Testing project operations, ownership transfer, tags, and token cost calculations
"""

import os
import sqlite3
import tempfile
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

from prompt_data_manager import PromptDataManager


class TestProjectManagement:
    """Test suite for Project Management functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def user_id(self):
        """Generate user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def second_user_id(self):
        """Generate second user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def data_manager(self, temp_db, tenant_id, user_id):
        """Create PromptDataManager instance with SQLite"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=user_id
            )
            # Initialize database schema
            manager.init_database()
            return manager

    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for testing"""
        return {
            "name": "test-project",
            "title": "Test Project",
            "description": "A test project for unit testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": "testing,unit-test,development"
        }

    def test_create_project_success(self, data_manager, sample_project_data):
        """Test successful project creation"""
        result = data_manager.add_project(
            name=sample_project_data["name"],
            title=sample_project_data["title"],
            description=sample_project_data["description"],
            project_type=sample_project_data["project_type"],
            visibility=sample_project_data["visibility"],
            shared_with_tenant=sample_project_data["shared_with_tenant"]
        )
        
        # add_project returns a string message, not a dict
        assert "created successfully" in result.lower()
        assert sample_project_data["title"] in result

    def test_create_project_duplicate_name(self, data_manager, sample_project_data):
        """Test project creation with duplicate name fails"""
        # Create first project
        data_manager.add_project(
            name=sample_project_data["name"],
            title=sample_project_data["title"],
            description=sample_project_data["description"],
            project_type=sample_project_data["project_type"],
            visibility=sample_project_data["visibility"],
            shared_with_tenant=sample_project_data["shared_with_tenant"]
        )
        
        # Try to create second project with same name
        result = data_manager.add_project(
            name=sample_project_data["name"],
            title=sample_project_data["title"],
            description=sample_project_data["description"],
            project_type=sample_project_data["project_type"],
            visibility=sample_project_data["visibility"],
            shared_with_tenant=sample_project_data["shared_with_tenant"]
        )
        
        assert "error" in result.lower()
        assert "already exists" in result.lower()

    def test_get_project_by_id_success(self, data_manager, sample_project_data):
        """Test retrieving project by ID"""
        # Create project
        data_manager.add_project(
            name=sample_project_data["name"],
            title=sample_project_data["title"],
            description=sample_project_data["description"],
            project_type=sample_project_data["project_type"],
            visibility=sample_project_data["visibility"],
            shared_with_tenant=sample_project_data["shared_with_tenant"]
        )
        
        # Get project by listing all projects and finding ours
        projects = data_manager.get_projects()
        created_project = next((p for p in projects if p["name"] == sample_project_data["name"]), None)
        assert created_project is not None
        project_id = created_project["id"]
        
        # Retrieve project by ID
        project = data_manager.get_project_by_id(project_id)
        
        assert project is not None
        assert project["id"] == project_id
        assert project["name"] == sample_project_data["name"]
        assert project["title"] == sample_project_data["title"]

    def test_get_project_by_id_not_found(self, data_manager):
        """Test retrieving non-existent project returns None"""
        project = data_manager.get_project_by_id(999999)
        assert project is None

    def test_get_project_by_id_tenant_isolation(self, temp_db, sample_project_data):
        """Test that projects are isolated by tenant"""
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # Create project in tenant 1
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}):
            manager1 = PromptDataManager(db_path=temp_db, tenant_id=tenant1_id, user_id=user_id)
            manager1.init_database()
            manager1.add_project(
                name=sample_project_data["name"],
                title=sample_project_data["title"],
                description=sample_project_data["description"],
                project_type=sample_project_data["project_type"],
                visibility=sample_project_data["visibility"],
                shared_with_tenant=sample_project_data["shared_with_tenant"]
            )
            # Get project ID by listing projects
            projects = manager1.get_projects()
            project_id = projects[0]["id"] if projects else None
        
        # Try to access from tenant 2
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}):
            manager2 = PromptDataManager(db_path=temp_db, tenant_id=tenant2_id, user_id=user_id)
            project = manager2.get_project_by_id(project_id)
            
        assert project is None

    def test_get_projects_list(self, data_manager, sample_project_data):
        """Test retrieving projects list"""
        # Create multiple projects
        project1_data = sample_project_data.copy()
        project1_data["name"] = "project-1"
        project1_data["title"] = "Project 1"
        
        project2_data = sample_project_data.copy()
        project2_data["name"] = "project-2"
        project2_data["title"] = "Project 2"
        project2_data["project_type"] = "sequenced"
        
        data_manager.add_project(**project1_data)
        data_manager.add_project(**project2_data)
        
        # Get projects list
        projects = data_manager.get_projects()
        
        assert len(projects) == 2
        project_names = [p["name"] for p in projects]
        assert "project-1" in project_names
        assert "project-2" in project_names

    def test_update_project_success(self, data_manager, sample_project_data):
        """Test successful project update"""
        # Create project
        create_result = data_manager.add_project(**sample_project_data)
        project_id = create_result["id"]
        
        # Update project
        update_data = {
            "title": "Updated Test Project",
            "description": "Updated description",
            "tags": "updated,tags,new"
        }
        
        result = data_manager.update_project(project_id, **update_data)
        
        assert result["success"] is True
        
        # Verify update
        updated_project = data_manager.get_project_by_id(project_id)
        assert updated_project["title"] == update_data["title"]
        assert updated_project["description"] == update_data["description"]
        assert updated_project["tags"] == update_data["tags"]

    def test_update_project_not_found(self, data_manager):
        """Test updating non-existent project fails"""
        result = data_manager.update_project(999999, title="Not Found")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_delete_project_success(self, data_manager, sample_project_data):
        """Test successful project deletion"""
        # Create project
        create_result = data_manager.add_project(**sample_project_data)
        project_id = create_result["id"]
        
        # Delete project
        result = data_manager.delete_project(project_id)
        
        assert result["success"] is True
        
        # Verify deletion
        deleted_project = data_manager.get_project_by_id(project_id)
        assert deleted_project is None

    def test_delete_project_not_found(self, data_manager):
        """Test deleting non-existent project fails"""
        result = data_manager.delete_project(999999)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestProjectOwnershipTransfer:
    """Test suite for Project Ownership Transfer functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def owner_user_id(self):
        """Generate owner user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def member_user_id(self):
        """Generate member user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def data_manager(self, temp_db, tenant_id, owner_user_id):
        """Create PromptDataManager instance as owner"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=owner_user_id
            )
            manager.init_database()
            return manager

    @pytest.fixture
    def project_with_member(self, data_manager, member_user_id):
        """Create project with a member for testing"""
        # Create project
        project_data = {
            "name": "transfer-test",
            "title": "Transfer Test Project",
            "description": "Project for ownership transfer testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": "transfer,test"
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        # Add member to project
        data_manager.add_project_member(project_id, member_user_id, "member")
        
        return project_id

    def test_transfer_ownership_success(self, data_manager, project_with_member, member_user_id, owner_user_id):
        """Test successful ownership transfer"""
        project_id = project_with_member
        
        # Transfer ownership
        result = data_manager.transfer_project_ownership(project_id, member_user_id)
        
        assert result["success"] is True
        assert result["old_owner"] == owner_user_id
        assert result["new_owner"] == member_user_id
        
        # Verify ownership change
        project = data_manager.get_project_by_id(project_id)
        assert project["user_id"] == member_user_id
        
        # Verify old owner is now a member
        members = data_manager.get_project_members(project_id)
        old_owner_member = next((m for m in members if m["user_id"] == owner_user_id), None)
        assert old_owner_member is not None
        assert old_owner_member["role"] == "member"
        
        # Verify new owner is no longer in members list (they're the owner)
        new_owner_member = next((m for m in members if m["user_id"] == member_user_id), None)
        assert new_owner_member is None

    def test_transfer_ownership_to_non_member(self, data_manager, project_with_member):
        """Test transferring ownership to non-member fails"""
        project_id = project_with_member
        non_member_id = str(uuid.uuid4())
        
        result = data_manager.transfer_project_ownership(project_id, non_member_id)
        
        assert result["success"] is False
        assert "not a member" in result["error"].lower()

    def test_transfer_ownership_non_existent_project(self, data_manager, member_user_id):
        """Test transferring ownership of non-existent project fails"""
        result = data_manager.transfer_project_ownership(999999, member_user_id)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_transfer_ownership_non_owner(self, temp_db, tenant_id, project_with_member, member_user_id):
        """Test that non-owner cannot transfer ownership"""
        project_id = project_with_member
        
        # Create manager as member (not owner)
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": temp_db}):
            member_manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=member_user_id
            )
            
            # Try to transfer ownership as member
            another_user_id = str(uuid.uuid4())
            result = member_manager.transfer_project_ownership(project_id, another_user_id)
            
            assert result["success"] is False
            assert "permission" in result["error"].lower() or "owner" in result["error"].lower()


class TestProjectTags:
    """Test suite for Project Tags functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def user_id(self):
        """Generate user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture  
    def data_manager(self, temp_db, tenant_id, user_id):
        """Create PromptDataManager instance"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=user_id
            )
            manager.init_database()
            return manager

    @pytest.fixture
    def project_with_content(self, data_manager):
        """Create project with prompts and rules for aggregate tag testing"""
        # Create project
        project_data = {
            "name": "tag-test",
            "title": "Tag Test Project", 
            "description": "Project for tag testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": "project,testing,main"
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        # Create prompts with tags
        prompt1_result = data_manager.save_prompt(
            name="test-prompt-1",
            content="Test prompt content 1",
            category="Testing",
            description="Test prompt 1",
            tags="prompt,test,ai"
        )
        
        prompt2_result = data_manager.save_prompt(
            name="test-prompt-2", 
            content="Test prompt content 2",
            category="Development",
            description="Test prompt 2",
            tags="prompt,dev,automation"
        )
        
        # Create rules with tags
        rule1_result = data_manager.create_rule(
            name="test-rule-1",
            title="Test Rule 1",
            content="# Test Rule 1\nThis is a test rule",
            category="Testing",
            tags="rule,test,validation"
        )
        
        rule2_result = data_manager.create_rule(
            name="test-rule-2",
            title="Test Rule 2", 
            content="# Test Rule 2\nAnother test rule",
            category="Development",
            tags="rule,dev,standards"
        )
        
        # Add prompts and rules to project
        data_manager.add_prompt_to_project(project_id, prompt1_result["id"])
        data_manager.add_prompt_to_project(project_id, prompt2_result["id"])
        data_manager.add_rule_to_project(project_id, rule1_result["id"])
        data_manager.add_rule_to_project(project_id, rule2_result["id"])
        
        return project_id

    def test_update_project_tags_success(self, data_manager, project_with_content):
        """Test successful project tags update"""
        project_id = project_with_content
        new_tags = "updated,project,tags,new"
        
        result = data_manager.update_project_tags(project_id, new_tags)
        
        assert result["success"] is True
        
        # Verify tags updated
        project = data_manager.get_project_by_id(project_id)
        assert project["tags"] == new_tags

    def test_update_project_tags_not_found(self, data_manager):
        """Test updating tags of non-existent project fails"""
        result = data_manager.update_project_tags(999999, "new,tags")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_get_project_aggregate_tags(self, data_manager, project_with_content):
        """Test retrieving aggregate tags from project content"""
        project_id = project_with_content
        
        aggregate_tags = data_manager.get_project_aggregate_tags(project_id)
        
        # Should contain tags from both prompts and rules
        expected_tags = {"prompt", "test", "ai", "dev", "automation", "rule", "validation", "standards"}
        assert set(aggregate_tags) == expected_tags

    def test_get_project_aggregate_tags_empty_project(self, data_manager):
        """Test aggregate tags for project with no content"""
        # Create empty project
        project_data = {
            "name": "empty-project",
            "title": "Empty Project",
            "description": "Empty project for testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": ""
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        aggregate_tags = data_manager.get_project_aggregate_tags(project_id)
        
        assert aggregate_tags == []

    def test_get_project_aggregate_tags_not_found(self, data_manager):
        """Test aggregate tags for non-existent project"""
        aggregate_tags = data_manager.get_project_aggregate_tags(999999)
        
        assert aggregate_tags == []


class TestProjectTokenCost:
    """Test suite for Project Token Cost Calculation functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def user_id(self):
        """Generate user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def data_manager(self, temp_db, tenant_id, user_id):
        """Create PromptDataManager instance"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=user_id
            )
            manager.init_database()
            return manager

    @pytest.fixture
    def project_with_content(self, data_manager):
        """Create project with prompts and rules for token cost testing"""
        # Create project
        project_data = {
            "name": "token-test",
            "title": "Token Test Project",
            "description": "Project for token cost testing",
            "project_type": "general", 
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": "token,test"
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        # Create prompts with known content lengths
        prompt1_content = "A" * 100  # 100 characters ≈ 25 tokens
        prompt1_result = data_manager.save_prompt(
            name="token-prompt-1",
            content=prompt1_content,
            category="Testing",
            description="Token test prompt 1"
        )
        
        prompt2_content = "B" * 200  # 200 characters ≈ 50 tokens  
        prompt2_result = data_manager.save_prompt(
            name="token-prompt-2",
            content=prompt2_content,
            category="Testing",
            description="Token test prompt 2"
        )
        
        # Create rules with known content lengths
        rule1_content = "C" * 400  # 400 characters ≈ 100 tokens
        rule1_result = data_manager.create_rule(
            name="token-rule-1",
            title="Token Rule 1",
            content=rule1_content,
            category="Testing"
        )
        
        rule2_content = "D" * 300  # 300 characters ≈ 75 tokens
        rule2_result = data_manager.create_rule(
            name="token-rule-2", 
            title="Token Rule 2",
            content=rule2_content,
            category="Testing"
        )
        
        # Add content to project
        data_manager.add_prompt_to_project(project_id, prompt1_result["id"])
        data_manager.add_prompt_to_project(project_id, prompt2_result["id"])
        data_manager.add_rule_to_project(project_id, rule1_result["id"])
        data_manager.add_rule_to_project(project_id, rule2_result["id"])
        
        return {
            "project_id": project_id,
            "expected_prompt_tokens": 75,  # 25 + 50
            "expected_rule_tokens": 175,   # 100 + 75
            "expected_total_tokens": 250   # 75 + 175
        }

    def test_calculate_project_token_cost_success(self, data_manager, project_with_content):
        """Test successful token cost calculation"""
        project_id = project_with_content["project_id"]
        expected_prompt_tokens = project_with_content["expected_prompt_tokens"]
        expected_rule_tokens = project_with_content["expected_rule_tokens"]
        expected_total_tokens = project_with_content["expected_total_tokens"]
        
        result = data_manager.calculate_project_token_cost(project_id)
        
        assert result["success"] is True
        assert result["prompt_tokens"] == expected_prompt_tokens
        assert result["rule_tokens"] == expected_rule_tokens
        assert result["total_tokens"] == expected_total_tokens
        assert result["total_cost"] == expected_total_tokens * 0.00003  # $0.03 per 1K tokens
        assert result["cost_per_1k_tokens"] == 0.03

    def test_calculate_project_token_cost_empty_project(self, data_manager):
        """Test token cost calculation for empty project"""
        # Create empty project
        project_data = {
            "name": "empty-token-test",
            "title": "Empty Token Test Project",
            "description": "Empty project for token testing",
            "project_type": "general",
            "visibility": "private", 
            "shared_with_tenant": False,
            "tags": ""
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        result = data_manager.calculate_project_token_cost(project_id)
        
        assert result["success"] is True
        assert result["prompt_tokens"] == 0
        assert result["rule_tokens"] == 0
        assert result["total_tokens"] == 0
        assert result["total_cost"] == 0.0

    def test_calculate_project_token_cost_not_found(self, data_manager):
        """Test token cost calculation for non-existent project"""
        result = data_manager.calculate_project_token_cost(999999)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_token_estimation_accuracy(self, data_manager):
        """Test token estimation accuracy (4 chars ≈ 1 token)"""
        # Create project with precise character counts
        project_data = {
            "name": "precision-test",
            "title": "Precision Test Project",
            "description": "Testing token estimation accuracy",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": ""
        }
        create_result = data_manager.add_project(**project_data)
        project_id = create_result["id"]
        
        # Create content with exactly 400 characters (should be 100 tokens)
        content_400_chars = "X" * 400
        prompt_result = data_manager.save_prompt(
            name="precision-prompt",
            content=content_400_chars,
            category="Testing",
            description="Precision test"
        )
        data_manager.add_prompt_to_project(project_id, prompt_result["id"])
        
        result = data_manager.calculate_project_token_cost(project_id)
        
        assert result["success"] is True
        assert result["prompt_tokens"] == 100  # 400 chars / 4 = 100 tokens
        assert result["total_tokens"] == 100


class TestProjectMembers:
    """Test suite for Project Members functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    @pytest.fixture
    def tenant_id(self):
        """Generate tenant ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def owner_user_id(self):
        """Generate owner user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def member_user_id(self):
        """Generate member user ID for testing"""
        return str(uuid.uuid4())

    @pytest.fixture
    def data_manager(self, temp_db, tenant_id, owner_user_id):
        """Create PromptDataManager instance as owner"""
        with patch.dict(
            os.environ,
            {"DB_TYPE": "sqlite", "DB_PATH": temp_db},
            clear=True,
        ):
            manager = PromptDataManager(
                db_path=temp_db, tenant_id=tenant_id, user_id=owner_user_id
            )
            manager.init_database()
            return manager

    @pytest.fixture
    def test_project(self, data_manager):
        """Create test project"""
        project_data = {
            "name": "member-test",
            "title": "Member Test Project",
            "description": "Project for member testing",
            "project_type": "general",
            "visibility": "private",
            "shared_with_tenant": False,
            "tags": "member,test"
        }
        create_result = data_manager.add_project(**project_data)
        return create_result["id"]

    def test_add_project_member_success(self, data_manager, test_project, member_user_id):
        """Test successfully adding project member"""
        result = data_manager.add_project_member(test_project, member_user_id, "member")
        
        assert result["success"] is True
        
        # Verify member added
        members = data_manager.get_project_members(test_project)
        member_user_ids = [m["user_id"] for m in members]
        assert member_user_id in member_user_ids

    def test_add_project_member_duplicate(self, data_manager, test_project, member_user_id):
        """Test adding duplicate member fails gracefully"""
        # Add member first time
        data_manager.add_project_member(test_project, member_user_id, "member")
        
        # Try to add same member again
        result = data_manager.add_project_member(test_project, member_user_id, "viewer")
        
        # Should update role, not fail
        assert result["success"] is True
        
        # Verify role updated
        members = data_manager.get_project_members(test_project)
        member = next((m for m in members if m["user_id"] == member_user_id), None)
        assert member is not None
        assert member["role"] == "viewer"

    def test_remove_project_member_success(self, data_manager, test_project, member_user_id):
        """Test successfully removing project member"""
        # Add member first
        data_manager.add_project_member(test_project, member_user_id, "member")
        
        # Remove member
        result = data_manager.remove_project_member(test_project, member_user_id)
        
        assert result["success"] is True
        
        # Verify member removed
        members = data_manager.get_project_members(test_project)
        member_user_ids = [m["user_id"] for m in members]
        assert member_user_id not in member_user_ids

    def test_remove_project_member_not_found(self, data_manager, test_project):
        """Test removing non-existent member fails"""
        non_member_id = str(uuid.uuid4())
        
        result = data_manager.remove_project_member(test_project, non_member_id)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_get_project_members_empty(self, data_manager, test_project):
        """Test getting members of project with no members"""
        members = data_manager.get_project_members(test_project)
        
        # Should be empty (owner is not in members list)
        assert len(members) == 0

    def test_get_project_members_with_members(self, data_manager, test_project, member_user_id):
        """Test getting members of project with members"""
        # Add member
        data_manager.add_project_member(test_project, member_user_id, "member")
        
        members = data_manager.get_project_members(test_project)
        
        assert len(members) == 1
        assert members[0]["user_id"] == member_user_id
        assert members[0]["role"] == "member"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])