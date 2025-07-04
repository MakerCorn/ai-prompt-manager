#!/usr/bin/env python3
"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

AI Prompt Manager Universal Launcher
Unified launcher supporting all deployment modes via environment variables.

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_arguments():
    """Parse command line arguments for quick configuration"""
    parser = argparse.ArgumentParser(
        description="AI Prompt Manager Universal Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  MULTITENANT_MODE     Enable multi-tenant mode (default: true)
  ENABLE_API          Enable REST API endpoints (default: false)
  SERVER_HOST         Server host (default: 0.0.0.0)
  SERVER_PORT         Server port (default: 7860)
  DB_TYPE             Database type: sqlite or postgres (default: sqlite)
  DEBUG               Enable debug mode (default: false)

Quick Start Examples:
  python run.py                           # Multi-tenant mode
  python run.py --single-user             # Single-user mode
  python run.py --with-api                # Multi-tenant + API
  python run.py --single-user --with-api  # Single-user + API
  python run.py --port 8080               # Custom port
        """,
    )

    # Mode flags
    parser.add_argument(
        "--single-user",
        action="store_true",
        help="Enable single-user mode (no authentication)",
    )
    parser.add_argument(
        "--multi-tenant", action="store_true", help="Enable multi-tenant mode (default)"
    )
    parser.add_argument(
        "--with-api", action="store_true", help="Enable REST API endpoints"
    )

    # Server configuration
    parser.add_argument(
        "--host", default=None, help="Server host (overrides SERVER_HOST)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Server port (overrides SERVER_PORT)"
    )

    # Other options
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--share",
        action="store_true",
        help="Enable Gradio sharing (creates public URL)",
    )

    return parser.parse_args()


def get_configuration(args):
    """Get final configuration from environment variables and arguments"""
    config: dict = {}

    # Mode configuration (args override env vars)
    if args.single_user:
        config["multitenant_mode"] = False
    elif args.multi_tenant:
        config["multitenant_mode"] = True
    else:
        config["multitenant_mode"] = bool(
            os.getenv("MULTITENANT_MODE", "true").lower() == "true"
        )

    # API configuration
    config["enable_api"] = args.with_api or (
        os.getenv("ENABLE_API", "false").lower() == "true"
    )

    # Server configuration (args override env vars)
    config["host"] = str(
        args.host or os.getenv("SERVER_HOST", "0.0.0.0")
    )  # nosec B104: Binding to all interfaces is intentional for web application deployment
    config["port"] = int(args.port or int(os.getenv("SERVER_PORT", "7860")))

    # Other options
    config["debug"] = bool(
        args.debug or (os.getenv("DEBUG", "false").lower() == "true")
    )
    config["share"] = bool(
        args.share or (os.getenv("GRADIO_SHARE", "false").lower() == "true")
    )

    # Database configuration
    config["db_type"] = str(os.getenv("DB_TYPE", "sqlite")).lower()
    config["db_path"] = str(os.getenv("DB_PATH", "prompts.db"))
    config["postgres_dsn"] = os.getenv("POSTGRES_DSN")

    # Development mode
    config["local_dev_mode"] = bool(
        os.getenv("LOCAL_DEV_MODE", "true").lower() == "true"
    )

    return config


def display_startup_info(config):
    """Display startup information and configuration"""
    print("=" * 80)
    print("🤖 AI PROMPT MANAGER - UNIVERSAL LAUNCHER")
    print("=" * 80)
    print()

    # Mode information
    if config["multitenant_mode"]:
        print("🏢 Multi-Tenant Mode: ENABLED")
        print("  🔐 Authentication: Required")
        print("  🛡️ Admin Panel: Available")
        print("  🏢 Data Isolation: Per Tenant")
        print("  👤 Default Admin: admin@localhost / admin123")
        print("  🏠 Default Tenant: localhost")
    else:
        print("👤 Single-User Mode: ENABLED")
        print("  🔐 Authentication: Not Required")
        print("  📝 Direct Access: Available")
        print("  💾 Local Storage: File-based")

    # API information
    if config["enable_api"]:
        print("  📊 REST API: ENABLED")
        print(f"  📖 API Docs: http://{config['host']}:{config['port']}" "/api/docs")
        print(
            f"  🔍 API Explorer: http://{config['host']}:{config['port']}" "/api/redoc"
        )

    # Database information
    print("  💾 Database: {}".format(config["db_type"].upper()))
    if config["db_type"] == "sqlite":
        print(f"  📁 Database File: {config['db_path']}")
    else:
        print("  🔗 Database: PostgreSQL")

    # Development mode
    if config["local_dev_mode"]:
        print("  🔧 Development Mode: ENABLED")

    print()
    print("🌐 Access URLs:")
    print(f"  • Web Interface: http://{config['host']}:{config['port']}")

    if config["enable_api"]:
        print(
            f"  • API Documentation: http://{config['host']}:"
            f"{config['port']}/api/docs"
        )
        print(
            f"  • API Reference: http://{config['host']}:" f"{config['port']}/api/redoc"
        )

    if config["share"]:
        print("  • Public URL: Will be generated by Gradio")

    print()

    # Usage instructions
    if config["multitenant_mode"]:
        print("🚀 Getting Started:")
        print("  1. Open the web interface")
        print("  2. Login with: admin@localhost / admin123")
        print("  3. Start creating and managing prompts")
        if config["enable_api"]:
            print(
                "  4. Create API tokens in Account Settings for " "programmatic access"
            )
    else:
        print("🚀 Getting Started:")
        print("  1. Open the web interface")
        print("  2. Start creating and managing prompts immediately")
        if config["enable_api"]:
            print("  3. API access available without authentication")

    print("=" * 80)
    print()


def main():
    """Main launcher that determines mode and runs appropriate interface"""

    # Parse command line arguments
    args = parse_arguments()

    # Get final configuration
    config = get_configuration(args)

    # Display startup information
    display_startup_info(config)

    # Update display for API integration
    if config["enable_api"]:
        print(f"🔗 API Integration: Unified server approach")
        print(f"   📊 API Endpoints: Same port as Gradio app ({config['port']})")
        print(f"   🌐 API Base URL: http://{config['host']}:{config['port']}/api")
        print()

    # Set environment variables for the application
    if not config["multitenant_mode"]:
        os.environ["MULTITENANT_MODE"] = "false"

    if config["local_dev_mode"]:
        os.environ["LOCAL_DEV_MODE"] = "true"

    # Import and create the interface
    try:
        from prompt_manager import create_interface

        print("🔧 Initializing AI Prompt Manager...")
        app = create_interface()
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)

    # Handle API integration if enabled  
    if config["enable_api"]:
        try:
            print("🔌 Integrating API endpoints into Gradio app...")
            
            from datetime import datetime
            from fastapi import APIRouter

            # Create API router for endpoints
            api_router = APIRouter()

            # Add API endpoints
            @api_router.get("/health")
            async def health_check():
                return {"status": "healthy", "timestamp": datetime.now().isoformat()}

            @api_router.get("/info")
            async def api_info():
                return {
                    "service": "ai-prompt-manager", 
                    "version": "1.0.0",
                    "api_version": "v1",
                }

            @api_router.get("/test")
            async def test_endpoint():
                return {"message": "API integration working", "service": "ai-prompt-manager"}

            # Get the underlying FastAPI app from Gradio
            fastapi_app = app.app

            # Include the API router with /api prefix
            fastapi_app.include_router(api_router, prefix="/api")
            
            print("✅ API endpoints integrated successfully")
            print(f"📖 Health check: http://{config['host']}:{config['port']}/api/health")
            print(f"📖 API info: http://{config['host']}:{config['port']}/api/info")
            print(f"📖 Test endpoint: http://{config['host']}:{config['port']}/api/test")

        except ImportError as e:
            print(f"⚠️  API integration failed (missing dependencies): {e}")
        except Exception as e:
            print(f"⚠️  API integration error: {e}")
            import traceback
            traceback.print_exc()

    # Launch configuration summary
    print("🚀 Launching server...")
    if config["debug"]:
        print("🐛 Debug mode enabled")
    if config["share"]:
        print("🌍 Public sharing enabled")

    # Launch the application
    try:
        app.launch(
            server_name=config["host"],
            server_port=config["port"],
            share=config["share"],
            show_error=True,
            debug=config["debug"],
            quiet=False,
        )
    except Exception as e:
        print(f"❌ Failed to launch server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
