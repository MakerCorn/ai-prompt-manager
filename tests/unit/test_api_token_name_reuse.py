#!/usr/bin/env python3
"""
Regression test: recreating a token with the name of a revoked token must
fail cleanly (the UNIQUE(user_id, name) constraint still reserves the name),
rather than raising a cryptic IntegrityError on INSERT.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ.setdefault("DB_TYPE", "sqlite")

from api_token_manager import APITokenManager  # noqa: E402


class TestTokenNameReuse(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name
        self.tm = APITokenManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_recreate_revoked_name_fails_cleanly(self):
        ok, msg, _ = self.tm.create_api_token("u1", "t1", "mytoken")
        self.assertTrue(ok, msg)

        # Find and revoke the token.
        tokens = self.tm.get_user_tokens("u1")
        self.tm.revoke_token("u1", tokens[0].id)

        # Recreating the same name must return a clean failure, not raise.
        ok2, msg2, _ = self.tm.create_api_token("u1", "t1", "mytoken")
        self.assertFalse(ok2)
        self.assertIn("already exists", msg2.lower())


if __name__ == "__main__":
    unittest.main()
