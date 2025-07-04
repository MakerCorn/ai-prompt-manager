#!/usr/bin/env python3
"""Debug prompt creation issue."""

import logging
import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.core.base.database_manager import DatabaseManager  # noqa: E402
from src.core.config.settings import DatabaseConfig  # noqa: E402
from src.core.config.settings import DatabaseType  # noqa: E402
from src.prompts.models.prompt import Prompt  # noqa: E402
from src.prompts.repositories.prompt_repository import PromptRepository  # noqa: E402

# Setup logging
logging.basicConfig(level=logging.DEBUG)


def debug_prompt_creation():
    """Debug the prompt creation process step by step."""

    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        print("🔍 Debugging Prompt Creation")
        print("=" * 40)

        # Setup database
        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=temp_db.name)

        db_manager = DatabaseManager(db_config)
        repository = PromptRepository(db_manager)

        # Set tenant context
        tenant_id = "test-tenant-123"
        user_id = "test-user-456"
        repository.set_tenant_context(tenant_id)

        print(f"✅ Database initialized: {temp_db.name}")
        print("✅ Repository initialized")
        print(f"✅ Tenant context set: {tenant_id}")
        print()

        # Create a prompt entity
        print("📝 Creating Prompt entity...")
        prompt = Prompt(
            tenant_id=tenant_id,
            user_id=user_id,
            name="debug_test",
            title="Debug Test Prompt",
            content="This is a debug test prompt content.",
            category="Debug",
            tags="debug, test",
            is_enhancement_prompt=False,
        )

        print("✅ Prompt entity created:")
        print(f"   - Name: {prompt.name}")
        print(f"   - Title: {prompt.title}")
        print(f"   - ID: {prompt.id}")
        print()

        # Test _entity_to_dict conversion
        print("🔄 Testing entity to dict conversion...")
        entity_dict = repository._entity_to_dict(prompt)
        print("✅ Entity converted to dict:")
        for key, value in entity_dict.items():
            print("   - {key}: {value}")
        print()

        # Test save operation
        print("💾 Testing save operation...")
        try:
            saved_prompt = repository.save(prompt)
            if saved_prompt:
                print("✅ Prompt saved successfully!")
                print("   - ID: {saved_prompt.id}")
                print("   - Name: {saved_prompt.name}")
                print("   - Created: {saved_prompt.created_at}")
            else:
                print("❌ Save returned None")

                # Let's test find_by_id manually to see the issue
                print("🔍 Testing find_by_id with ID 1...")
                found_prompt = repository.find_by_id(1)
                if found_prompt:
                    print("✅ Found prompt by ID: {found_prompt.name}")
                else:
                    print("❌ Could not find prompt by ID 1")

        except Exception as e:
            print(f"❌ Save failed with error: {e}")
            import traceback

            traceback.print_exc()

        print()

        # Test direct database query
        print("🗃️  Testing direct database query...")
        try:
            with db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'"
                )
                table_exists = cursor.fetchone()

                if table_exists:
                    print("✅ Prompts table exists")
                    cursor.execute("SELECT COUNT(*) FROM prompts")
                    count = cursor.fetchone()[0]
                    print("✅ Prompts table has {count} records")

                    if count > 0:
                        cursor.execute("SELECT * FROM prompts")
                        rows = cursor.fetchall()
                        for row in rows:
                            print("   - Record: {dict(row)}")
                else:
                    print("❌ Prompts table does not exist")

        except Exception as e:
            print(f"❌ Database query failed: {e}")
            import traceback

            traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Clean up
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


if __name__ == "__main__":
    debug_prompt_creation()
