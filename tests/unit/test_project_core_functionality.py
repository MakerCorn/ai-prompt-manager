"""
Core unit tests for Project Management functionality
Testing the most important project operations that were recently implemented
"""

import os
import sqlite3
import tempfile
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

from prompt_data_manager import PromptDataManager


class TestProjectCoreFunctionality:
    """Test suite for core Project Management functionality"""

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
        """Create PromptDataManager instance with SQLite"""
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
    def sample_project(self, data_manager):
        """Create a sample project for testing"""
        result = data_manager.add_project(
            name="test-project",
            title="Test Project",
            description="A test project for unit testing",
            project_type="general",
            visibility="private",
            shared_with_tenant=False
        )
        assert "created successfully" in result.lower()
        
        # Get the created project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "test-project"), None)
        assert project is not None
        return project

    def test_add_project_success(self, data_manager):
        """Test successful project creation"""
        result = data_manager.add_project(
            name="new-project",
            title="New Project",
            description="A new test project",
            project_type="sequenced",
            visibility="public",
            shared_with_tenant=True
        )
        
        assert "created successfully" in result.lower()
        assert "New Project" in result

    def test_add_project_duplicate_name_fails(self, data_manager):
        """Test that duplicate project names fail"""
        # Create first project
        data_manager.add_project(
            name="duplicate-test",
            title="First Project",
            description="First project"
        )
        
        # Try to create second project with same name
        result = data_manager.add_project(
            name="duplicate-test",
            title="Second Project",
            description="Second project"
        )
        
        assert "error" in result.lower()
        assert "already exists" in result.lower()

    def test_get_project_by_id_success(self, data_manager, sample_project):
        """Test retrieving project by ID"""
        project_id = sample_project["id"]
        
        retrieved_project = data_manager.get_project_by_id(project_id)
        
        assert retrieved_project is not None
        assert retrieved_project["id"] == project_id
        assert retrieved_project["name"] == "test-project"
        assert retrieved_project["title"] == "Test Project"

    def test_get_project_by_id_not_found(self, data_manager):
        """Test retrieving non-existent project"""
        project = data_manager.get_project_by_id(999999)
        assert project is None

    def test_get_projects_list(self, data_manager):
        """Test getting all projects"""
        # Create multiple projects
        data_manager.add_project(name="proj1", title="Project 1")
        data_manager.add_project(name="proj2", title="Project 2")
        
        projects = data_manager.get_projects()
        
        assert len(projects) >= 2
        project_names = [p["name"] for p in projects]
        assert "proj1" in project_names
        assert "proj2" in project_names

    def test_delete_project_success(self, data_manager, sample_project):
        """Test successful project deletion"""
        project_id = sample_project["id"]
        
        result = data_manager.delete_project(project_id)
        
        # delete_project returns a string message
        assert "deleted" in result.lower() or "success" in result.lower()
        
        # Verify project is actually deleted
        deleted_project = data_manager.get_project_by_id(project_id)
        assert deleted_project is None

    def test_delete_project_not_found(self, data_manager):
        """Test deleting non-existent project"""
        result = data_manager.delete_project(999999)
        
        assert "error" in result.lower() or "not found" in result.lower()


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
        data_manager.add_project(
            name="transfer-test",
            title="Transfer Test Project",
            description="Project for ownership transfer testing"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "transfer-test"), None)
        project_id = project["id"]
        
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

    def test_transfer_ownership_to_non_member_fails(self, data_manager, project_with_member):
        """Test transferring ownership to non-member fails"""
        project_id = project_with_member
        non_member_id = str(uuid.uuid4())
        
        result = data_manager.transfer_project_ownership(project_id, non_member_id)
        
        assert result["success"] is False
        assert "must be a member" in result["error"].lower()

    def test_transfer_ownership_non_existent_project_fails(self, data_manager, member_user_id):
        """Test transferring ownership of non-existent project fails"""
        result = data_manager.transfer_project_ownership(999999, member_user_id)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


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
        data_manager.add_project(
            name="tag-test",
            title="Tag Test Project", 
            description="Project for tag testing"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "tag-test"), None)
        project_id = project["id"]
        
        # Create prompts with tags
        data_manager.add_prompt(
            name="test-prompt-1",
            title="Test Prompt 1",
            content="Test prompt content 1",
            category="Testing",
            tags="prompt,test,ai"
        )
        
        data_manager.add_prompt(
            name="test-prompt-2", 
            title="Test Prompt 2",
            content="Test prompt content 2",
            category="Development",
            tags="prompt,dev,automation"
        )
        
        # Create rules with tags
        data_manager.add_rule(
            name="test-rule-1",
            title="Test Rule 1",
            content="# Test Rule 1\nThis is a test rule",
            category="Testing",
            tags="rule,test,validation"
        )
        
        data_manager.add_rule(
            name="test-rule-2",
            title="Test Rule 2", 
            content="# Test Rule 2\nAnother test rule",
            category="Development",
            tags="rule,dev,standards"
        )
        
        # Get created items by name and add to project
        prompt1 = data_manager.get_prompt_by_name("test-prompt-1")
        prompt2 = data_manager.get_prompt_by_name("test-prompt-2")
        rule1 = data_manager.get_rule_by_name("test-rule-1") 
        rule2 = data_manager.get_rule_by_name("test-rule-2")
        
        # Add prompts and rules to project
        if prompt1:
            data_manager.add_prompt_to_project(project_id, prompt1["id"])
        if prompt2:
            data_manager.add_prompt_to_project(project_id, prompt2["id"])
        if rule1:
            data_manager.add_rule_to_project(project_id, rule1["id"])
        if rule2:
            data_manager.add_rule_to_project(project_id, rule2["id"])
        
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
        assert ("not found" in result["error"].lower() or "permission denied" in result["error"].lower())

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
        data_manager.add_project(
            name="empty-project",
            title="Empty Project",
            description="Empty project for testing"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "empty-project"), None)
        project_id = project["id"]
        
        aggregate_tags = data_manager.get_project_aggregate_tags(project_id)
        
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
        data_manager.add_project(
            name="token-test",
            title="Token Test Project",
            description="Project for token cost testing"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "token-test"), None)
        project_id = project["id"]
        
        # Create prompts with known content lengths
        prompt1_content = "A" * 100  # 100 characters ≈ 25 tokens
        data_manager.add_prompt(
            name="token-prompt-1",
            title="Token Prompt 1",
            content=prompt1_content,
            category="Testing",
            tags=""
        )
        
        prompt2_content = "B" * 200  # 200 characters ≈ 50 tokens  
        data_manager.add_prompt(
            name="token-prompt-2",
            title="Token Prompt 2",
            content=prompt2_content,
            category="Testing",
            tags=""
        )
        
        # Create rules with known content lengths
        rule1_content = "C" * 400  # 400 characters ≈ 100 tokens
        data_manager.add_rule(
            name="token-rule-1",
            title="Token Rule 1",
            content=rule1_content,
            category="Testing"
        )
        
        rule2_content = "D" * 300  # 300 characters ≈ 75 tokens
        data_manager.add_rule(
            name="token-rule-2", 
            title="Token Rule 2",
            content=rule2_content,
            category="Testing"
        )
        
        # Get created items and add to project
        prompt1 = data_manager.get_prompt_by_name("token-prompt-1")
        prompt2 = data_manager.get_prompt_by_name("token-prompt-2")
        rule1 = data_manager.get_rule_by_name("token-rule-1")
        rule2 = data_manager.get_rule_by_name("token-rule-2")
        
        # Add content to project
        if prompt1:
            data_manager.add_prompt_to_project(project_id, prompt1["id"])
        if prompt2:
            data_manager.add_prompt_to_project(project_id, prompt2["id"])
        if rule1:
            data_manager.add_rule_to_project(project_id, rule1["id"])
        if rule2:
            data_manager.add_rule_to_project(project_id, rule2["id"])
        
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
        # Use approximate comparison for floating point
        assert abs(result["total_cost"] - (expected_total_tokens * 0.00003)) < 0.000001
        assert result["cost_per_1k_tokens"] == 0.03

    def test_calculate_project_token_cost_empty_project(self, data_manager):
        """Test token cost calculation for empty project"""
        # Create empty project
        data_manager.add_project(
            name="empty-token-test",
            title="Empty Token Test Project",
            description="Empty project for token testing"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "empty-token-test"), None)
        project_id = project["id"]
        
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
        assert ("not found" in result["error"].lower() or "permission denied" in result["error"].lower())

    def test_token_estimation_accuracy(self, data_manager):
        """Test token estimation accuracy (4 chars ≈ 1 token)"""
        # Create project with precise character counts
        data_manager.add_project(
            name="precision-test",
            title="Precision Test Project",
            description="Testing token estimation accuracy"
        )
        
        # Get project
        projects = data_manager.get_projects()
        project = next((p for p in projects if p["name"] == "precision-test"), None)
        project_id = project["id"]
        
        # Create content with exactly 400 characters (should be 100 tokens)
        content_400_chars = "X" * 400
        data_manager.add_prompt(
            name="precision-prompt",
            title="Precision Prompt",
            content=content_400_chars,
            category="Testing",
            tags=""
        )
        
        # Get the created prompt and add to project
        precision_prompt = data_manager.get_prompt_by_name("precision-prompt")
        if precision_prompt:
            data_manager.add_prompt_to_project(project_id, precision_prompt["id"])
        
        result = data_manager.calculate_project_token_cost(project_id)
        
        assert result["success"] is True
        assert result["prompt_tokens"] == 100  # 400 chars / 4 = 100 tokens
        assert result["total_tokens"] == 100


