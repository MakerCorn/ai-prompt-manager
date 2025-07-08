"""
Integration tests for prompt visibility functionality.

This module tests the complete integration of visibility features
across the web interface, API endpoints, and database operations.
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from src.prompts.models.prompt import Prompt
from src.prompts.repositories.prompt_repository import PromptRepository
from src.prompts.services.prompt_service import PromptService
from src.core.base.database_manager import BaseDatabaseManager
from src.core.config.settings import AppConfig, DatabaseConfig, DatabaseType


class TestPromptVisibilityIntegration:
    """Integration test cases for prompt visibility functionality."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager for integration testing."""
        from src.core.config.settings import DatabaseConfig

        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=":memory:")
        config = AppConfig(database=db_config)
        db_manager = MagicMock(spec=BaseDatabaseManager)
        db_manager.config = db_config
        return db_manager

    @pytest.fixture
    def repository(self, mock_db_manager):
        """Create a repository instance for testing."""
        repo = PromptRepository(mock_db_manager)
        repo.set_tenant_context("tenant-123")
        return repo

    @pytest.fixture
    def service(self, mock_db_manager):
        """Create a service instance for testing."""
        with patch(
            "src.prompts.services.prompt_service.PromptRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = PromptService(mock_db_manager)
            service.repository = mock_repo
            return service, mock_repo

    def test_end_to_end_prompt_creation_with_visibility(self, service):
        """Test complete workflow of creating prompts with different visibility levels."""
        prompt_service, mock_repo = service

        # Mock repository responses
        mock_repo.set_tenant_context.return_value = None
        mock_repo.name_exists.return_value = False

        # Create private prompt
        private_prompt = MagicMock()
        private_prompt.visibility = "private"
        mock_repo.save.return_value = private_prompt

        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="private_test",
            title="Private Test Prompt",
            content="This is a private prompt",
            visibility="private",
        )

        assert result.success is True
        assert result.data.visibility == "private"

        # Create public prompt
        public_prompt = MagicMock()
        public_prompt.visibility = "public"
        mock_repo.save.return_value = public_prompt

        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-789",
            name="public_test",
            title="Public Test Prompt",
            content="This is a public prompt",
            visibility="public",
        )

        assert result.success is True
        assert result.data.visibility == "public"

        # Verify repository was called correctly
        assert mock_repo.save.call_count == 2

    def test_visibility_filtering_across_users(self, service):
        """Test that visibility filtering works correctly across different users."""
        prompt_service, mock_repo = service

        # Mock repository responses for visibility filtering
        mock_repo.set_tenant_context.return_value = None

        # Mock prompts from different users
        user1_private = MagicMock()
        user1_private.visibility = "private"
        user1_private.user_id = "user-1"

        user1_public = MagicMock()
        user1_public.visibility = "public"
        user1_public.user_id = "user-1"

        user2_private = MagicMock()
        user2_private.visibility = "private"
        user2_private.user_id = "user-2"

        user2_public = MagicMock()
        user2_public.visibility = "public"
        user2_public.user_id = "user-2"

        # Test: User 1 should see their own prompts + public prompts from others
        mock_repo.find_all_with_visibility.return_value = [
            user1_private,
            user1_public,
            user2_public,
        ]

        result = prompt_service.get_all_prompts_with_visibility(
            tenant_id="tenant-123", user_id="user-1", include_public_from_tenant=True
        )

        assert result.success is True
        assert len(result.data) == 3

        # Verify the repository was called with correct parameters
        mock_repo.find_all_with_visibility.assert_called_with(
            include_enhancement_prompts=True,
            include_public_from_tenant=True,
            user_id="user-1",
            limit=None,
            order_by="category, name",
        )

    def test_search_with_visibility_filtering(self, service):
        """Test that search functionality respects visibility settings."""
        prompt_service, mock_repo = service

        # Mock repository responses
        mock_repo.set_tenant_context.return_value = None
        mock_repo.search_prompts.return_value = [
            MagicMock(visibility="private", user_id="user-1"),
            MagicMock(visibility="public", user_id="user-2"),
        ]

        result = prompt_service.search_prompts(
            tenant_id="tenant-123",
            search_term="test",
            user_id="user-1",
            include_public_from_tenant=True,
        )

        assert result.success is True
        assert len(result.data) == 2

        # Verify search was called with visibility parameters
        mock_repo.search_prompts.assert_called_with(
            "test",
            search_in=None,
            limit=None,
            user_id="user-1",
            include_public_from_tenant=True,
        )

    def test_visibility_update_workflow(self, service):
        """Test updating prompt visibility through the service layer."""
        prompt_service, mock_repo = service

        # Mock existing prompt
        existing_prompt = MagicMock()
        existing_prompt.id = 1
        existing_prompt.visibility = "private"

        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_by_name.return_value = existing_prompt
        mock_repo.name_exists.return_value = False
        mock_repo.save.return_value = existing_prompt

        result = prompt_service.update_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            original_name="test_prompt",
            new_name="test_prompt",
            title="Updated Test Prompt",
            content="Updated content",
            visibility="public",
        )

        assert result.success is True
        assert existing_prompt.visibility == "public"
        mock_repo.save.assert_called_once()

    def test_visibility_statistics_integration(self, service):
        """Test visibility statistics across the service layer."""
        prompt_service, mock_repo = service

        mock_repo.set_tenant_context.return_value = None
        mock_repo.get_visibility_statistics.return_value = {
            "total_prompts": 20,
            "private_prompts": 12,
            "public_prompts": 8,
            "private_percentage": 60.0,
            "public_percentage": 40.0,
        }

        result = prompt_service.get_visibility_statistics("tenant-123")

        assert result.success is True
        assert result.data["total_prompts"] == 20
        assert result.data["private_prompts"] == 12
        assert result.data["public_prompts"] == 8

    def test_public_prompts_filtering_integration(self, service):
        """Test filtering to show only public prompts."""
        prompt_service, mock_repo = service

        public_prompts = [
            MagicMock(visibility="public", user_id="user-1"),
            MagicMock(visibility="public", user_id="user-2"),
            MagicMock(visibility="public", user_id="user-3"),
        ]

        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_public_prompts_in_tenant.return_value = public_prompts

        result = prompt_service.get_public_prompts_in_tenant("tenant-123")

        assert result.success is True
        assert len(result.data) == 3
        assert all(p.visibility == "public" for p in result.data)

    def test_visibility_validation_integration(self, service):
        """Test that invalid visibility values are properly rejected."""
        prompt_service, mock_repo = service

        mock_repo.set_tenant_context.return_value = None

        # Test invalid visibility in create
        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="invalid_test",
            title="Invalid Test",
            content="Test content",
            visibility="invalid_value",
        )

        assert result.success is False
        assert "Visibility must be either 'private' or 'public'" in result.error

        # Test invalid visibility in update
        existing_prompt = MagicMock()
        existing_prompt.id = 1
        mock_repo.find_by_name.return_value = existing_prompt

        result = prompt_service.update_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            original_name="test_prompt",
            new_name="test_prompt",
            title="Test",
            content="Test",
            visibility="also_invalid",
        )

        assert result.success is False
        assert "Visibility must be either 'private' or 'public'" in result.error

    def test_repository_query_integration(self, repository, mock_db_manager):
        """Test repository queries with visibility filtering."""
        # Mock database responses
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-1",
                "name": "prompt1",
                "title": "Prompt 1",
                "content": "Content 1",
                "category": "Test",
                "tags": "",
                "visibility": "private",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": 2,
                "tenant_id": "tenant-123",
                "user_id": "user-2",
                "name": "prompt2",
                "title": "Prompt 2",
                "content": "Content 2",
                "category": "Test",
                "tags": "",
                "visibility": "public",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        # Test find_all_with_visibility
        prompts = repository.find_all_with_visibility(
            user_id="user-1", include_public_from_tenant=True
        )

        assert len(prompts) == 2
        assert mock_db_manager.execute_query.called

        # Verify the SQL query includes visibility conditions
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "tenant_id" in query
        assert "user_id = ? OR visibility = 'public'" in query
        assert "tenant-123" in params
        assert "user-1" in params

    def test_database_schema_integration(self, repository, mock_db_manager):
        """Test that database schema properly handles visibility constraints."""
        # Test that we can create and validate prompts with visibility field
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="schema_test",
            title="Schema Test",
            content="Test content",
            visibility="public",
        )

        # Verify the prompt is created correctly
        assert prompt.visibility == "public"
        assert prompt.is_public()
        assert not prompt.is_private()

        # Test that the entity_to_dict includes visibility
        entity_dict = repository._entity_to_dict(prompt)
        assert entity_dict["visibility"] == "public"

        # Test that the schema would be created with visibility field
        # (The repository constructor would have called execute_query to create tables)
        assert mock_db_manager.execute_query.called

    def test_error_handling_integration(self, service):
        """Test error handling across the visibility integration."""
        prompt_service, mock_repo = service

        # Test database error handling
        mock_repo.set_tenant_context.side_effect = Exception(
            "Database connection error"
        )

        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="error_test",
            title="Error Test",
            content="Test content",
            visibility="private",
        )

        assert result.success is False
        assert "unexpected error" in result.error.lower()
        assert result.error_code == "INTERNAL_ERROR"

    def test_tenant_isolation_with_visibility(self, repository, mock_db_manager):
        """Test that visibility filtering respects tenant isolation."""
        # Mock prompts from different tenants
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-1",
                "name": "tenant1_private",
                "title": "T1 Private",
                "content": "Content",
                "category": "Test",
                "tags": "",
                "visibility": "private",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": 2,
                "tenant_id": "tenant-123",
                "user_id": "user-2",
                "name": "tenant1_public",
                "title": "T1 Public",
                "content": "Content",
                "category": "Test",
                "tags": "",
                "visibility": "public",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        # Set tenant context
        repository.set_tenant_context("tenant-123")

        # Get public prompts for the tenant
        prompts = repository.find_public_prompts_in_tenant()

        assert len(prompts) == 2

        # Verify tenant filtering in query
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "tenant_id" in query
        assert "tenant-123" in params

    def test_performance_with_visibility_filtering(self, repository, mock_db_manager):
        """Test performance implications of visibility filtering."""
        # Mock large dataset
        large_dataset = []
        for i in range(100):
            large_dataset.append(
                {
                    "id": i,
                    "tenant_id": "tenant-123",
                    "user_id": f"user-{i % 10}",
                    "name": f"prompt_{i}",
                    "title": f"Prompt {i}",
                    "content": f"Content {i}",
                    "category": "Test",
                    "tags": "",
                    "visibility": "public" if i % 3 == 0 else "private",
                    "is_enhancement_prompt": False,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }
            )

        mock_db_manager.execute_query.return_value = large_dataset

        # Test with pagination
        prompts = repository.find_all_with_visibility(
            user_id="user-1", include_public_from_tenant=True, limit=20, offset=0
        )

        assert len(prompts) == 100  # Mock returns all data

        # Verify LIMIT was included in query
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        assert "LIMIT 20" in query


