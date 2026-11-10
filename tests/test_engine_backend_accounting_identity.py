"""Backend accounting compatibility paths must reach the same financial owner."""

import importlib
import inspect

import pytest
from quant_backtest_core.daily import trade_accounting as owned


@pytest.mark.parametrize(
    "module_name",
    [
        "quant_platform._portfolio.backends.trade_accounting",
        "quant_platform.backtest.legacy.backends.trade_accounting",
        "portfolio_backtester.backends.trade_accounting",
    ],
)
@pytest.mark.parametrize(
    "name",
    [
        "TradeCostConfig",
        "TradeAccounting",
        "_clean_weights",
        "drift_weights",
        "compute_trade_accounting",
        "compute_trade_accounting_frame",
    ],
)
def test_backend_accounting_uses_exact_owned_definitions(module_name, name):
    public = importlib.import_module(module_name)
    assert getattr(public, name) is getattr(owned, name)
    assert inspect.signature(getattr(public, name)) == inspect.signature(getattr(owned, name))


def test_legacy_trade_summary_remains_a_distinct_owned_api():
    from quant_backtest_core.daily import _period_helpers

    from quant_platform.backtest.legacy import trade_accounting as legacy

    assert legacy.compute_trade_summary is owned.compute_trade_summary
    assert legacy.drift_previous_weights is owned.drift_previous_weights
    assert legacy.compute_trade_summary is not owned.compute_trade_accounting
    assert legacy.drift_previous_weights is not owned.drift_weights
    assert legacy.compute_trade_summary is not _period_helpers._compute_trade_summary
