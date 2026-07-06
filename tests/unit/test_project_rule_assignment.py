#!/usr/bin/env python3
"""
Unit tests for assign_rule_to_project / unassign_rule_from_project.

These methods referenced a non-existent ``tenant_id`` column (and assign also
inserted into non-existent ``user_id``/``created_at`` columns), so every call
failed with "no such column" on SQLite and errored on PostgreSQL too. The
project_rules schema is (id, project_id, rule_id, rule_set_name, added_at).
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


class TestProjectRuleAssignment(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.db_path = tmp.name
        self.dm = PromptDataManager(db_path=self.db_path, tenant_id="t1", user_id="u1")
        # A project (creator has edit permission) and a rule.
        self.dm.add_project(
            name="proj", title="Proj", description="d", project_type="general"
        )
        self.project_id = next(
            p["id"] for p in self.dm.get_projects() if p["name"] == "proj"
        )
        self.dm.add_rule("r1", "Rule 1", "content", category="General")
        self.rule_id = next(
            r["id"] for r in self.dm.get_all_rules() if r["name"] == "r1"
        )

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_assign_then_unassign(self):
        assign = self.dm.assign_rule_to_project(self.project_id, self.rule_id)
        self.assertTrue(assign.get("success"), assign)

        rule_ids = {r["id"] for r in self.dm.get_project_rules(self.project_id)}
        self.assertIn(self.rule_id, rule_ids)

        unassign = self.dm.unassign_rule_from_project(self.project_id, self.rule_id)
        self.assertTrue(unassign.get("success"), unassign)
        rule_ids = {r["id"] for r in self.dm.get_project_rules(self.project_id)}
        self.assertNotIn(self.rule_id, rule_ids)

    def test_duplicate_assignment_rejected(self):
        first = self.dm.assign_rule_to_project(self.project_id, self.rule_id)
        self.assertTrue(first.get("success"), first)
        second = self.dm.assign_rule_to_project(self.project_id, self.rule_id)
        self.assertFalse(second.get("success"))

    def test_unassign_missing_returns_failure(self):
        result = self.dm.unassign_rule_from_project(self.project_id, self.rule_id)
        self.assertFalse(result.get("success"))


if __name__ == "__main__":
    unittest.main()
