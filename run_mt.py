#!/usr/bin/env python3
"""
Multi-tenant AI Prompt Manager launcher script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from prompt_manager_mt import create_interface
    
    # Get configuration from environment
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 7860))
    
    print("🚀 Starting Multi-Tenant AI Prompt Manager...")
    print(f"🌐 Server: http://{host}:{port}")
    print("🏢 Local Development Tenant: localhost")
    print("👤 Default Admin: admin@localhost / admin123")
    print("=" * 50)
    
    # Create and launch the interface
    app = create_interface()
    app.launch(
        server_name=host,
        server_port=port,
        share=False,
        show_error=True,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )