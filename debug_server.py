#!/usr/bin/env python3
"""
Debug server startup to see what's happening with API integration
"""
import os
import sys

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Set environment for testing
os.environ["MULTITENANT_MODE"] = "false"
os.environ["ENABLE_API"] = "true"
os.environ["LOCAL_DEV_MODE"] = "true"

try:
    from api_endpoints import APIManager
    from prompt_manager import create_interface

    print("🔧 Creating Gradio interface...")
    app = create_interface()

    print("🔧 Creating API manager...")
    api_manager = APIManager()

    print("🔧 Getting API router...")
    api_router = api_manager.get_router()

    print(f"🔍 API router type: {type(api_router)}")
    print(f"🔍 API router routes: {len(api_router.routes)} routes")

    for i, route in enumerate(api_router.routes):
        print(f"  Route {i}: {route.path} - {getattr(route, 'methods', 'unknown')}")

    print("🔧 Getting Gradio app...")
    gradio_app = app.app

    print(f"🔍 Gradio app type: {type(gradio_app)}")
    print(f"🔍 Has include_router: {hasattr(gradio_app, 'include_router')}")

    if hasattr(gradio_app, "include_router"):
        print("✅ Using include_router")
        gradio_app.include_router(api_router, prefix="/api")
    else:
        print("ℹ️ Using manual route addition")
        for route in api_router.routes:
            if hasattr(route, "endpoint") and hasattr(route, "methods"):
                path = f"/api{route.path}"
                gradio_app.add_api_route(
                    path, route.endpoint, methods=list(route.methods)
                )
                print(f"  • Added route: {path}")

    print("🔍 Final Gradio app routes:")
    routes = getattr(gradio_app, "routes", [])
    print(f"  Total routes: {len(routes)}")

    # Look for API routes specifically
    api_routes = [
        route for route in routes if getattr(route, "path", "").startswith("/api")
    ]
    print(f"  API routes found: {len(api_routes)}")
    for i, route in enumerate(api_routes):
        path = getattr(route, "path", "unknown")
        methods = getattr(route, "methods", set())
        print(f"  API Route {i}: {path} - {methods}")

    print("✅ Setup complete - API integration ready")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
