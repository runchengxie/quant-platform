"""Public adapter must retain the owner's explicit valuation policy and real quotes."""

import numpy as np
import pandas as pd
from quant_backtest_core.daily.contracts import ExecutionCalendar
from quant_backtest_core.daily.execution_sim import ExecutionSimConfig

from quant_platform.backtest.engine_daily import build_daily_request, run_daily


def test_explicit_suspension_policy_survives_platform_request_and_owner_results():
    days = ["2025-01-03", "2025-01-06", "2025-01-07"]
    positions = pd.DataFrame(
        {
            "rebalance_date": ["2025-01-02"],
            "entry_date": [days[0]],
            "symbol": ["A"],
            "weight": [1.0],
            "side": ["long"],
        }
    )
    prices = pd.DataFrame(
        {
            "trade_date": days,
            "symbol": ["A"] * 3,
            "close": [10.0, np.nan, 12.0],
            "amount": [100000.0] * 3,
            "can_trade": [True, False, True],
            "suspension_witness": [False, True, False],
        }
    )
    clock = {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": "2025-01-02T15:00:00+08:00",
        "signal_at": "2025-01-02T15:00:01+08:00",
        "decision_at": "2025-01-02T15:00:02+08:00",
        "earliest_order_at": "2025-01-03T09:30:00+08:00",
        "execution_window_start_at": "2025-01-03T09:30:00+08:00",
        "execution_window_end_at": "2025-01-03T15:00:00+08:00",
        "valuation_at": "2025-01-07T15:00:00+08:00",
        "timing_policy_id": "synthetic",
        "trading_calendar_ref": "synthetic",
    }
    config = ExecutionSimConfig(
        enabled=True,
        portfolio_value=1000,
        participation_rate=1,
        liquidity_cols=("amount",),
        valuation_policy="suspended_last_quote",
        valuation_suspension_col="suspension_witness",
        valuation_max_stale_sessions=1,
    )
    request = build_daily_request(
        positions=positions,
        pricing=prices,
        calendar=ExecutionCalendar.from_dates("Asia/Shanghai", days),
        decision_clocks={"2025-01-02": clock},
        config=config,
        price_basis="adjusted",
        tradable_col="can_trade",
    )
    assert request.config.valuation_policy == config.valuation_policy
    assert request.config.valuation_max_stale_sessions == config.valuation_max_stale_sessions
    assert request.config.valuation_suspension_col == "suspension_witness"
    result = run_daily(request)
    assert result.valuation_marks.endpoint_complete.tolist() == [True, True, True]
    assert result.valuation_marks.current_marks.tolist() == [1, 0, 1]
    assert result.valuation_marks.policy_valued_symbols.iloc[1] == ("A",)
    assert result.daily.portfolio_value.iloc[-1] == 1200.0
    assert not result.fills.trade_date.eq("20250106").any()
    assert result.summary["execution_summary"]["valuation_policy"] == "suspended_last_quote"
    assert result.summary["execution_summary"]["policy_valued_endpoints"] == 1
