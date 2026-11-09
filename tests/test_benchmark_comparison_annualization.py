"""Analytical regressions for daily benchmark-relative risk metrics."""

import math
import unittest

import pandas as pd

from quant_platform.analytics.benchmark_comparison import compare_portfolio_returns


class TestBenchmarkComparisonAnnualization(unittest.TestCase):
    def test_information_ratio_annualizes_signed_active_returns(self) -> None:
        # Each fixture has sample daily volatility 0.02 (ddof=1).
        # Mean daily active returns are +0.01, -0.01, and 0.0.
        for active_returns, expected_ir in [
            ([-0.01, 0.01, 0.03], math.sqrt(63)),
            ([-0.03, -0.01, 0.01], -math.sqrt(63)),
            ([-0.02, 0.00, 0.02], 0.0),
        ]:
            with self.subTest(active_returns=active_returns):
                portfolio = pd.Series(active_returns)
                benchmark = pd.Series([0.0, 0.0, 0.0])
                weights = pd.Series({"A": 1.0})

                result = compare_portfolio_returns(portfolio, benchmark, weights, weights)

                self.assertAlmostEqual(result["tracking_error"], 0.02 * math.sqrt(252))
                self.assertAlmostEqual(result["information_ratio"], expected_ir)

    def test_information_ratio_uses_active_returns_not_absolute_returns(self) -> None:
        # Subtracting a varying benchmark gives the same [-0.01, 0.01, 0.03] fixture.
        portfolio = pd.Series([0.02, 0.00, 0.05])
        benchmark = pd.Series([0.03, -0.01, 0.02])
        weights = pd.Series({"A": 1.0})

        result = compare_portfolio_returns(portfolio, benchmark, weights, weights)

        self.assertAlmostEqual(result["tracking_error"], 0.02 * math.sqrt(252))
        self.assertAlmostEqual(result["information_ratio"], math.sqrt(63))

    def test_information_ratio_stays_undefined_without_sample_active_volatility(self) -> None:
        for active_returns in ([0.0, 0.0], [0.01, 0.01], [-0.01, -0.01], [0.01]):
            with self.subTest(active_returns=active_returns):
                portfolio = pd.Series(active_returns)
                benchmark = pd.Series(0.0, index=portfolio.index)
                weights = pd.Series({"A": 1.0})

                result = compare_portfolio_returns(portfolio, benchmark, weights, weights)

                self.assertEqual(result["tracking_error"], 0.0)
                self.assertTrue(math.isnan(result["information_ratio"]))
