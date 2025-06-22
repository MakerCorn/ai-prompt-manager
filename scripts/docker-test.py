#!/usr/bin/env python3
"""
Docker build test script to verify architecture components can be imported and initialized.
"""
import os
import sys
import tempfile

# Add src to Python path
sys.path.insert(0, "./src")


def test_imports():
    """Test that all components can be imported."""
    try:
        # Test legacy imports
        import api_endpoints  # noqa: F401
        import auth_manager  # noqa: F401
        import prompt_manager  # noqa: F401
        from src.core.base.database_manager import \
            DatabaseManager  # noqa: F401
        # Test new architecture imports
        from src.core.config.settings import AppConfig  # noqa: F401
        from src.core.config.settings import DatabaseConfig  # noqa: F401
        from src.prompts.models.prompt import Prompt  # noqa: F401
        from src.prompts.services.prompt_service import \
            PromptService  # noqa: F401

        print("✅ Docker build: All imports successful")
        return True
    except Exception as e:
        print(f"❌ Docker build: Import failed: {e}")
        return False


def test_new_architecture():
    """Test that new architecture services can be initialized."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        from src.core.base.database_manager import DatabaseManager
        from src.core.config.settings import DatabaseConfig, DatabaseType
        from src.prompts.services.prompt_service import PromptService

        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=temp_db.name)
        db_manager = DatabaseManager(db_config)
        prompt_service = PromptService(db_manager)  # noqa: F841

        print("✅ Docker build: New architecture services initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Docker build: New architecture test failed: {e}")
        return False
    finally:
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


if __name__ == "__main__":
    success = test_imports() and test_new_architecture()
    sys.exit(0 if success else 1)
