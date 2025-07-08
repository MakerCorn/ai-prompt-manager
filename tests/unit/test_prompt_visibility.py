"""
Unit tests for prompt visibility functionality.

This module tests the visibility features including model validation,
repository filtering, service logic, and API endpoints.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.core.base.database_manager import BaseDatabaseManager
from src.core.config.settings import AppConfig, DatabaseType
from src.prompts.models.prompt import Prompt
from src.prompts.repositories.prompt_repository import PromptRepository
from src.prompts.services.prompt_service import PromptService


class TestPromptVisibilityModel:
    """Test cases for Prompt model visibility functionality."""

    def test_prompt_default_visibility(self):
        """Test that prompts default to private visibility."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        assert prompt.visibility == "private"
        assert prompt.is_private() is True
        assert prompt.is_public() is False

    def test_prompt_explicit_private_visibility(self):
        """Test creating prompt with explicit private visibility."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="private",
        )

        assert prompt.visibility == "private"
        assert prompt.is_private() is True
        assert prompt.is_public() is False

    def test_prompt_public_visibility(self):
        """Test creating prompt with public visibility."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="public",
        )

        assert prompt.visibility == "public"
        assert prompt.is_public() is True
        assert prompt.is_private() is False

    def test_prompt_invalid_visibility_validation(self):
        """Test that invalid visibility values are rejected."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="test_prompt",
                title="Test Prompt",
                content="Test content",
                visibility="invalid",
            )

        assert "Visibility must be either 'private' or 'public'" in str(exc_info.value)

    def test_set_visibility_method(self):
        """Test set_visibility method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="private",
        )

        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        prompt.set_visibility("public")

        assert prompt.visibility == "public"
        assert prompt.is_public() is True
        assert prompt.updated_at > original_updated_at

    def test_set_visibility_invalid_value(self):
        """Test set_visibility method with invalid value."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        with pytest.raises(ValueError) as exc_info:
            prompt.set_visibility("invalid")

        assert "Visibility must be either 'private' or 'public'" in str(exc_info.value)

    def test_visibility_in_to_dict(self):
        """Test that visibility is included in to_dict output."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="public",
        )

        prompt_dict = prompt.to_dict()
        assert prompt_dict["visibility"] == "public"

    def test_visibility_in_from_dict(self):
        """Test that visibility is handled in from_dict creation."""
        prompt_data = {
            "tenant_id": "tenant-123",
            "user_id": "user-456",
            "name": "test_prompt",
            "title": "Test Prompt",
            "content": "Test content",
            "visibility": "public",
        }

        prompt = Prompt.from_dict(prompt_data)
        assert prompt.visibility == "public"

    def test_visibility_in_from_dict_default(self):
        """Test that visibility defaults to private in from_dict when not specified."""
        prompt_data = {
            "tenant_id": "tenant-123",
            "user_id": "user-456",
            "name": "test_prompt",
            "title": "Test Prompt",
            "content": "Test content",
        }

        prompt = Prompt.from_dict(prompt_data)
        assert prompt.visibility == "private"

    def test_visibility_in_legacy_dict(self):
        """Test visibility handling in legacy dictionary methods."""
        # Test from_legacy_dict
        legacy_data = {
            "name": "legacy_prompt",
            "content": "Legacy content",
            "visibility": "public",
        }

        prompt = Prompt.from_legacy_dict(legacy_data, "tenant-123", "user-456")
        assert prompt.visibility == "public"

        # Test to_legacy_dict
        legacy_dict = prompt.to_legacy_dict()
        assert legacy_dict["visibility"] == "public"

    def test_visibility_in_clone(self):
        """Test that visibility is preserved when cloning."""
        original = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="original_prompt",
            title="Original Prompt",
            content="Original content",
            visibility="public",
        )

        cloned = original.clone(new_name="cloned_prompt")
        assert cloned.visibility == "public"


