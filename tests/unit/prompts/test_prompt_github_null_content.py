#!/usr/bin/env python3
"""
Regression test: Prompt.from_github_format must not crash when a message has
null (None) content. A JSON null becomes Python None, and dict.get(key, "")
does not substitute the default for a present-but-None value, so the previous
content.strip() raised AttributeError.
"""

import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from src.prompts.models.prompt import Prompt  # noqa: E402


class TestGithubNullContent(unittest.TestCase):
    def test_null_content_message_does_not_crash(self):
        github_data = {
            "messages": [
                {"role": "system", "content": None},
                {"role": "user", "content": "Summarize this"},
            ],
            "model": "openai/gpt-4o",
        }
        prompt = Prompt.from_github_format(github_data, tenant_id="t", user_id="u")
        # The valid user message survives; the null one is skipped.
        self.assertIn("Summarize this", prompt.content)
        self.assertNotIn("SYSTEM:", prompt.content)

    def test_null_role_does_not_crash(self):
        github_data = {"messages": [{"role": None, "content": "hi there"}]}
        prompt = Prompt.from_github_format(github_data, tenant_id="t", user_id="u")
        self.assertIn("hi there", prompt.content)


if __name__ == "__main__":
    unittest.main()
