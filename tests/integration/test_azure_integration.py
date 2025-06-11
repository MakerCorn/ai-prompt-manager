#!/usr/bin/env python3
"""
Test script for Azure AI and Entra ID integration

This script tests the Azure AI and Entra ID features without requiring actual Azure credentials.
It validates the configuration, token calculation, and authentication method detection.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_token_calculator():
    """Test Azure AI models in token calculator"""
    print("🧮 Testing Azure AI Token Calculator...")
    
    try:
        from token_calculator import TokenCalculator
        
        calculator = TokenCalculator()
        
        # Test Azure OpenAI models
        azure_models = ["azure-gpt-4", "azure-gpt-35-turbo", "azure-ai-phi-3", "azure-ai-mistral"]
        
        test_text = "Analyze the performance metrics of our AI system and provide recommendations for optimization."
        
        for model in azure_models:
            try:
                estimate = calculator.estimate_tokens(test_text, model, max_completion_tokens=500)
                
                print(f"  ✅ {model}:")
                print(f"     Prompt tokens: {estimate.prompt_tokens}")
                print(f"     Total tokens: {estimate.total_tokens}")
                print(f"     Tokenizer: {estimate.tokenizer_used}")
                if estimate.cost_estimate:
                    print(f"     Cost estimate: ${estimate.cost_estimate:.4f}")
                print()
                
            except Exception as e:
                print(f"  ❌ {model}: {e}")
        
        # Test supported models list
        supported_models = calculator.get_supported_models()
        azure_supported = [m for m in supported_models if 'azure' in m.lower()]
        print(f"  📋 Azure models in supported list: {azure_supported}")
        
        print("✅ Azure Token Calculator tests completed\n")
        
    except Exception as e:
        print(f"❌ Azure Token Calculator test failed: {e}\n")


def test_entra_id_configuration():
    """Test Entra ID authentication configuration"""
    print("🔐 Testing Entra ID Configuration...")
    
    try:
        from auth_manager import AuthManager
        
        auth = AuthManager()
        
        # Test configuration detection
        entra_enabled = auth.is_entra_id_enabled()
        azure_ai_enabled = auth.is_azure_ai_enabled()
        
        print(f"  📋 Entra ID enabled: {entra_enabled}")
        print(f"  📋 Azure AI enabled: {azure_ai_enabled}")
        
        # Test authentication methods
        auth_methods = auth.get_authentication_methods()
        print(f"  📋 Available authentication methods: {auth_methods}")
        
        # Test Azure configuration
        azure_config = auth.get_azure_ai_config()
        if azure_config:
            print(f"  📋 Azure AI configuration: {list(azure_config.keys())}")
        else:
            print("  📋 No Azure AI configuration found")
        
        # Test Entra ID URL generation (without credentials)
        if entra_enabled:
            login_url = auth.get_entra_id_login_url("test-tenant")
            if login_url:
                print(f"  ✅ Entra ID login URL generated successfully")
            else:
                print(f"  ⚠️  Entra ID login URL generation failed (check configuration)")
        else:
            print(f"  ℹ️  Entra ID not enabled - set ENTRA_ID_ENABLED=true to test")
        
        print("✅ Entra ID configuration tests completed\n")
        
    except Exception as e:
        print(f"❌ Entra ID configuration test failed: {e}\n")


def test_azure_credential_validation():
    """Test Azure credential validation (if configured)"""
    print("🔍 Testing Azure Credential Validation...")
    
    try:
        from auth_manager import AuthManager
        
        auth = AuthManager()
        
        if not auth.is_azure_ai_enabled():
            print("  ℹ️  Azure AI not configured - skipping credential validation")
            print("  💡 To test: Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY")
            return
        
        # Only test validation if Azure is configured
        print("  🔍 Validating Azure credentials...")
        valid, message = auth.validate_azure_credentials()
        
        if valid:
            print(f"  ✅ Azure credentials validated: {message}")
        else:
            print(f"  ⚠️  Azure credential validation: {message}")
        
        print("✅ Azure credential validation tests completed\n")
        
    except Exception as e:
        print(f"❌ Azure credential validation test failed: {e}\n")


def print_environment_info():
    """Print current environment configuration"""
    print("📋 Environment Configuration:")
    
    azure_vars = [
        "ENTRA_ID_ENABLED",
        "ENTRA_CLIENT_ID", 
        "ENTRA_TENANT_ID",
        "AZURE_AI_ENABLED",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_AI_ENDPOINT"
    ]
    
    for var in azure_vars:
        value = os.getenv(var, "Not set")
        # Mask sensitive values
        if "SECRET" in var or "KEY" in var:
            value = "***" if value != "Not set" else "Not set"
        elif "CLIENT_ID" in var or "TENANT_ID" in var:
            value = f"{value[:8]}..." if value != "Not set" and len(value) > 8 else value
        
        print(f"  {var}: {value}")
    
    print()


def main():
    """Run all Azure integration tests"""
    print("🔵 AI Prompt Manager - Azure Integration Tests")
    print("=" * 50)
    print()
    
    print_environment_info()
    
    # Run tests
    test_azure_token_calculator()
    test_entra_id_configuration()
    test_azure_credential_validation()
    
    print("🎉 Azure integration tests completed!")
    print()
    print("💡 Configuration Tips:")
    print("  • Set ENTRA_ID_ENABLED=true to enable Entra ID authentication")
    print("  • Set AZURE_AI_ENABLED=true with endpoint/key to enable Azure AI")
    print("  • See README.md Azure AI & Entra ID Integration section for full setup")


if __name__ == "__main__":
    main()