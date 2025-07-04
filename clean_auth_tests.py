#!/usr/bin/env python3
"""
Clean up the auth manager test file to fix duplicated patterns
"""

import re

def clean_auth_tests():
    # Read the file
    with open('tests/unit/test_auth_manager.py', 'r') as f:
        content = f.read()
    
    # Fix duplicate assignment patterns like "var = var = value"
    content = re.sub(r'(\w+), (\w+) = \1, \2 = ', r'\1, \2 = ', content)
    
    # Remove duplicate tenant creation/assertion blocks
    content = re.sub(
        r'(\s+)assert tenant_success, f"Failed to create tenant: \{tenant_message\}"\s*\n\s*\n\s*# Get the tenant ID after creation\s*\n\s*tenants = auth_manager\.get_all_tenants\(\)\s*\n\s*tenant = next\(\(t for t in tenants if t\.subdomain == sample_tenant_data\["subdomain"\]\), None\)\s*\n\s*assert tenant is not None, "Tenant should exist after creation"\s*\n\s*\n(\1)assert tenant_success, f"Failed to create tenant: \{tenant_message\}"\s*\n\s*\n\s*# Get the tenant ID after creation by finding it in all tenants\s*\n\s*tenants = auth_manager\.get_all_tenants\(\)\s*\n\s*tenant = next\(\(t for t in tenants if t\.subdomain == sample_tenant_data\["subdomain"\]\), None\)\s*\n\s*assert tenant is not None, "Tenant should exist after creation"\s*\n',
        r'\1assert tenant_success, f"Failed to create tenant: {tenant_message}"\n        \n        # Get the tenant ID after creation by finding it in all tenants\n        tenants = auth_manager.get_all_tenants()\n        tenant = next((t for t in tenants if t.subdomain == sample_tenant_data["subdomain"]), None)\n        assert tenant is not None, "Tenant should exist after creation"\n        \n',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Fix incomplete patterns where create_user isn't being called properly
    # Find patterns where there's the user_success assignment but it's orphaned
    content = re.sub(
        r'(\s+)user_success, user_message = user_success, user_message = auth_manager\.create_user\(\s*\n\s*tenant\.id,\s*\n(.*?)\s*\)',
        r'\1user_success, user_message = auth_manager.create_user(\n            tenant.id,\n\2)',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Fix any remaining orphaned patterns
    content = re.sub(
        r'(\s+)user_success, user_message = user_success, user_message = auth_manager\.create_user\(',
        r'\1user_success, user_message = auth_manager.create_user(',
        content
    )
    
    # Write back the file
    with open('tests/unit/test_auth_manager.py', 'w') as f:
        f.write(content)
    
    print("Cleaned up auth manager test duplicates")

if __name__ == "__main__":
    clean_auth_tests()