class TestProjectSearch:
    """Test suite for enhanced project search functionality"""

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

    def test_search_projects_by_term(self, data_manager):
        """Test searching projects by search term"""
        # Create test projects
        result1 = data_manager.add_project(
            name="search-test-1", 
            title="Search Test Project", 
            description="A project for search testing"
        )
        result2 = data_manager.add_project(
            name="other-project", 
            title="Other Project", 
            description="A different project"
        )
        
        assert "successfully" in result1
        assert "successfully" in result2
        
        # Test search by term
        search_results = data_manager.search_projects(search_term="search")
        assert len(search_results) == 1
        assert search_results[0]["name"] == "search-test-1"
        
        # Test search by title
        title_results = data_manager.search_projects(search_term="Other")
        assert len(title_results) == 1
        assert title_results[0]["name"] == "other-project"

    def test_search_projects_by_type(self, data_manager):
        """Test searching projects by project type"""
        # Create projects with different types
        data_manager.add_project(
            name="general-proj", 
            title="General Project", 
            project_type="general"
        )
        data_manager.add_project(
            name="sequenced-proj", 
            title="Sequenced Project", 
            project_type="sequenced"
        )
        
        # Test filter by type
        general_results = data_manager.search_projects(project_type="general")
        sequenced_results = data_manager.search_projects(project_type="sequenced")
        
        assert len(general_results) >= 1
        assert len(sequenced_results) >= 1
        assert all(p["project_type"] == "general" for p in general_results)
        assert all(p["project_type"] == "sequenced" for p in sequenced_results)

    def test_search_projects_by_tags(self, data_manager):
        """Test searching projects by tags"""
        # Create project and add tags
        result = data_manager.add_project(
            name="tagged-proj", 
            title="Tagged Project"
        )
        assert "successfully" in result
        
        # Get project ID and add tags
        projects = data_manager.get_projects()
        project_id = next(p["id"] for p in projects if p["name"] == "tagged-proj")
        data_manager.update_project_tags(project_id, "test,development,python")
        
        # Test search by tags
        tag_results = data_manager.search_projects(tags="development")
        assert len(tag_results) >= 1
        assert any("development" in p["tags"] for p in tag_results)

    def test_search_projects_with_pagination(self, data_manager):
        """Test search with pagination"""
        # Create multiple projects
        for i in range(5):
            data_manager.add_project(
                name=f"paginated-proj-{i}", 
                title=f"Paginated Project {i}"
            )
        
        # Test pagination
        page1_results = data_manager.search_projects(search_term="paginated", limit=3, offset=0)
        page2_results = data_manager.search_projects(search_term="paginated", limit=3, offset=3)
        
        assert len(page1_results) <= 3
        assert len(page2_results) <= 3
        
        # Ensure no overlap
        page1_ids = {p["id"] for p in page1_results}
        page2_ids = {p["id"] for p in page2_results}
        assert len(page1_ids.intersection(page2_ids)) == 0

    def test_search_projects_combined_filters(self, data_manager):
        """Test search with multiple combined filters"""
        # Create project with specific characteristics
        result = data_manager.add_project(
            name="multi-filter-test", 
            title="Multi Filter Test", 
            description="Testing multiple filters",
            project_type="developer"
        )
        assert "successfully" in result
        
        # Get project and add tags
        projects = data_manager.get_projects()
        project_id = next(p["id"] for p in projects if p["name"] == "multi-filter-test")
        data_manager.update_project_tags(project_id, "multi,filter,test")
        
        # Test combined search
        combined_results = data_manager.search_projects(
            search_term="multi",
            project_type="developer",
            tags="filter"
        )
        
        assert len(combined_results) >= 1
        found_project = next(p for p in combined_results if p["name"] == "multi-filter-test")
        assert found_project["project_type"] == "developer"
        assert "filter" in found_project["tags"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])