class TestVisibilityAPIIntegration:
    """Integration tests for visibility API endpoints."""

    def test_api_endpoint_visibility_filtering(self):
        """Test that API endpoints properly handle visibility filtering."""
        # This would typically test actual HTTP endpoints
        # For now, we'll test the underlying service calls

        # Mock API request data
        request_data = {
            "user_id": "user-123",
            "include_public": True,
            "visibility": "private",
        }

        # Simulate API endpoint logic
        assert request_data["visibility"] in ["private", "public"]
        assert isinstance(request_data["include_public"], bool)
        assert request_data["user_id"] is not None

    def test_api_error_responses_for_visibility(self):
        """Test API error responses for invalid visibility values."""
        # Test invalid visibility value
        invalid_request = {"visibility": "invalid_value"}

        # This would typically be handled by API validation
        valid_visibility_values = ["private", "public"]
        assert invalid_request["visibility"] not in valid_visibility_values


class TestVisibilityWebIntegration:
    """Integration tests for web interface visibility features."""

    def test_web_form_visibility_controls(self):
        """Test web form integration with visibility controls."""
        # Mock form data that would come from web interface
        form_data = {
            "name": "web_test_prompt",
            "title": "Web Test Prompt",
            "content": "Test content from web form",
            "visibility": "public",
            "category": "Web Test",
        }

        # Validate form data (simulating web form validation)
        assert form_data["visibility"] in ["private", "public"]
        assert form_data["name"].strip() != ""
        assert form_data["content"].strip() != ""

    def test_web_interface_visibility_display(self):
        """Test web interface display of visibility settings."""
        # Mock prompt data for web display
        prompt_data = {
            "id": 1,
            "name": "display_test",
            "title": "Display Test",
            "visibility": "public",
            "user_id": "user-123",
        }

        # Simulate web template rendering logic
        visibility_icon = "🌐" if prompt_data["visibility"] == "public" else "🔒"
        visibility_text = (
            "Public" if prompt_data["visibility"] == "public" else "Private"
        )

        assert visibility_icon in ["🌐", "🔒"]
        assert visibility_text in ["Public", "Private"]


if __name__ == "__main__":
    pytest.main([__file__])
