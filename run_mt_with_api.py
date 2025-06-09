#!/usr/bin/env python3
"""
Multi-tenant AI Prompt Manager with integrated REST API
Launcher that combines Gradio web interface with FastAPI REST endpoints
"""

import os
import threading
import uvicorn
from contextlib import asynccontextmanager

# Set environment for local development
os.environ.setdefault("LOCAL_DEV_MODE", "true")

from prompt_manager_mt import create_interface
from api_endpoints import get_api_app

@asynccontextmanager
async def lifespan(app):
    """Lifecycle management for the combined application"""
    print("🚀 Starting AI Prompt Manager with API endpoints...")
    yield
    print("📴 Shutting down AI Prompt Manager...")

def create_combined_app():
    """Create combined Gradio + FastAPI application"""
    
    # Create the Gradio interface first
    gradio_app = create_interface()
    
    # Get the FastAPI app from the Gradio app
    fastapi_app = gradio_app.fastapi_app if hasattr(gradio_app, 'fastapi_app') else gradio_app.app
    
    # Initialize API manager and add routes to the FastAPI app
    from api_endpoints import APIManager
    api_manager = APIManager()
    
    # Include all routes from the API app
    fastapi_app.include_router(api_manager.app.router)
    
    print("🔌 Added API routes to Gradio FastAPI app")
    print(f"📊 Total routes: {len(fastapi_app.routes)}")
    
    return gradio_app

def run_combined_server():
    """Run the combined server with both Gradio UI and REST API"""
    
    print("=" * 80)
    print("🤖 AI PROMPT MANAGER - MULTI-TENANT WITH API")
    print("=" * 80)
    print()
    print("Features:")
    print("  🔐 Secure Authentication (Email/Password + SSO/ADFS)")
    print("  🏢 Multi-Tenant Architecture with Data Isolation")
    print("  👥 User Management with Role-Based Access Control")
    print("  🛡️ Admin Panel for Tenant & User Management")
    print("  📝 Advanced Prompt Management with AI Enhancement")
    print("  🔑 API Token Management with Secure REST Access")
    print("  📊 REST API Endpoints for Programmatic Access")
    print()
    print("Interfaces:")
    print("  🌐 Web UI: http://localhost:7860")
    print("  📖 API Docs: http://localhost:7860/api/docs")
    print("  🔍 API Explorer: http://localhost:7860/api/redoc")
    print()
    print("Default Development Credentials:")
    print("  📧 Email: admin@localhost")
    print("  🔑 Password: admin123")
    print("  🏢 Tenant: localhost")
    print()
    print("API Usage:")
    print("  1. Login to web interface")
    print("  2. Go to Account Settings → API Tokens")
    print("  3. Create a new API token")
    print("  4. Use token with: Authorization: Bearer apm_your_token")
    print()
    print("=" * 80)
    print()
    
    # Create the combined application
    app = create_combined_app()
    
    # Launch using Gradio's built-in server which handles FastAPI integration
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    run_combined_server()