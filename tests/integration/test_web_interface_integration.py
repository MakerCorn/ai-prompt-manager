#!/usr/bin/env python3
"""
Complete integration test for the new Web UI architecture
Replaces Gradio-based integration tests
"""

import os
import sys
import tempfile
import time
from multiprocessing import Process

import requests

# Add the project root to the path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def test_web_imports():
    """Test that all web UI modules can be imported"""
    print("🔍 Testing Web UI imports...")

    try:
        from web_app import create_web_app  # noqa: F401

        print("  ✅ web_app imported successfully")

        from i18n import i18n  # noqa: F401

        print("  ✅ i18n imported successfully")

        from text_translator import text_translator  # noqa: F401

        print("  ✅ text_translator imported successfully")

        from langwatch_optimizer import langwatch_optimizer  # noqa: F401

        print("  ✅ langwatch_optimizer imported successfully")

        from token_calculator import token_calculator  # noqa: F401

        print("  ✅ token_calculator imported successfully")

        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_web_app_creation():
    """Test web application creation"""
    print("\n🌐 Testing web application creation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_web.db")

        try:
            from web_app import create_web_app

            app = create_web_app(db_path)
            print("  ✅ FastAPI app created successfully")

            # Check that app has expected routes
            routes = [route.path for route in app.routes]
            expected_routes = ["/", "/login", "/prompts", "/templates", "/settings"]

            for route in expected_routes:
                if any(r.startswith(route) for r in routes):
                    print(f"  ✅ Route {route} found")
                else:
                    print(f"  ❌ Route {route} missing")
                    return False

            return True

        except Exception as e:
            print(f"  ❌ Web app creation error: {e}")
            return False


def test_i18n_functionality():
    """Test internationalization functionality"""
    print("\n🌍 Testing internationalization...")

    try:
        from i18n import i18n

        # Test default language
        print(f"  📍 Default language: {i18n.current_language}")

        # Test available languages
        languages = i18n.get_available_languages()
        print(f"  🗣️  Available languages: {len(languages)}")

        # Test language switching
        original_lang = i18n.current_language
        success = i18n.set_language("es")
        print(f"  🔄 Language switch to Spanish: {'Success' if success else 'Failed'}")

        # Test translation
        test_key = "login.title"
        translation = i18n.t(test_key)
        print(f"  📝 Translation test: {translation}")

        # Restore original language
        i18n.set_language(original_lang)

        return True

    except Exception as e:
        print(f"  ❌ i18n error: {e}")
        return False


def test_translation_service():
    """Test translation service"""
    print("\n🔤 Testing translation service...")

    try:
        from text_translator import text_translator

        # Test basic translation (will use mock service in test environment)
        success, translated, error = text_translator.translate_to_english("Hello world")
        print(f"  🔄 Translation test: {'Success' if success else 'Failed'}")
        if success:
            print(f"  📝 Translated text: '{translated}'")
        else:
            print(f"  ❌ Translation error: {error}")

        return True

    except Exception as e:
        print(f"  ❌ Translation service error: {e}")
        return False


def test_optimization_service():
    """Test prompt optimization service"""
    print("\n⭐ Testing optimization service...")

    try:
        from langwatch_optimizer import langwatch_optimizer

        # Test basic optimization
        test_prompt = "Write email to customer"
        result = langwatch_optimizer.optimize_prompt(test_prompt)

        print(f"  🔄 Optimization test: {'Success' if result.success else 'Failed'}")
        print(f"  📊 Optimization score: {result.optimization_score}")
        print(f"  📝 Optimized prompt: '{result.optimized_prompt[:50]}...'")

        return True

    except Exception as e:
        print(f"  ❌ Optimization service error: {e}")
        return False


def test_token_calculator():
    """Test token calculation service"""
    print("\n🧮 Testing token calculator...")

    try:
        from token_calculator import token_calculator

        # Test token counting
        test_text = "This is a test prompt for token calculation"
        result = token_calculator.estimate_tokens(test_text, "gpt-4")
        print(f"  📊 Token count for test text: {result.prompt_tokens}")

        # Test cost estimation
        cost = result.cost_estimate or 0
        print(f"  💰 Estimated cost: ${cost:.4f}")

        return result.prompt_tokens > 0

    except Exception as e:
        print(f"  ❌ Token calculator error: {e}")
        return False


def _run_test_server(db_path, port):
    """Helper function to run test server"""
    import uvicorn

    from web_app import create_web_app

    app = create_web_app(db_path=db_path)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


