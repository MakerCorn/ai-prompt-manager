#!/usr/bin/env python3
"""
Unit tests for the launcher's configuration -> environment propagation.

Regression coverage for the defect where ``--multi-tenant`` was silently
ignored when the environment already contained ``MULTITENANT_MODE=false``,
because ``main()`` only wrote the variable in the single-user branch. The
resolved launcher configuration must be the single source of truth.
"""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import run  # noqa: E402


class TestModeEnvironmentPropagation(unittest.TestCase):
    def setUp(self):
        self._saved = {
            key: os.environ.get(key) for key in ("MULTITENANT_MODE", "LOCAL_DEV_MODE")
        }

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_multitenant_config_overrides_stale_false_env(self):
        """A multi-tenant config must win over a stale MULTITENANT_MODE=false."""
        os.environ["MULTITENANT_MODE"] = "false"
        config = {"multitenant_mode": True, "local_dev_mode": False}

        run.apply_configuration_to_environment(config)

        self.assertEqual(os.environ["MULTITENANT_MODE"], "true")

    def test_single_user_config_sets_false(self):
        """A single-user config must set MULTITENANT_MODE=false."""
        os.environ["MULTITENANT_MODE"] = "true"
        config = {"multitenant_mode": False, "local_dev_mode": False}

        run.apply_configuration_to_environment(config)

        self.assertEqual(os.environ["MULTITENANT_MODE"], "false")


if __name__ == "__main__":
    unittest.main()