class TestPromptVisibilityRepository:
    """Test cases for PromptRepository visibility functionality."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager."""
        from src.core.config.settings import DatabaseConfig

        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=":memory:")
        AppConfig(database=db_config)
        db_manager = MagicMock(spec=BaseDatabaseManager)
        db_manager.config = db_config
        return db_manager

    @pytest.fixture
    def repository(self, mock_db_manager):
        """Create a repository instance with mocked database."""
        repo = PromptRepository(mock_db_manager)
        repo.set_tenant_context("tenant-123")
        return repo

    def test_find_all_with_visibility_user_and_public(
        self, repository, mock_db_manager
    ):
        """Test finding prompts with user's own prompts and public prompts."""
        # Mock database query response
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-456",
                "name": "private_prompt",
                "title": "Private",
                "content": "Private content",
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
                "user_id": "user-789",
                "name": "public_prompt",
                "title": "Public",
                "content": "Public content",
                "category": "Test",
                "tags": "",
                "visibility": "public",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        prompts = repository.find_all_with_visibility(
            user_id="user-456", include_public_from_tenant=True
        )

        assert len(prompts) == 2
        # Check that the method was called (table creation calls + our query)
        assert mock_db_manager.execute_query.call_count >= 1

        # Verify the query includes visibility conditions
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "tenant_id" in query
        assert (
            "user_id = ? OR visibility = 'public'" in query
            or "user_id = %s OR visibility = 'public'" in query
        )
        assert "tenant-123" in params
        assert "user-456" in params

    def test_find_all_with_visibility_user_only(self, repository, mock_db_manager):
        """Test finding only user's own prompts."""
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-456",
                "name": "user_prompt",
                "title": "User Prompt",
                "content": "User content",
                "category": "Test",
                "tags": "",
                "visibility": "private",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        prompts = repository.find_all_with_visibility(
            user_id="user-456", include_public_from_tenant=False
        )

        assert len(prompts) == 1

        # Verify the query includes only user filtering
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "user_id = ?" in query
        assert "OR visibility" not in query
        assert "user-456" in params

    def test_find_public_prompts_in_tenant(self, repository, mock_db_manager):
        """Test finding only public prompts in tenant."""
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-789",
                "name": "public_prompt",
                "title": "Public",
                "content": "Public content",
                "category": "Test",
                "tags": "",
                "visibility": "public",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        prompts = repository.find_public_prompts_in_tenant()

        assert len(prompts) == 1
        assert prompts[0].visibility == "public"

    def test_find_by_visibility_private(self, repository, mock_db_manager):
        """Test finding prompts by private visibility."""
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-456",
                "name": "private_prompt",
                "title": "Private",
                "content": "Private content",
                "category": "Test",
                "tags": "",
                "visibility": "private",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        prompts = repository.find_by_visibility("private", user_id="user-456")

        assert len(prompts) == 1
        assert prompts[0].visibility == "private"

    def test_find_by_visibility_public(self, repository, mock_db_manager):
        """Test finding prompts by public visibility."""
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-789",
                "name": "public_prompt",
                "title": "Public",
                "content": "Public content",
                "category": "Test",
                "tags": "",
                "visibility": "public",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        prompts = repository.find_by_visibility("public")

        assert len(prompts) == 1
        assert prompts[0].visibility == "public"

    def test_get_visibility_statistics(self, repository, mock_db_manager):
        """Test getting visibility statistics."""
        # Reset the mock to clear table creation calls
        mock_db_manager.execute_query.reset_mock()

        # Mock three separate queries for total, private, and public counts
        mock_db_manager.execute_query.side_effect = [
            {"count": 10},  # Total count
            {"count": 7},  # Private count
            {"count": 3},  # Public count
        ]

        stats = repository.get_visibility_statistics()

        assert stats["total_prompts"] == 10
        assert stats["private_prompts"] == 7
        assert stats["public_prompts"] == 3
        assert stats["private_percentage"] == 70.0
        assert stats["public_percentage"] == 30.0

        # Verify three separate queries were made
        assert mock_db_manager.execute_query.call_count == 3

    def test_search_prompts_with_visibility(self, repository, mock_db_manager):
        """Test searching prompts with visibility filtering."""
        mock_db_manager.execute_query.return_value = [
            {
                "id": 1,
                "tenant_id": "tenant-123",
                "user_id": "user-456",
                "name": "test_prompt",
                "title": "Test",
                "content": "Test content",
                "category": "Test",
                "tags": "",
                "visibility": "private",
                "is_enhancement_prompt": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        prompts = repository.search_prompts(
            "test", user_id="user-456", include_public_from_tenant=True
        )

        assert len(prompts) == 1

        # Verify the query includes visibility conditions
        call_args = mock_db_manager.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "tenant_id" in query
        assert (
            "user_id = ? OR visibility = 'public'" in query
            or "user_id = %s OR visibility = 'public'" in query
        )
        assert any("test" in str(param).lower() for param in params)


class TestPromptVisibilityService:
    """Test cases for PromptService visibility functionality."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager."""
        from src.core.config.settings import DatabaseConfig

        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=":memory:")
        AppConfig(database=db_config)
        db_manager = MagicMock(spec=BaseDatabaseManager)
        db_manager.config = db_config
        return db_manager

    @pytest.fixture
    def service(self, mock_db_manager):
        """Create a service instance with mocked database."""
        with patch(
            "src.prompts.services.prompt_service.PromptRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = PromptService(mock_db_manager)
            service.repository = mock_repo
            return service, mock_repo

    def test_create_prompt_with_visibility(self, service):
        """Test creating a prompt with visibility."""
        prompt_service, mock_repo = service

        # Mock repository methods
        mock_repo.set_tenant_context.return_value = None
        mock_repo.name_exists.return_value = False

        mock_prompt = MagicMock()
        mock_repo.save.return_value = mock_prompt

        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="public",
        )

        assert result.success is True
        assert result.data == mock_prompt
        mock_repo.save.assert_called_once()

    def test_create_prompt_invalid_visibility(self, service):
        """Test creating a prompt with invalid visibility."""
        prompt_service, mock_repo = service

        mock_repo.set_tenant_context.return_value = None

        result = prompt_service.create_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            visibility="invalid",
        )

        assert result.success is False
        assert "Visibility must be either 'private' or 'public'" in result.error

    def test_update_prompt_with_visibility(self, service):
        """Test updating a prompt with visibility."""
        prompt_service, mock_repo = service

        # Mock existing prompt
        existing_prompt = MagicMock()
        existing_prompt.id = 1
        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_by_name.return_value = existing_prompt
        mock_repo.name_exists.return_value = False
        mock_repo.save.return_value = existing_prompt

        result = prompt_service.update_prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            original_name="old_name",
            new_name="new_name",
            title="Updated Title",
            content="Updated content",
            visibility="public",
        )

        assert result.success is True
        assert existing_prompt.visibility == "public"
        mock_repo.save.assert_called_once()

    def test_get_all_prompts_with_visibility(self, service):
        """Test getting all prompts with visibility filtering."""
        prompt_service, mock_repo = service

        mock_prompts = [MagicMock(), MagicMock()]
        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_all_with_visibility.return_value = mock_prompts

        result = prompt_service.get_all_prompts_with_visibility(
            tenant_id="tenant-123", user_id="user-456", include_public_from_tenant=True
        )

        assert result.success is True
        assert result.data == mock_prompts
        mock_repo.find_all_with_visibility.assert_called_once_with(
            include_enhancement_prompts=True,
            include_public_from_tenant=True,
            user_id="user-456",
            limit=None,
            order_by="category, name",
        )

    def test_get_public_prompts_in_tenant(self, service):
        """Test getting public prompts in tenant."""
        prompt_service, mock_repo = service

        mock_prompts = [MagicMock()]
        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_public_prompts_in_tenant.return_value = mock_prompts

        result = prompt_service.get_public_prompts_in_tenant(tenant_id="tenant-123")

        assert result.success is True
        assert result.data == mock_prompts

    def test_get_prompts_by_visibility(self, service):
        """Test getting prompts by visibility."""
        prompt_service, mock_repo = service

        mock_prompts = [MagicMock()]
        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_by_visibility.return_value = mock_prompts

        result = prompt_service.get_prompts_by_visibility(
            tenant_id="tenant-123", visibility="public", user_id="user-456"
        )

        assert result.success is True
        assert result.data == mock_prompts
        mock_repo.find_by_visibility.assert_called_once_with(
            visibility="public", user_id="user-456", limit=None
        )

    def test_get_prompts_by_visibility_invalid(self, service):
        """Test getting prompts by invalid visibility."""
        prompt_service, mock_repo = service

        mock_repo.set_tenant_context.return_value = None

        result = prompt_service.get_prompts_by_visibility(
            tenant_id="tenant-123", visibility="invalid"
        )

        assert result.success is False
        assert "Visibility must be either 'private' or 'public'" in result.error

    def test_get_visibility_statistics(self, service):
        """Test getting visibility statistics."""
        prompt_service, mock_repo = service

        mock_stats = {
            "total_prompts": 10,
            "private_prompts": 7,
            "public_prompts": 3,
        }
        mock_repo.set_tenant_context.return_value = None
        mock_repo.get_visibility_statistics.return_value = mock_stats

        result = prompt_service.get_visibility_statistics("tenant-123")

        assert result.success is True
        assert result.data == mock_stats

    def test_search_prompts_with_visibility(self, service):
        """Test searching prompts with visibility filtering."""
        prompt_service, mock_repo = service

        mock_prompts = [MagicMock()]
        mock_repo.set_tenant_context.return_value = None
        mock_repo.search_prompts.return_value = mock_prompts

        result = prompt_service.search_prompts(
            tenant_id="tenant-123",
            search_term="test",
            user_id="user-456",
            include_public_from_tenant=True,
        )

        assert result.success is True
        assert result.data == mock_prompts
        mock_repo.search_prompts.assert_called_once_with(
            "test",
            search_in=None,
            limit=None,
            user_id="user-456",
            include_public_from_tenant=True,
        )

    def test_search_prompts_empty_term_uses_visibility_filtering(self, service):
        """Test that empty search term uses visibility-aware get_all method."""
        prompt_service, mock_repo = service

        mock_prompts = [MagicMock()]
        mock_repo.set_tenant_context.return_value = None
        mock_repo.find_all_with_visibility.return_value = mock_prompts

        result = prompt_service.search_prompts(
            tenant_id="tenant-123",
            search_term="",
            user_id="user-456",
            include_public_from_tenant=True,
        )

        assert result.success is True
        assert result.data == mock_prompts

        # Should call get_all_prompts_with_visibility, not search_prompts
        mock_repo.find_all_with_visibility.assert_called_once()
        mock_repo.search_prompts.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
