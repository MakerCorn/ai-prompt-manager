#!/usr/bin/env python3
"""
Unit tests for model-pricing selection in TokenCalculator._calculate_cost.

The lookup matched pricing keys by substring in insertion order, so
"gpt-4-turbo" matched the earlier "gpt-4" key and was billed at gpt-4's higher
rate. The most specific (longest) matching key must win.
"""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from token_calculator import TokenCalculator  # noqa: E402


class TestPricingSelection(unittest.TestCase):
    def setUp(self):
        self.calc = TokenCalculator()

    def test_gpt_4_turbo_uses_turbo_pricing(self):
        """gpt-4-turbo must use its own pricing, not gpt-4's."""
        turbo = self.calc.MODEL_PRICING["gpt-4-turbo"]
        expected = (1000 / 1000) * turbo["input"] + (1000 / 1000) * turbo["output"]
        cost = self.calc._calculate_cost(1000, 1000, "gpt-4-turbo")
        self.assertAlmostEqual(cost, expected)

    def test_gpt_4_still_uses_gpt_4_pricing(self):
        """Plain gpt-4 must still resolve to gpt-4 pricing."""
        base = self.calc.MODEL_PRICING["gpt-4"]
        expected = (1000 / 1000) * base["input"] + (1000 / 1000) * base["output"]
        cost = self.calc._calculate_cost(1000, 1000, "gpt-4")
        self.assertAlmostEqual(cost, expected)

    def test_unknown_model_returns_none(self):
        self.assertIsNone(self.calc._calculate_cost(1000, 1000, "no-such-model"))


if __name__ == "__main__":
    unittest.main()
