#!/usr/bin/env python3
"""
Test script to verify the new prompt management architecture.

This script tests the migration from legacy prompt_data_manager to
the new repository pattern with PromptService and PromptRepository.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config.settings import DatabaseConfig, DatabaseType
from src.core.base.database_manager import DatabaseManager
from src.prompts.services.prompt_service import PromptService
from src.prompts.models.prompt import Prompt


def test_new_prompt_architecture():
    """Test the new prompt architecture components."""
    print("🧪 Testing New Prompt Architecture")
    print("=" * 50)
    
    # Create temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Setup database configuration
        db_config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            db_path=temp_db.name
        )
        
        # Initialize database manager and service
        db_manager = DatabaseManager(db_config)
        prompt_service = PromptService(db_manager)
        
        # Test data
        tenant_id = "test-tenant-123"
        user_id = "test-user-456"
        
        print(f"✅ Database manager initialized: {db_config.db_type.value}")
        print(f"✅ Prompt service initialized")
        print(f"✅ Test tenant: {tenant_id}")
        print()
        
        # Test 1: Create a prompt
        print("📝 Test 1: Creating a prompt")
        result = prompt_service.create_prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            name="test_prompt",
            title="Test Prompt Title",
            content="This is a test prompt content for validation.",
            category="Testing",
            tags="test, validation, new-architecture",
            is_enhancement_prompt=False
        )
        
        if result.success:
            print(f"✅ Prompt created successfully: {result.message}")
            created_prompt = result.data
            if created_prompt:
                print(f"   - ID: {created_prompt.id}")
                print(f"   - Name: {created_prompt.name}")
                print(f"   - Category: {created_prompt.category}")
                print(f"   - Tags: {created_prompt.tag_list}")
            else:
                print("⚠️ Prompt service returned success but no data - checking database...")
                # Check if the prompt was actually saved
                with db_manager.get_connection_context() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM prompts WHERE name = 'test_prompt'")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print("✅ Prompt was actually saved in database")
                    else:
                        print("❌ Prompt was not saved")
                        return False
        else:
            print(f"❌ Failed to create prompt: {result.error}")
            return False
        
        print()
        
        # Test 2: Create an enhancement prompt
        print("🚀 Test 2: Creating an enhancement prompt")
        result = prompt_service.create_prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            name="enhance_writing",
            title="Writing Enhancement Prompt",
            content="Please improve the writing style and clarity of the following text:",
            category="Enhancement",
            tags="writing, enhancement, style",
            is_enhancement_prompt=True
        )
        
        if result.success:
            print(f"✅ Enhancement prompt created: {result.message}")
            if result.data:
                print(f"   - Enhancement flag: {result.data.is_enhancement_prompt}")
            else:
                print("⚠️ Enhancement prompt service returned success but no data")
        else:
            print(f"❌ Failed to create enhancement prompt: {result.error}")
            return False
        
        print()
        
        # Test 3: Get all prompts
        print("📋 Test 3: Retrieving all prompts")
        result = prompt_service.get_all_prompts(tenant_id)
        
        if result.success:
            prompts = result.data
            print(f"✅ Retrieved {len(prompts)} prompts")
            for prompt in prompts:
                prompt_type = "Enhancement" if prompt.is_enhancement_prompt else "Regular"
                print(f"   - {prompt.name} ({prompt_type}) - {prompt.category}")
        else:
            print(f"❌ Failed to retrieve prompts: {result.error}")
            return False
        
        print()
        
        # Test 4: Search prompts
        print("🔍 Test 4: Searching prompts")
        result = prompt_service.search_prompts(
            tenant_id=tenant_id,
            search_term="test",
            include_enhancement_prompts=True
        )
        
        if result.success:
            found_prompts = result.data
            print(f"✅ Found {len(found_prompts)} prompts matching 'test'")
            for prompt in found_prompts:
                print(f"   - {prompt.name}: {prompt.title}")
        else:
            print(f"❌ Failed to search prompts: {result.error}")
            return False
        
        print()
        
        # Test 5: Get categories and tags
        print("🏷️  Test 5: Getting categories and tags")
        
        categories_result = prompt_service.get_categories(tenant_id)
        tags_result = prompt_service.get_tags(tenant_id)
        
        if categories_result.success and tags_result.success:
            print(f"✅ Categories: {categories_result.data}")
            print(f"✅ Tags: {tags_result.data}")
        else:
            print(f"❌ Failed to get categories or tags")
            return False
        
        print()
        
        # Test 6: Update a prompt
        print("✏️  Test 6: Updating a prompt")
        result = prompt_service.update_prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            original_name="test_prompt",
            new_name="updated_test_prompt",
            title="Updated Test Prompt Title",
            content="This is updated content for the test prompt.",
            category="Updated Testing",
            tags="updated, test, validation",
            is_enhancement_prompt=False
        )
        
        if result.success:
            print(f"✅ Prompt updated: {result.message}")
            updated_prompt = result.data
            print(f"   - New name: {updated_prompt.name}")
            print(f"   - New category: {updated_prompt.category}")
        else:
            print(f"❌ Failed to update prompt: {result.error}")
            return False
        
        print()
        
        # Test 7: Duplicate a prompt
        print("📋 Test 7: Duplicating a prompt")
        result = prompt_service.duplicate_prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            original_name="updated_test_prompt",
            new_name="duplicated_prompt"
        )
        
        if result.success:
            print(f"✅ Prompt duplicated: {result.message}")
            print(f"   - Original: updated_test_prompt")
            print(f"   - Duplicate: {result.data.name}")
        else:
            print(f"❌ Failed to duplicate prompt: {result.error}")
            return False
        
        print()
        
        # Test 8: Get statistics
        print("📊 Test 8: Getting statistics")
        result = prompt_service.get_statistics(tenant_id)
        
        if result.success:
            stats = result.data
            print(f"✅ Statistics retrieved:")
            print(f"   - Total prompts: {stats['total_prompts']}")
            print(f"   - Enhancement prompts: {stats['enhancement_prompts']}")
            print(f"   - Regular prompts: {stats['regular_prompts']}")
            print(f"   - Categories: {stats['categories']}")
            print(f"   - Recent prompts: {stats['recent_prompts']}")
        else:
            print(f"❌ Failed to get statistics: {result.error}")
            return False
        
        print()
        
        # Test 9: Delete a prompt
        print("🗑️  Test 9: Deleting a prompt")
        result = prompt_service.delete_prompt(tenant_id, "duplicated_prompt")
        
        if result.success:
            print(f"✅ Prompt deleted: {result.message}")
        else:
            print(f"❌ Failed to delete prompt: {result.error}")
            return False
        
        print()
        
        # Test 10: Validation errors
        print("⚠️  Test 10: Testing validation")
        result = prompt_service.create_prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            name="",  # Invalid: empty name
            title="Test",
            content="Test content"
        )
        
        if not result.success and result.error_code == "VALIDATION_ERROR":
            print(f"✅ Validation working correctly: {result.error}")
        else:
            print(f"❌ Validation not working as expected")
            return False
        
        print()
        print("🎉 All tests passed! New prompt architecture is working correctly.")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary database
        try:
            os.unlink(temp_db.name)
        except:
            pass


if __name__ == "__main__":
    success = test_new_prompt_architecture()
    sys.exit(0 if success else 1)