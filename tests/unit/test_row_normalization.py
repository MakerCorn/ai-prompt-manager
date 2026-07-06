#!/usr/bin/env python3
"""
Unit tests for PromptDataManager._row_to_dict cross-backend row normalization.

sqlite3 returns positional tuples; psycopg2 RealDictCursor returns dict-like
rows (a dict subclass). The helper must produce an identical plain dict for
both so downstream code can index by column name on either backend.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ.setdefault("DB_TYPE", "sqlite")

from prompt_data_manager import PromptDataManager  # noqa: E402


class TestRowToDict(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name
        self.dm = PromptDataManager(db_path=self.db_path, tenant_id="t", user_id="u")

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_sqlite_tuple_row_becomes_dict(self):
        """A positional tuple row is keyed by column name via description."""
        conn = self.dm.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 AS id, 'alpha' AS name")
        row = cur.fetchone()
        self.assertIsInstance(row, tuple)  # sqlite default row shape
        result = PromptDataManager._row_to_dict(cur, row)
        conn.close()
        self.assertEqual(result, {"id": 1, "name": "alpha"})

    def test_dict_row_passthrough(self):
        """A RealDictRow-like dict row is returned as a plain dict."""
        # RealDictRow is a dict subclass; a plain dict is a faithful stand-in.
        result = PromptDataManager._row_to_dict(None, {"id": 7, "name": "beta"})
        self.assertEqual(result, {"id": 7, "name": "beta"})
        self.assertIsInstance(result, dict)

    def test_none_row(self):
        self.assertIsNone(PromptDataManager._row_to_dict(None, None))

    def test_rows_to_dicts_batch(self):
        conn = self.dm.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 AS a, 2 AS b")
        rows = cur.fetchall()
        result = PromptDataManager._rows_to_dicts(cur, rows)
        conn.close()
        self.assertEqual(result, [{"a": 1, "b": 2}])


if __name__ == "__main__":
    unittest.main()
