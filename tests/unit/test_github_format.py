"""
Unit tests for GitHub format support in AI Prompt Manager.

Tests the GitHub YAML format import/export functionality.
"""

import os

# Add project root to path
import sys
import tempfile
import unittest

import yaml

# test imports removed: unused MagicMock, patch


sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.prompts.models.prompt import Prompt
from src.utils.github_format import GitHubFormatHandler


class TestGitHubFormatHandler(unittest.TestCase):
    """Test GitHub format handler functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = GitHubFormatHandler()
        self.sample_github_data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Create an Azure Logic App for PDF processing.",
                },
            ],
            "model": "openai/gpt-4o",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        self.sample_yaml = """
messages:
  - role: system
    content: 'You are a helpful assistant.'
  - role: user
    content: >-
      Create an azure logic app that will provide a UI to allow a user to upload
      a PDF document with medical information.
model: openai/gpt-4o
temperature: 0.7
max_tokens: 1000
"""

    def test_validate_github_format_valid(self):
        """Test validation of valid GitHub format."""
        is_valid, error = self.handler.validate_github_format(self.sample_github_data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_github_format_missing_messages(self):
        """Test validation fails when messages field is missing."""
        invalid_data = {"model": "openai/gpt-4o"}
        is_valid, error = self.handler.validate_github_format(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("Missing required 'messages' field", error)

    def test_validate_github_format_empty_messages(self):
        """Test validation fails when messages list is empty."""
        invalid_data = {"messages": [], "model": "openai/gpt-4o"}
        is_valid, error = self.handler.validate_github_format(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("'messages' cannot be empty", error)

    def test_validate_github_format_invalid_role(self):
        """Test validation fails with invalid message role."""
        invalid_data = {
            "messages": [{"role": "invalid", "content": "test"}],
            "model": "openai/gpt-4o",
        }
        is_valid, error = self.handler.validate_github_format(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("invalid role", error)

    def test_validate_github_format_missing_content(self):
        """Test validation fails when message content is missing."""
        invalid_data = {"messages": [{"role": "user"}], "model": "openai/gpt-4o"}
        is_valid, error = self.handler.validate_github_format(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("missing required 'content' field", error)

    def test_import_from_yaml_string(self):
        """Test importing from YAML string."""
        prompt = Prompt.from_github_yaml(
            self.sample_yaml, tenant_id="test_tenant", user_id="test_user"
        )

        self.assertEqual(prompt.tenant_id, "test_tenant")
        self.assertEqual(prompt.user_id, "test_user")
        self.assertEqual(prompt.category, "GitHub Import")
        self.assertIn("github,import", prompt.tags)

        # Check metadata
        self.assertEqual(prompt.get_metadata("model"), "openai/gpt-4o")
        self.assertEqual(prompt.get_metadata("temperature"), 0.7)
        self.assertEqual(prompt.get_metadata("max_tokens"), 1000)
        self.assertEqual(prompt.get_metadata("format"), "messages")

    def test_export_to_yaml_string(self):
        """Test exporting to YAML string."""
        # Create a prompt with GitHub format metadata
        prompt = Prompt(
            tenant_id="test_tenant",
            user_id="test_user",
            name="Test Prompt",
            title="Test Prompt",
            content="USER: Create an Azure Logic App",
            category="Test",
            metadata={
                "format": "messages",
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Create an Azure Logic App"},
                ],
                "model": "openai/gpt-4o",
            },
        )

        yaml_output = prompt.to_github_yaml()

        # Parse the YAML to verify structure
        parsed = yaml.safe_load(yaml_output)
        self.assertIn("messages", parsed)
        self.assertIn("model", parsed)
        self.assertEqual(len(parsed["messages"]), 2)
        self.assertEqual(parsed["model"], "openai/gpt-4o")

    def test_content_parsing_with_role_markers(self):
        """Test parsing content with explicit role markers."""
        content = """SYSTEM: You are a helpful assistant.

USER: Create an Azure Logic App for PDF processing.

