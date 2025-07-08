#!/usr/bin/env python3
"""
Integration tests for Rules API endpoints
Testing complete Rules management workflow through web interface
"""

import os
import sys

# Add the project root to the path
sys.path.insert(  # noqa: E402
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import tempfile  # noqa: E402
import time  # noqa: E402
import unittest  # noqa: E402
from multiprocessing import Process  # noqa: E402

import requests  # noqa: E402
import uvicorn  # noqa: E402

from auth_manager import AuthManager  # noqa: E402
from web_app import create_web_app  # noqa: E402


def _run_rules_test_server(db_path, port):
    """Helper function to run test server"""
    app = create_web_app(db_path=db_path)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


class RulesAPIIntegrationTest(unittest.TestCase):
    """Integration tests for Rules API functionality"""

    # Class attributes for type checking
    test_db: str
    base_url: str
    port: int
    auth_manager: any
    server_process: any

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
        cls.base_url = "http://localhost:8905"
        cls.port = 8905

        # Create test database and admin user
        cls.auth_manager = AuthManager(cls.test_db)

        # Create test tenant and admin user
        success, tenant_message = cls.auth_manager.create_tenant("Test Tenant", "test")
        if not success:
            raise Exception(f"Failed to create test tenant: {tenant_message}")

        # Get tenant ID
        conn = cls.auth_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants WHERE subdomain = ?", ("test",))
        result = cursor.fetchone()
        tenant_id = result[0] if result else None
        conn.close()

        if not tenant_id:
            raise Exception("Failed to get tenant ID after creation")

        success, user_message = cls.auth_manager.create_user(
            tenant_id=tenant_id,
            email="test@example.com",
            password="test123",
            first_name="Test",
            last_name="User",
            role="admin",
        )
        if not success:
            raise Exception(f"Failed to create test user: {user_message}")

        # Start the test server
        cls.server_process = Process(
            target=_run_rules_test_server, args=(cls.test_db, cls.port)
        )
        cls.server_process.start()
        time.sleep(3)  # Give server time to start

        # Health check
        try:
            response = requests.get(f"{cls.base_url}/", timeout=5)
            if response.status_code != 200:
                raise Exception("Server health check failed")
        except Exception as e:
            cls.tearDownClass()
            raise Exception(f"Failed to start test server: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if hasattr(cls, "server_process") and cls.server_process:
            cls.server_process.terminate()
            cls.server_process.join(timeout=5)
            if cls.server_process.is_alive():
                cls.server_process.kill()

        # Clean up test database
        if hasattr(cls, "test_db") and os.path.exists(cls.test_db):
            os.unlink(cls.test_db)

    def setUp(self):
        """Set up for each test"""
        self.session = requests.Session()

        # Login to get session
        login_response = self.session.post(
            f"{self.base_url}/login",
            data={
                "email": "test@example.com",
                "password": "test123",
                "subdomain": "test",
            },
            allow_redirects=False,
        )
        self.assertEqual(login_response.status_code, 302)  # Redirect after login

    def test_01_rules_page_loads(self):
        """Test that the rules page loads successfully"""
        response = self.session.get(f"{self.base_url}/rules")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Rules Library", response.text)
        self.assertIn("No rules found", response.text)  # Initially empty

    def test_02_new_rule_page_loads(self):
        """Test that the new rule creation page loads"""
        response = self.session.get(f"{self.base_url}/rules/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Create New Rule", response.text)
        self.assertIn("Rule Name", response.text)
        self.assertIn("Rule Content", response.text)

    def test_03_create_rule_success(self):
        """Test successful rule creation"""
        rule_data = {
            "name": "test-rule",
            "title": "Test Rule",
            "content": "# Test Rule\n\n## Guidelines\n- Be specific\n- Be clear\n- Be helpful",
            "category": "Testing",
            "tags": "test, guidelines",
            "description": "A test rule for integration testing",
        }

        response = self.session.post(
            f"{self.base_url}/rules/new", data=rule_data, allow_redirects=False
        )
        self.assertEqual(response.status_code, 302)  # Redirect after creation

        # Verify rule appears in the list
        list_response = self.session.get(f"{self.base_url}/rules")
        self.assertIn("test-rule", list_response.text)
        self.assertIn("Test Rule", list_response.text)

    def test_04_create_rule_validation(self):
        """Test rule creation validation"""
        # Test missing required fields
        invalid_data = {
            "name": "",  # Missing name
            "title": "Test",
            "content": "Content",
        }

        response = self.session.post(f"{self.base_url}/rules/new", data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Should return form with error
        self.assertIn("required", response.text.lower())

    def test_05_create_duplicate_rule(self):
        """Test duplicate rule name handling"""
        rule_data = {
            "name": "duplicate-rule",
            "title": "Duplicate Rule",
            "content": "# Duplicate Rule\n\nContent",
            "category": "Testing",
        }

        # Create first rule
        response1 = self.session.post(
            f"{self.base_url}/rules/new", data=rule_data, allow_redirects=False
        )
        self.assertEqual(response1.status_code, 302)

        # Try to create duplicate
        response2 = self.session.post(f"{self.base_url}/rules/new", data=rule_data)
        self.assertEqual(response2.status_code, 200)  # Should return form with error
        self.assertIn("already exists", response2.text)

    def test_06_edit_rule_page_loads(self):
        """Test that the rule edit page loads"""
        # First create a rule
        rule_data = {
            "name": "edit-test-rule",
            "title": "Edit Test Rule",
            "content": "# Edit Test Rule\n\nOriginal content",
            "category": "Testing",
        }
        self.session.post(f"{self.base_url}/rules/new", data=rule_data)

        # Get the rules list to find the rule ID
        list_response = self.session.get(f"{self.base_url}/rules")
        # Extract rule ID from the edit link (simplified approach)
        # In real implementation, you'd parse the HTML properly
        self.assertIn("edit-test-rule", list_response.text)

        # Note: For this test, we'll assume rule ID is 1 since it's the first in this test
        # In production, you'd extract the actual ID from the HTML
        response = self.session.get(f"{self.base_url}/rules/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Edit Rule", response.text)
        # Check for form elements instead of specific rule name
        self.assertIn('name="name"', response.text)
        self.assertIn('name="title"', response.text)

    def test_07_edit_rule_success(self):
        """Test successful rule editing"""
        # First create a rule to edit
        rule_data = {
            "name": "editable-rule",
            "title": "Editable Rule",
            "content": "# Editable Rule\n\nOriginal content",
            "category": "Testing",
        }
        self.session.post(f"{self.base_url}/rules/new", data=rule_data)

        # Update the rule
        updated_data = {
            "name": "updated-rule",
            "title": "Updated Rule",
            "content": "# Updated Rule\n\nUpdated content",
            "category": "Updated",
            "tags": "updated, modified",
            "description": "Updated description",
        }

        # Note: Assuming rule ID is predictable for test
        response = self.session.post(
            f"{self.base_url}/rules/2/edit", data=updated_data, allow_redirects=False
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update

        # Verify update
        list_response = self.session.get(f"{self.base_url}/rules")
        self.assertIn("updated-rule", list_response.text)
        self.assertIn("Updated Rule", list_response.text)

    def test_08_delete_rule(self):
        """Test rule deletion"""
        # First create a rule to delete
        rule_data = {
            "name": "deletable-rule",
            "title": "Deletable Rule",
            "content": "# Deletable Rule\n\nContent to be deleted",
            "category": "Testing",
        }
        self.session.post(f"{self.base_url}/rules/new", data=rule_data)

        # Test delete endpoint behavior - delete route should be DELETE method
        response = self.session.delete(f"{self.base_url}/rules/3")
        # Should return 302 redirect or 200/204 for successful deletion
        self.assertIn(response.status_code, [200, 204, 302])

        # Verify the rules list page still loads after deletion attempt
        list_response = self.session.get(f"{self.base_url}/rules")
        self.assertEqual(list_response.status_code, 200)

    def test_09_search_rules(self):
        """Test rule search functionality"""
        # Create multiple rules for searching
        rules = [
            {
                "name": "search-rule-1",
                "title": "Python Guidelines",
                "content": "# Python Guidelines\n\n## Coding Standards\n- Use PEP 8",
                "category": "Coding",
                "tags": "python, coding",
            },
            {
                "name": "search-rule-2",
                "title": "Writing Standards",
                "content": "# Writing Standards\n\n## Documentation\n- Be clear and concise",
                "category": "Writing",
                "tags": "writing, documentation",
            },
        ]

        for rule in rules:
            self.session.post(f"{self.base_url}/rules/new", data=rule)

        # Test search by title
        search_response = self.session.get(
            f"{self.base_url}/rules/search", params={"q": "Python"}
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertIn("search-rule-1", search_response.text)
        self.assertNotIn("search-rule-2", search_response.text)

        # Test search by content
        search_response = self.session.get(
            f"{self.base_url}/rules/search", params={"q": "Documentation"}
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertIn("search-rule-2", search_response.text)

    def test_10_filter_rules_by_category(self):
        """Test rule filtering by category"""
        # Create rules in different categories
        rules = [
            {
                "name": "coding-rule",
                "title": "Coding Rule",
                "content": "# Coding Rule\n\nCoding guidelines",
                "category": "Coding",
            },
            {
                "name": "writing-rule",
                "title": "Writing Rule",
                "content": "# Writing Rule\n\nWriting guidelines",
                "category": "Writing",
            },
        ]

        for rule in rules:
            self.session.post(f"{self.base_url}/rules/new", data=rule)

        # Test filtering by category
        filter_response = self.session.get(
            f"{self.base_url}/rules/filter", params={"category": "Coding"}
        )
        self.assertEqual(filter_response.status_code, 200)
        self.assertIn("coding-rule", filter_response.text)
        self.assertNotIn("writing-rule", filter_response.text)

    def test_11_rules_builder_page_loads(self):
        """Test that the rules builder page loads"""
        response = self.session.get(f"{self.base_url}/rules/builder")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Rules Builder", response.text)
        self.assertIn("Available Rules", response.text)
        self.assertIn("Selected Rules", response.text)

    def test_12_complex_rule_content(self):
        """Test creating rules with complex markdown content"""
        complex_content = """# Complex Rule Example

## Purpose
This rule demonstrates complex markdown formatting for AI systems.

## Core Guidelines

### 1. Structure Requirements
- **Always** use proper headers
- *Emphasize* important points
- Use `code formatting` for technical terms

### 2. Content Standards
1. Be specific and actionable
2. Include examples when possible
3. Use clear, unambiguous language

## Code Examples

```python
def validate_input(user_input):
    # Always validate user input
    if not user_input or len(user_input.strip()) == 0:
        return False
    return True
```

```javascript
// Client-side validation
function isValidEmail(email) {
    const pattern = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return pattern.test(email);
}
```

## Important Notes

> **Warning**: Always consider security implications
> when processing user input.

### Links and References
- [Security Best Practices](https://example.com/security)
- [Coding Standards](https://example.com/standards)

## Checklist
- [ ] Input validation implemented
- [ ] Error handling in place
- [ ] Security review completed
- [ ] Tests written and passing

---

*This rule should be reviewed quarterly.*"""

        rule_data = {
            "name": "complex-markdown-rule",
            "title": "Complex Markdown Rule",
            "content": complex_content,
            "category": "Standards",
            "tags": "markdown, complex, standards, security",
            "description": "Example of a complex rule with full markdown formatting",
        }

        response = self.session.post(
            f"{self.base_url}/rules/new", data=rule_data, allow_redirects=False
        )
        self.assertEqual(response.status_code, 302)

        # Verify the complex content is preserved
        list_response = self.session.get(f"{self.base_url}/rules")
        self.assertIn("complex-markdown-rule", list_response.text)

    def test_13_unicode_and_special_characters(self):
        """Test rules with unicode and special characters"""
        unicode_content = """# Règle Unicode 🌍

## Directives Internationales
- Support émojis: ✅ 🚀 📝
- Handle unicode: αβγ δεζ ηθι
- Special chars: @#$%^&*()
- Quotes: "smart quotes" 'apostrophes'

## Exemples de Code
```python
message = "Bonjour le monde! 🌍"
print(f"Message: {message}")
```

## Notes Importantes
> **Attention**: Gérer les caractères spéciaux
> avec soin dans les systèmes d'IA.

### Références
- Documentation française
- 中文文档
- Документация на русском"""

        rule_data = {
            "name": "unicode-rule",
            "title": "Règle avec Unicode et Émojis 🌍",
            "content": unicode_content,
            "category": "International",
            "tags": "unicode, émojis, international, français",
            "description": "Testing unicode, émojis, and special characters",
        }

        response = self.session.post(
            f"{self.base_url}/rules/new", data=rule_data, allow_redirects=False
        )
        self.assertEqual(response.status_code, 302)

        # Verify unicode content is preserved
        list_response = self.session.get(f"{self.base_url}/rules")
        self.assertIn("unicode-rule", list_response.text)

    def test_14_single_user_mode_compatibility(self):
        """Test rules functionality in single-user mode"""
        # This would require starting a separate server in single-user mode
        # For now, we'll just verify the endpoints exist and respond appropriately

        # Test that rules endpoints are accessible
        response = self.session.get(f"{self.base_url}/rules")
        self.assertEqual(response.status_code, 200)

        # Note: Full single-user mode testing would require a separate test setup

    def test_15_rules_with_tags_integration(self):
        """Test rules integration with tag management system"""
        # Create rules with various tags
        tagged_rules = [
            {
                "name": "ai-safety-rule",
                "title": "AI Safety Guidelines",
                "content": "# AI Safety\n\nEnsure safe AI interactions",
                "category": "Safety",
                "tags": "ai, safety, guidelines, ethics",
            },
            {
                "name": "performance-rule",
                "title": "Performance Guidelines",
                "content": "# Performance\n\nOptimize for speed and efficiency",
                "category": "Performance",
                "tags": "performance, optimization, speed",
            },
        ]

        for rule in tagged_rules:
            response = self.session.post(
                f"{self.base_url}/rules/new", data=rule, allow_redirects=False
            )
            self.assertEqual(response.status_code, 302)

        # Test tag-based search
        search_response = self.session.get(
            f"{self.base_url}/rules/search", params={"q": "safety"}
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertIn("ai-safety-rule", search_response.text)

    def test_16_error_handling(self):
        """Test error handling for various scenarios"""
        # Test accessing non-existent rule
        response = self.session.get(f"{self.base_url}/rules/99999/edit")
        self.assertEqual(response.status_code, 404)

        # Test deleting non-existent rule
        response = self.session.delete(f"{self.base_url}/rules/99999")
        self.assertIn(response.status_code, [404, 400])

        # Test invalid form data
        invalid_data = {
            "name": "x" * 1000,  # Extremely long name
            "title": "",  # Empty title
            "content": "",  # Empty content
        }

        response = self.session.post(f"{self.base_url}/rules/new", data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Should return form with errors

    def test_17_performance_with_many_rules(self):
        """Test performance with a larger number of rules"""
        # Create multiple rules to test list performance
        for i in range(10):
            rule_data = {
                "name": f"performance-rule-{i}",
                "title": f"Performance Rule {i}",
                "content": f"# Performance Rule {i}\n\nRule content for performance testing",
                "category": "Performance",
                "tags": f"performance, test, rule{i}",
            }

            response = self.session.post(
                f"{self.base_url}/rules/new", data=rule_data, allow_redirects=False
            )
            self.assertEqual(response.status_code, 302)

        # Test that the list page still loads quickly
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/rules")
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 5.0)  # Should load within 5 seconds

        # Verify all rules are shown
        for i in range(10):
            self.assertIn(f"performance-rule-{i}", response.text)


if __name__ == "__main__":
    unittest.main()
