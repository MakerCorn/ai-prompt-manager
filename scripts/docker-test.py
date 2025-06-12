#!/usr/bin/env python3
"""
Docker build test script to verify architecture components can be imported and initialized.
"""
import sys
import tempfile
import os

# Add src to Python path
sys.path.insert(0, './src')

def test_imports():
    """Test that all components can be imported."""
    try:
        # Test legacy imports
        import prompt_manager
        import auth_manager
        import api_endpoints
        
        # Test new architecture imports
        from src.core.config.settings import AppConfig, DatabaseConfig, DatabaseType
        from src.prompts.models.prompt import Prompt
        from src.core.base.database_manager import DatabaseManager
        from src.prompts.services.prompt_service import PromptService
        
        print('✅ Docker build: All imports successful')
        return True
    except Exception as e:
        print(f'❌ Docker build: Import failed: {e}')
        return False

def test_new_architecture():
    """Test that new architecture services can be initialized."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        from src.core.config.settings import DatabaseConfig, DatabaseType
        from src.core.base.database_manager import DatabaseManager
        from src.prompts.services.prompt_service import PromptService
        
        db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=temp_db.name)
        db_manager = DatabaseManager(db_config)
        prompt_service = PromptService(db_manager)
        
        print('✅ Docker build: New architecture services initialized successfully')
        return True
    except Exception as e:
        print(f'❌ Docker build: New architecture test failed: {e}')
        return False
    finally:
        try:
            os.unlink(temp_db.name)
        except:
            pass

if __name__ == '__main__':
    success = test_imports() and test_new_architecture()
    sys.exit(0 if success else 1)