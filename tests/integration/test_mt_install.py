#!/usr/bin/env python3
"""
Installation and basic functionality test for Multi-Tenant AI Prompt Manager
"""

import os
import sys
import tempfile


def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from auth_manager import AuthManager  # noqa: F401

        print("  ✅ auth_manager imported successfully")

        from prompt_data_manager import PromptDataManager  # noqa: F401

        print("  ✅ prompt_data_manager imported successfully")

        from prompt_manager import create_interface  # noqa: F401

        print("  ✅ prompt_manager imported successfully")

        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_database_creation():
    """Test database initialization"""
    print("\n💾 Testing database creation...")

    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_prompts.db")

        try:
            from auth_manager import AuthManager

            # Initialize with test database
            os.environ["LOCAL_DEV_MODE"] = "true"
            auth = AuthManager(db_path)

            print("  ✅ Database initialized successfully")

            # Check if tables exist by trying to get tenants
            tenants = auth.get_all_tenants()
            print(f"  ✅ Found {len(tenants)} default tenants")

            return True
        except Exception as e:
            print(f"  ❌ Database creation error: {e}")
            return False


def test_authentication_flow():
    """Test complete authentication flow"""
    print("\n🔐 Testing authentication flow...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_auth.db")

        try:
            from auth_manager import AuthManager

            os.environ["LOCAL_DEV_MODE"] = "true"
            auth = AuthManager(db_path)

            # Test tenant creation
            success, message = auth.create_tenant("Test Company", "test-company", 50)
            print(f"  📋 Tenant creation: {message}")

            # Get tenant
            tenants = auth.get_all_tenants()
            test_tenant = next(
                (t for t in tenants if t.subdomain == "test-company"), None
            )

            if not test_tenant:
                print("  ❌ Test tenant not found")
                return False

            # Test user creation
            success, message = auth.create_user(
                test_tenant.id, "test@test.com", "test123", "Test", "User", "user"
            )
            print(f"  👤 User creation: {message}")

            # Test authentication
            auth_success, user, auth_message = auth.authenticate_user(
                "test@test.com", "test123", "test-company"
            )
            print(f"  🔑 Authentication: {auth_message}")

            if not auth_success or not user:
                return False

            # Test session management
            token = auth.create_session(user.id)
            print("  🎫 Session token created")

            valid, validated_user = auth.validate_session(token)
            print(f"  ✅ Session validation: {'Success' if valid else 'Failed'}")

            return valid

        except Exception as e:
            print(f"  ❌ Authentication flow error: {e}")
            return False


def test_prompt_management():
    """Test prompt management with tenant isolation"""
    print("\n📝 Testing prompt management...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_prompts.db")

        try:
            from auth_manager import AuthManager
            from prompt_data_manager import PromptDataManager

            os.environ["LOCAL_DEV_MODE"] = "true"
            auth = AuthManager(db_path)

            # Get default tenant and user
            tenants = auth.get_all_tenants()
            users = auth.get_tenant_users(tenants[0].id)

            # Create data manager
            data_manager = PromptDataManager(
                db_path=db_path, tenant_id=tenants[0].id, user_id=users[0].id
            )

            # Test prompt creation
            result = data_manager.add_prompt(
                "test-prompt", "Test Prompt", "Test content", "Testing", "test", False
            )
            print(f"  📄 Prompt creation: {result}")

            # Test prompt retrieval
            prompts = data_manager.get_all_prompts()
            print(f"  📊 Retrieved {len(prompts)} prompts")

            # Test prompt search
            search_results = data_manager.search_prompts("test")
            print(f"  🔍 Search found {len(search_results)} prompts")

            # Test categories
            categories = data_manager.get_categories()
            print(f"  📁 Found categories: {categories}")

            return len(prompts) > 0

        except Exception as e:
            print(f"  ❌ Prompt management error: {e}")
            return False


def test_ui_creation():
    """Test that the UI can be created"""
    print("\n🖥️ Testing UI creation...")

    try:
        from prompt_manager import create_interface

        # Create interface (without launching)
        create_interface()  # noqa: F841
        print("  ✅ Gradio interface created successfully")

        return True

    except Exception as e:
        print(f"  ❌ UI creation error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Multi-Tenant AI Prompt Manager Installation Test")
    print("=" * 55)

    tests = [
        test_imports,
        test_database_creation,
        test_authentication_flow,
        test_prompt_management,
        test_ui_creation,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n📊 Test Results")
    print("=" * 20)
    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Multi-tenant system is ready to use.")
        print("\n🚀 To start the application:")
        print("   poetry run python run.py")
        print("\n🔑 Default credentials:")
        print("   Email: admin@localhost")
        print("   Password: admin123")
        print("   Tenant: localhost")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
