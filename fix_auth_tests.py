#!/usr/bin/env python3
"""
Fix auth manager tests with incorrect tenant creation patterns
"""

import re

def fix_auth_tests():
    # Read the file
    with open('tests/unit/test_auth_manager.py', 'r') as f:
        content = f.read()
    
    # Pattern 1: Fix auth_manager.create_user calls that use sample_tenant_data["id"] directly
    # Replace them with the pattern of getting tenant after creation
    
    # Find all test methods that have the problematic pattern
    pattern = r'(def test_\w+.*?\n.*?# Create tenant and user.*?\n.*?)auth_manager\.create_tenant\(\s*sample_tenant_data\["name"\], sample_tenant_data\["subdomain"\], sample_tenant_data\["max_users"\]\s*\)\s*\n(.*?)auth_manager\.create_user\(\s*sample_tenant_data\["id"\],'
    
    def replacement(match):
        method_start = match.group(1)
        method_middle = match.group(2)
        
        # Create the replacement pattern
        new_pattern = f'''{method_start}tenant_success, tenant_message = auth_manager.create_tenant(
            sample_tenant_data["name"], sample_tenant_data["subdomain"], sample_tenant_data["max_users"]
        )
        assert tenant_success, f"Failed to create tenant: {{tenant_message}}"
        
        # Get the tenant ID after creation
        tenants = auth_manager.get_all_tenants()
        tenant = next((t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None)
        assert tenant is not None, "Tenant should exist after creation"
        
{method_middle}        user_success, user_message = auth_manager.create_user(
            tenant.id,'''
        
        return new_pattern
    
    # Apply the pattern replacement
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also fix any remaining create_user calls that don't have success checking
    content = re.sub(
        r'auth_manager\.create_user\(\s*tenant\.id,\s*\n(.*?)\)\s*\n\s*\n',
        r'user_success, user_message = auth_manager.create_user(\n            tenant.id,\n\1)\n        assert user_success, f"Failed to create user: {user_message}"\n\n',
        content,
        flags=re.DOTALL
    )
    
    # Write back the file
    with open('tests/unit/test_auth_manager.py', 'w') as f:
        f.write(content)
    
    print("Applied auth manager test fixes")

if __name__ == "__main__":
    fix_auth_tests()