#!/usr/bin/env python3
"""
Debug script to understand Gradio app structure
"""
import os
import sys

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment for single-user mode to avoid auth complexity
os.environ["MULTITENANT_MODE"] = "false"
os.environ["ENABLE_API"] = "true"
os.environ["LOCAL_DEV_MODE"] = "true"

try:
    from prompt_manager import create_interface

    print("🔧 Creating Gradio interface...")
    app = create_interface()

    print(f"🔍 Gradio app type: {type(app)}")
    print(f"🔍 Gradio app class: {app.__class__.__name__}")
    print(f"🔍 Gradio app module: {app.__class__.__module__}")

    # Check for different possible attributes
    attrs_to_check = ["fastapi_app", "app", "server", "root_app", "_app", "web_app"]

    print("\n🔍 Checking attributes:")
    for attr in attrs_to_check:
        if hasattr(app, attr):
            attr_obj = getattr(app, attr)
            print(f"  ✅ {attr}: {type(attr_obj)} - {attr_obj.__class__.__name__}")
        else:
            print(f"  ❌ {attr}: Not found")

    # Show all non-private attributes
    print(f"\n🔍 All public attributes:")
    public_attrs = [attr for attr in dir(app) if not attr.startswith("_")]
    for attr in public_attrs[:20]:  # Show first 20 to avoid overflow
        try:
            attr_obj = getattr(app, attr)
            attr_type = type(attr_obj).__name__
            print(f"  • {attr}: {attr_type}")
        except Exception as e:
            print(f"  • {attr}: Error accessing - {e}")

    if len(public_attrs) > 20:
        print(f"  ... and {len(public_attrs) - 20} more attributes")

    # Check the app.app object for FastAPI
    if hasattr(app, "app"):
        gradio_app = app.app
        print(f"\n🔍 gradio.routes.App type: {type(gradio_app)}")

        fastapi_attrs = ["fastapi_app", "app", "server", "_app", "root_app"]
        print("\n🔍 Checking gradio.routes.App for FastAPI:")
        for attr in fastapi_attrs:
            if hasattr(gradio_app, attr):
                attr_obj = getattr(gradio_app, attr)
                print(f"  ✅ {attr}: {type(attr_obj)} - {attr_obj.__class__.__name__}")
            else:
                print(f"  ❌ {attr}: Not found")

        # Show all attributes of gradio.routes.App
        print(f"\n🔍 gradio.routes.App public attributes:")
        app_attrs = [attr for attr in dir(gradio_app) if not attr.startswith("_")]
        for attr in app_attrs[:15]:  # Show first 15
            try:
                attr_obj = getattr(gradio_app, attr)
                attr_type = type(attr_obj).__name__
                print(f"  • {attr}: {attr_type}")
            except Exception as e:
                print(f"  • {attr}: Error - {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