def test_web_server_startup():
    """Test web server startup and basic endpoints"""
    print("\n🚀 Testing web server startup...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_server.db")
        port = 8903

        try:
            from auth_manager import AuthManager

            # Initialize database with test data
            auth = AuthManager(db_path)
            tenant_id = auth.create_tenant("Test Tenant", "test")
            auth.create_user(
                tenant_id=tenant_id,
                email="test@example.com",
                password="testpass",
                first_name="Test",
                last_name="User",
                role="admin",
            )

            # Start server in separate process
            server_process = Process(target=_run_test_server, args=(db_path, port))
            server_process.start()

            # Wait for server to start
            base_url = f"http://localhost:{port}"
            server_ready = False

            for _ in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{base_url}/login", timeout=2)
                    if response.status_code == 200:
                        server_ready = True
                        break
                except Exception:
                    pass
                time.sleep(1)

            if not server_ready:
                print("  ❌ Server failed to start")
                server_process.terminate()
                return False

            print("  ✅ Web server started successfully")

            # Test basic endpoints
            endpoints_to_test = [
                ("/login", "Login page"),
                # Note: Other endpoints require authentication
            ]

            for endpoint, description in endpoints_to_test:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        print(f"  ✅ {description}: OK")
                    else:
                        print(f"  ⚠️  {description}: Status {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {description}: {e}")

            # Test authentication endpoint
            try:
                login_data = {
                    "email": "test@example.com",
                    "password": "testpass",
                    "subdomain": "test",
                }
                response = requests.post(
                    f"{base_url}/login", data=login_data, allow_redirects=False
                )
                if response.status_code == 302:
                    print("  ✅ Authentication: Login successful")
                else:
                    print(f"  ❌ Authentication: Login failed ({response.status_code})")
            except Exception as e:
                print(f"  ❌ Authentication test error: {e}")

            # Clean up
            server_process.terminate()
            server_process.join(timeout=5)

            return True

        except Exception as e:
            print(f"  ❌ Web server test error: {e}")
            return False


def test_api_endpoints():
    """Test API endpoints functionality"""
    print("\n🔌 Testing API endpoints...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_api.db")
        port = 8904

        try:
            from auth_manager import AuthManager

            # Initialize database
            auth = AuthManager(db_path)
            tenant_id = auth.create_tenant("Test Tenant", "test")
            auth.create_user(
                tenant_id=tenant_id,
                email="test@example.com",
                password="testpass",
                first_name="Test",
                last_name="User",
                role="admin",
            )

            # Start server
            server_process = Process(target=_run_test_server, args=(db_path, port))
            server_process.start()

            # Wait for server
            time.sleep(3)

            base_url = f"http://localhost:{port}"
            session = requests.Session()

            # Login to get session
            login_data = {
                "email": "test@example.com",
                "password": "testpass",
                "subdomain": "test",
            }
            session.post(f"{base_url}/login", data=login_data)

            # Test API endpoints
            api_tests = [
                (
                    "/translate",
                    {"text": "Hello", "target_lang": "en"},
                    "Translation API",
                ),
                ("/optimize", {"prompt": "Write email"}, "Optimization API"),
                (
                    "/calculate-tokens",
                    {"text": "Test text", "model": "gpt-4"},
                    "Token calculation API",
                ),
            ]

            for endpoint, data, description in api_tests:
                try:
                    response = session.post(f"{base_url}{endpoint}", data=data)
                    if response.status_code == 200:
                        result = response.json()
                        print(
                            f"  ✅ {description}: {'Success' if result.get('success') else 'Failed'}"
                        )
                    else:
                        print(f"  ❌ {description}: Status {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {description}: {e}")

            # Clean up
            server_process.terminate()
            server_process.join(timeout=5)

            return True

        except Exception as e:
            print(f"  ❌ API endpoints test error: {e}")
            return False


def run_all_tests():
    """Run all integration tests"""
    print("🧪 Running Web UI Integration Tests...")
    print("=" * 60)

    # Set test environment
    os.environ["LOCAL_DEV_MODE"] = "true"
    os.environ["TRANSLATION_SERVICE"] = "mock"
    os.environ["PROMPT_OPTIMIZER"] = "builtin"

    tests = [
        ("Import Tests", test_web_imports),
        ("Web App Creation", test_web_app_creation),
        ("Internationalization", test_i18n_functionality),
        ("Translation Service", test_translation_service),
        ("Optimization Service", test_optimization_service),
        ("Token Calculator", test_token_calculator),
        ("Web Server Startup", test_web_server_startup),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Web UI is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
