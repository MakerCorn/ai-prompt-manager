"""
Unit tests for the Prompt model.

This module tests the Prompt entity model including validation,
business logic, metadata operations, and serialization.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from src.prompts.models.prompt import Prompt


class TestPromptModel:
    """Test cases for the Prompt model."""

    def test_prompt_creation_with_required_fields(self):
        """Test creating a prompt with only required fields."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="This is a test prompt",
        )

        assert prompt.tenant_id == "tenant-123"
        assert prompt.user_id == "user-456"
        assert prompt.name == "test_prompt"
        assert prompt.title == "Test Prompt"
        assert prompt.content == "This is a test prompt"
        assert prompt.category == "Uncategorized"
        assert prompt.tags == ""
        assert prompt.is_enhancement_prompt is False
        assert prompt.id is None
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)
        assert prompt.metadata == {}

    def test_prompt_creation_with_all_fields(self):
        """Test creating a prompt with all fields."""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        metadata = {"version": 1, "source": "test"}

        prompt = Prompt(
            id=123,
            tenant_id="tenant-123",
            user_id="user-456",
            name="full_prompt",
            title="Full Test Prompt",
            content="Complete test prompt content",
            category="Testing",
            tags="test,automation,unit",
            is_enhancement_prompt=True,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )

        assert prompt.id == 123
        assert prompt.category == "Testing"
        assert prompt.tags == "test,automation,unit"
        assert prompt.is_enhancement_prompt is True
        assert prompt.created_at == created_at
        assert prompt.updated_at == updated_at
        assert prompt.metadata == metadata

    def test_prompt_post_init_sets_timestamps(self):
        """Test that __post_init__ sets default timestamps."""
        with patch("src.prompts.models.prompt.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now

            prompt = Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="test_prompt",
                title="Test Prompt",
                content="Test content",
            )

            assert prompt.created_at == mock_now
            assert prompt.updated_at == mock_now

    def test_prompt_validation_empty_name(self):
        """Test prompt validation fails with empty name."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="",
                title="Test Prompt",
                content="Test content",
            )

        assert "Prompt name cannot be empty" in str(exc_info.value)

    def test_prompt_validation_whitespace_name(self):
        """Test prompt validation fails with whitespace-only name."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="   ",
                title="Test Prompt",
                content="Test content",
            )

        assert "Prompt name cannot be empty" in str(exc_info.value)

    def test_prompt_validation_empty_title(self):
        """Test prompt validation fails with empty title."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="test_prompt",
                title="",
                content="Test content",
            )

        assert "Prompt title cannot be empty" in str(exc_info.value)

    def test_prompt_validation_empty_content(self):
        """Test prompt validation fails with empty content."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="test_prompt",
                title="Test Prompt",
                content="",
            )

        assert "Prompt content cannot be empty" in str(exc_info.value)

    def test_prompt_validation_empty_tenant_id(self):
        """Test prompt validation fails with empty tenant_id."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="",
                user_id="user-456",
                name="test_prompt",
                title="Test Prompt",
                content="Test content",
            )

        assert "Tenant ID is required" in str(exc_info.value)

    def test_prompt_validation_empty_user_id(self):
        """Test prompt validation fails with empty user_id."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="",
                name="test_prompt",
                title="Test Prompt",
                content="Test content",
            )

        assert "User ID is required" in str(exc_info.value)

    def test_prompt_validation_invalid_name_format(self):
        """Test prompt validation fails with invalid name format."""
        with pytest.raises(ValueError) as exc_info:
            Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name="test@prompt#invalid",
                title="Test Prompt",
                content="Test content",
            )

        assert (
            "can only contain letters, numbers, spaces, hyphens, and underscores"
            in str(exc_info.value)
        )

    def test_prompt_validation_valid_name_formats(self):
        """Test prompt validation passes with valid name formats."""
        valid_names = [
            "test_prompt",
            "test-prompt",
            "test prompt",
            "TestPrompt123",
            "test_prompt_123",
            "test-prompt-456",
        ]

        for name in valid_names:
            # Should not raise exception
            prompt = Prompt(
                tenant_id="tenant-123",
                user_id="user-456",
                name=name,
                title="Test Prompt",
                content="Test content",
            )
            assert prompt.name == name

    def test_tag_list_property_getter(self):
        """Test tag_list property getter."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="tag1, tag2,  tag3  ,tag4",
        )

        tag_list = prompt.tag_list
        assert tag_list == ["tag1", "tag2", "tag3", "tag4"]

    def test_tag_list_property_empty_tags(self):
        """Test tag_list property with empty tags."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="",
        )

        assert prompt.tag_list == []

    def test_tag_list_property_setter(self):
        """Test tag_list property setter."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        prompt.tag_list = ["new_tag1", "new_tag2", "new_tag3"]

        assert prompt.tags == "new_tag1, new_tag2, new_tag3"
        assert prompt.updated_at is not None and original_updated_at is not None
        assert prompt.updated_at > original_updated_at

    def test_tag_list_property_setter_empty_list(self):
        """Test tag_list property setter with empty list."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="existing,tags",
        )

        prompt.tag_list = []

        assert prompt.tags == ""

    def test_content_length_property(self):
        """Test content_length property."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="This is a test prompt with some content",
        )

        assert prompt.content_length == len("This is a test prompt with some content")

    def test_content_length_property_empty_content(self):
        """Test content_length property with empty content after creation."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Initial content",
        )

        # Manually set content to empty (bypassing validation)
        prompt.content = ""

        assert prompt.content_length == 0

    def test_word_count_property(self):
        """Test word_count property."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="This is a test prompt with eight words",
        )

        assert prompt.word_count == 8

    def test_word_count_property_empty_content(self):
        """Test word_count property with empty content."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Initial content",
        )

        # Manually set content to empty
        prompt.content = ""

        assert prompt.word_count == 0

    def test_update_content_method(self):
        """Test update_content method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Original content",
        )

        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        prompt.update_content("Updated content")

        assert prompt.content == "Updated content"
        assert prompt.updated_at is not None and original_updated_at is not None
        assert prompt.updated_at > original_updated_at

    def test_add_tag_method(self):
        """Test add_tag method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="existing_tag",
        )

        prompt.add_tag("new_tag")

        assert "new_tag" in prompt.tag_list
        assert "existing_tag" in prompt.tag_list
        assert len(prompt.tag_list) == 2

    def test_add_tag_method_duplicate(self):
        """Test add_tag method with duplicate tag."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="existing_tag",
        )

        prompt.add_tag("existing_tag")

        # Should not add duplicate
        assert prompt.tag_list.count("existing_tag") == 1
        assert len(prompt.tag_list) == 1

    def test_remove_tag_method(self):
        """Test remove_tag method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="tag1, tag2, tag3",
        )

        prompt.remove_tag("tag2")

        assert "tag2" not in prompt.tag_list
        assert "tag1" in prompt.tag_list
        assert "tag3" in prompt.tag_list
        assert len(prompt.tag_list) == 2

    def test_remove_tag_method_nonexistent(self):
        """Test remove_tag method with non-existent tag."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="tag1, tag2",
        )

        prompt.remove_tag("nonexistent_tag")

        # Should remain unchanged
        assert prompt.tag_list == ["tag1", "tag2"]

    def test_has_tag_method(self):
        """Test has_tag method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            tags="tag1, tag2, tag3",
        )

        assert prompt.has_tag("tag2") is True
        assert prompt.has_tag("nonexistent_tag") is False

    def test_set_category_method(self):
        """Test set_category method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        prompt.set_category("New Category")

        assert prompt.category == "New Category"
        assert prompt.updated_at is not None and original_updated_at is not None
        assert prompt.updated_at > original_updated_at

    def test_mark_as_enhancement_method(self):
        """Test mark_as_enhancement method."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        # Mark as enhancement
        prompt.mark_as_enhancement(True)

        assert prompt.is_enhancement_prompt is True
        assert prompt.updated_at is not None and original_updated_at is not None
        assert prompt.updated_at > original_updated_at

        # Unmark as enhancement
        prompt.mark_as_enhancement(False)

        assert prompt.is_enhancement_prompt is False

    def test_metadata_operations(self):
        """Test metadata get and set operations."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        # Test setting metadata
        original_updated_at = prompt.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        prompt.set_metadata("version", 1)
        prompt.set_metadata("source", "test")

        # Test getting metadata
        assert prompt.get_metadata("version") == 1
        assert prompt.get_metadata("source") == "test"
        assert prompt.get_metadata("nonexistent") is None
        assert prompt.get_metadata("nonexistent", "default") == "default"
        assert prompt.updated_at is not None and original_updated_at is not None
        assert prompt.updated_at > original_updated_at

        # Test metadata in dict
        assert prompt.metadata["version"] == 1
        assert prompt.metadata["source"] == "test"

    def test_to_dict_with_metadata(self):
        """Test converting prompt to dictionary with metadata."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 1, 13, 0, 0)
        metadata = {"version": 1, "source": "test"}

        prompt = Prompt(
            id=123,
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            category="Testing",
            tags="tag1, tag2",
            is_enhancement_prompt=True,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )

        prompt_dict = prompt.to_dict(include_metadata=True)

        assert prompt_dict["id"] == 123
        assert prompt_dict["tenant_id"] == "tenant-123"
        assert prompt_dict["user_id"] == "user-456"
        assert prompt_dict["name"] == "test_prompt"
        assert prompt_dict["title"] == "Test Prompt"
        assert prompt_dict["content"] == "Test content"
        assert prompt_dict["category"] == "Testing"
        assert prompt_dict["tags"] == "tag1, tag2"
        assert prompt_dict["tag_list"] == ["tag1", "tag2"]
        assert prompt_dict["is_enhancement_prompt"] is True
        assert prompt_dict["created_at"] == created_at.isoformat()
        assert prompt_dict["updated_at"] == updated_at.isoformat()
        assert prompt_dict["content_length"] == len("Test content")
        assert prompt_dict["word_count"] == 2
        assert prompt_dict["metadata"] == metadata

    def test_to_dict_without_metadata(self):
        """Test converting prompt to dictionary without metadata."""
        prompt = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
        )

        prompt.set_metadata("secret", "hidden")
        prompt_dict = prompt.to_dict(include_metadata=False)

        assert "metadata" not in prompt_dict
        assert "id" in prompt_dict
        assert "name" in prompt_dict

    def test_from_dict_creation(self):
        """Test creating prompt from dictionary."""
        prompt_data = {
            "id": 123,
            "tenant_id": "tenant-123",
            "user_id": "user-456",
            "name": "dict_prompt",
            "title": "Dictionary Prompt",
            "content": "Content from dictionary",
            "category": "Dictionary",
            "tags": "dict, test",
            "is_enhancement_prompt": True,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T13:00:00",
            "metadata": {"source": "dict"},
        }

        prompt = Prompt.from_dict(prompt_data)

        assert prompt.id == 123
        assert prompt.tenant_id == "tenant-123"
        assert prompt.user_id == "user-456"
        assert prompt.name == "dict_prompt"
        assert prompt.title == "Dictionary Prompt"
        assert prompt.content == "Content from dictionary"
        assert prompt.category == "Dictionary"
        assert prompt.tags == "dict, test"
        assert prompt.is_enhancement_prompt is True
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)
        assert prompt.metadata == {"source": "dict"}

    def test_from_dict_with_datetime_objects(self):
        """Test creating prompt from dictionary with datetime objects."""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        prompt_data = {
            "tenant_id": "tenant-123",
            "user_id": "user-456",
            "name": "datetime_prompt",
            "title": "DateTime Prompt",
            "content": "Content with datetime objects",
            "created_at": created_at,
            "updated_at": updated_at,
        }

        prompt = Prompt.from_dict(prompt_data)

        assert prompt.created_at == created_at
        assert prompt.updated_at == updated_at

    def test_from_dict_minimal_data(self):
        """Test creating prompt from dictionary with minimal data."""
        prompt_data = {
            "tenant_id": "tenant-123",
            "user_id": "user-456",
            "name": "minimal_prompt",
            "title": "Minimal Prompt",
            "content": "Minimal content",
        }

        prompt = Prompt.from_dict(prompt_data)

        assert prompt.category == "Uncategorized"
        assert prompt.tags == ""
        assert prompt.is_enhancement_prompt is False
        assert prompt.metadata == {}
        assert prompt.created_at is not None
        assert prompt.updated_at is not None

    def test_from_legacy_dict(self):
        """Test creating prompt from legacy dictionary format."""
        legacy_data = {
            "id": 123,
            "name": "legacy_prompt",
            "content": "Legacy content",
            "category": "Legacy",
            "tags": "legacy, old",
            "is_enhancement_prompt": False,
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 13, 0, 0),
        }

        prompt = Prompt.from_legacy_dict(legacy_data, "tenant-789", "user-101")

        assert prompt.id == 123
        assert prompt.tenant_id == "tenant-789"
        assert prompt.user_id == "user-101"
        assert prompt.name == "legacy_prompt"
        assert prompt.title == "legacy_prompt"  # Falls back to name
        assert prompt.content == "Legacy content"
        assert prompt.category == "Legacy"
        assert prompt.tags == "legacy, old"

    def test_from_legacy_dict_with_title(self):
        """Test creating prompt from legacy dictionary with title."""
        legacy_data = {
            "name": "legacy_prompt",
            "title": "Legacy Title",
            "content": "Legacy content",
        }

        prompt = Prompt.from_legacy_dict(legacy_data, "tenant-789", "user-101")

        assert prompt.title == "Legacy Title"

    def test_to_legacy_dict(self):
        """Test converting prompt to legacy dictionary format."""
        prompt = Prompt(
            id=123,
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            category="Testing",
            tags="tag1, tag2",
            is_enhancement_prompt=True,
        )

        legacy_dict = prompt.to_legacy_dict()

        assert legacy_dict["id"] == 123
        assert legacy_dict["name"] == "test_prompt"
        assert legacy_dict["title"] == "Test Prompt"
        assert legacy_dict["content"] == "Test content"
        assert legacy_dict["category"] == "Testing"
        assert legacy_dict["tags"] == "tag1, tag2"
        assert legacy_dict["is_enhancement_prompt"] is True
        assert legacy_dict["tenant_id"] == "tenant-123"
        assert legacy_dict["user_id"] == "user-456"
        assert "created_at" in legacy_dict
        assert "updated_at" in legacy_dict

    def test_clone_method(self):
        """Test cloning a prompt."""
        original = Prompt(
            id=123,
            tenant_id="tenant-123",
            user_id="user-456",
            name="original_prompt",
            title="Original Prompt",
            content="Original content",
            category="Original",
            tags="original, test",
            is_enhancement_prompt=True,
            metadata={"version": 1},
        )

        cloned = original.clone()

        # Should have different ID and name
        assert cloned.id is None
        assert cloned.name == "original_prompt_copy"

        # Should have same content but different timestamps
        assert cloned.tenant_id == original.tenant_id
        assert cloned.user_id == original.user_id
        assert cloned.title == original.title
        assert cloned.content == original.content
        assert cloned.category == original.category
        assert cloned.tags == original.tags
        assert cloned.is_enhancement_prompt == original.is_enhancement_prompt
        assert cloned.metadata == original.metadata
        assert cloned.created_at != original.created_at
        assert cloned.updated_at != original.updated_at

    def test_clone_method_with_new_name(self):
        """Test cloning a prompt with new name."""
        original = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="original_prompt",
            title="Original Prompt",
            content="Original content",
        )

        cloned = original.clone(new_name="cloned_prompt")

        assert cloned.name == "cloned_prompt"
        assert cloned.title == original.title

    def test_clone_method_with_new_tenant(self):
        """Test cloning a prompt with new tenant."""
        original = Prompt(
            tenant_id="tenant-123",
            user_id="user-456",
            name="original_prompt",
            title="Original Prompt",
            content="Original content",
        )

        cloned = original.clone(new_tenant_id="tenant-789")

        assert cloned.tenant_id == "tenant-789"
        assert cloned.user_id == original.user_id

    def test_string_representations(self):
        """Test string representation methods."""
        prompt = Prompt(
            id=123,
            tenant_id="tenant-123",
            user_id="user-456",
            name="test_prompt",
            title="Test Prompt",
            content="Test content",
            category="Testing",
        )

        str_repr = str(prompt)
        assert "test_prompt" in str_repr
        assert "Testing" in str_repr
        assert "tenant-123" in str_repr

        repr_str = repr(prompt)
        assert "123" in repr_str
        assert "test_prompt" in repr_str
        assert "Test Prompt" in repr_str
        assert "tenant_id=tenant-123" in repr_str
        assert "user_id=user-456" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])