ASSISTANT: I'll help you create an Azure Logic App."""

        prompt = Prompt(
            tenant_id="test_tenant",
            user_id="test_user",
            name="Test",
            title="Test",
            content=content,
        )

        messages = prompt._parse_content_to_messages()
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[2]["role"], "assistant")

    def test_content_parsing_without_role_markers(self):
        """Test parsing plain content without role markers."""
        content = "Create an Azure Logic App for PDF processing."

        prompt = Prompt(
            tenant_id="test_tenant",
            user_id="test_user",
            name="Test",
            title="Test",
            content=content,
        )

        messages = prompt._parse_content_to_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], content)

    def test_file_import_export(self):
        """Test importing and exporting files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "test_prompt.yml")
            with open(test_file, "w") as f:
                f.write(self.sample_yaml)

            # Test import
            prompt = self.handler.import_from_file(
                test_file, tenant_id="test_tenant", user_id="test_user"
            )

            self.assertEqual(prompt.name, "test_prompt")
            self.assertEqual(prompt.category, "GitHub Import")

            # Test export
            output_file = os.path.join(temp_dir, "output.yml")
            self.handler.export_to_file(prompt, output_file)

            # Verify exported file exists and is valid
            self.assertTrue(os.path.exists(output_file))

            with open(output_file, "r") as f:
                exported_data = yaml.safe_load(f.read())

            self.assertIn("messages", exported_data)
            self.assertIn("model", exported_data)

    def test_is_github_format_detection(self):
        """Test GitHub format file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create GitHub format file
            github_file = os.path.join(temp_dir, "github.yml")
            with open(github_file, "w") as f:
                f.write(self.sample_yaml)

            # Create non-GitHub YAML file
            non_github_file = os.path.join(temp_dir, "other.yml")
            with open(non_github_file, "w") as f:
                f.write("name: test\ncontent: hello")

            # Create non-YAML file
            text_file = os.path.join(temp_dir, "text.txt")
            with open(text_file, "w") as f:
                f.write("Hello world")

            # Test detection
            self.assertTrue(self.handler.is_github_format(github_file))
            self.assertFalse(self.handler.is_github_format(non_github_file))
            self.assertFalse(self.handler.is_github_format(text_file))

    def test_directory_import(self):
        """Test importing all GitHub files from a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple GitHub format files
            for i in range(3):
                file_path = os.path.join(temp_dir, f"prompt_{i}.yml")
                sample_data = self.sample_github_data.copy()
                if isinstance(sample_data, dict) and "messages" in sample_data:
                    messages = sample_data["messages"]
                    if isinstance(messages, list) and len(messages) > 1:
                        if isinstance(messages[1], dict):
                            messages[1]["content"] = f"Test prompt {i}"

                with open(file_path, "w") as f:
                    yaml.dump(sample_data, f)

            # Create a non-GitHub file that should be ignored
            non_github_file = os.path.join(temp_dir, "other.yml")
            with open(non_github_file, "w") as f:
                f.write("name: test\ncontent: hello")

            # Import directory
            prompts = self.handler.import_from_directory(
                temp_dir, tenant_id="test_tenant", user_id="test_user"
            )

            # Should have imported 3 GitHub format files
            self.assertEqual(len(prompts), 3)

            # Verify all prompts have correct tenant/user
            for prompt in prompts:
                self.assertEqual(prompt.tenant_id, "test_tenant")
                self.assertEqual(prompt.user_id, "test_user")

    def test_directory_export(self):
        """Test exporting prompts to directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test prompts
            prompts = []
            for i in range(2):
                prompt = Prompt(
                    tenant_id="test_tenant",
                    user_id="test_user",
                    name=f"Test Prompt {i}",
                    title=f"Test Prompt {i}",
                    content=f"Test content {i}",
                    metadata={
                        "format": "messages",
                        "messages": [{"role": "user", "content": f"Test content {i}"}],
                        "model": "openai/gpt-4o",
                    },
                )
                prompts.append(prompt)

            # Export to directory
            created_files = self.handler.export_to_directory(
                prompts, temp_dir, use_prompt_names=True
            )

            # Verify files were created
            self.assertEqual(len(created_files), 2)

            for file_path in created_files:
                self.assertTrue(os.path.exists(file_path))
                self.assertTrue(file_path.endswith(".yml"))

                # Verify file content is valid YAML
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f.read())
                self.assertIn("messages", data)
                self.assertIn("model", data)

    def test_get_format_info(self):
        """Test getting format information."""
        info = self.handler.get_format_info()

        self.assertIn("name", info)
        self.assertIn("description", info)
        self.assertIn("extensions", info)
        self.assertIn("required_fields", info)
        self.assertIn("optional_fields", info)
        self.assertIn("message_roles", info)
        self.assertIn("example", info)

        # Verify required fields
        self.assertIn("messages", info["required_fields"])

        # Verify supported roles
        expected_roles = ["system", "user", "assistant"]
        for role in expected_roles:
            self.assertIn(role, info["message_roles"])

    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["

        with self.assertRaises(ValueError) as context:
            Prompt.from_github_yaml(
                invalid_yaml, tenant_id="test_tenant", user_id="test_user"
            )

        self.assertIn("Invalid YAML format", str(context.exception))

    def test_name_generation_from_content(self):
        """Test automatic name generation from user message content."""
        prompt = Prompt.from_github_format(
            self.sample_github_data, tenant_id="test_tenant", user_id="test_user"
        )

        # Should use first few words of user message
        self.assertIn("Create", prompt.name)
        self.assertIn("Azure", prompt.name)


if __name__ == "__main__":
    unittest.main()
