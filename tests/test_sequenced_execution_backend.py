"""Synthetic multi-decision clock and market-event contract."""

from __future__ import annotations

import pandas as pd
import pytest

from portfolio_backtester.backends import (
    SequencedExecutionBackend,
    SequencedExecutionRequest,
    write_execution_aware_result_bundle,
)
from portfolio_backtester.execution_sim import ExecutionSimConfig


def _clock(day: str, entry: str) -> dict[str, str]:
    date = pd.Timestamp(day).strftime("%Y-%m-%d")
    next_date = pd.Timestamp(entry).strftime("%Y-%m-%d")
    return {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": f"{date}T18:00:00+08:00",
        "signal_at": f"{date}T18:01:00+08:00",
        "decision_at": f"{date}T18:02:00+08:00",
        "earliest_order_at": f"{next_date}T09:30:00+08:00",
        "execution_window_start_at": f"{next_date}T09:30:00+08:00",
        "execution_window_end_at": f"{next_date}T15:00:00+08:00",
        "valuation_at": "2020-01-08T16:00:00+08:00",
        "timing_policy_id": "test.after_close_next_session",
        "trading_calendar_ref": "synthetic-calendar",
    }


def _request() -> SequencedExecutionRequest:
    positions = pd.DataFrame(
        {
            "rebalance_date": ["2020-01-02", "2020-01-06"],
            "entry_date": ["2020-01-03", "2020-01-07"],
            "symbol": ["A", "B"],
            "weight": [1.0, 1.0],
        }
    )
    pricing = pd.DataFrame(
        [
            {
                "trade_date": day,
                "symbol": symbol,
                "close": 10.0,
                "amount": 1_000_000.0,
                "tradable": True,
                "limit_up": symbol == "B" and day == "2020-01-07",
                "limit_down": False,
            }
            for day in ("2020-01-03", "2020-01-06", "2020-01-07", "2020-01-08")
            for symbol in ("A", "B")
        ]
    )
    return SequencedExecutionRequest(
        positions=positions,
        pricing=pricing,
        decision_clocks={
            "2020-01-02": _clock("2020-01-02", "2020-01-03"),
            "2020-01-06": _clock("2020-01-06", "2020-01-07"),
        },
        config=ExecutionSimConfig(
            enabled=True,
            portfolio_value=10_000.0,
            participation_rate=1.0,
            liquidity_cols=("amount",),
            buy_max_days=2,
            sell_max_days=2,
            enforce_price_limits=True,
            limit_up_col="limit_up",
            limit_down_col="limit_down",
        ),
        tradable_col="tradable",
        limit_up_col="limit_up",
        limit_down_col="limit_down",
    )


def test_sequence_uses_one_clock_per_decision_and_shared_market_rules() -> None:
    result = SequencedExecutionBackend().run(_request())
    assert result.metadata["decision_count"] == 2
    assert result.capabilities.daily_ledger
    assert "price_limits" in result.capabilities.market_rules
    assert result.daily_ledger.shape[0] == 4
    assert result.unified_ledger is not None
    b_fills = result.fills.loc[result.fills["symbol"].eq("B")]
    assert "20200107" not in set(b_fills["trade_date"].astype(str))
    assert "20200108" in set(b_fills["trade_date"].astype(str))


def test_sequence_rejects_missing_clock_and_early_entry() -> None:
    request = _request()
    request.decision_clocks.pop("2020-01-06")
    with pytest.raises(ValueError, match="decision clocks must match"):
        SequencedExecutionBackend().run(request)

    request = _request()
    request.positions.loc[0, "entry_date"] = "2020-01-02"
    with pytest.raises(ValueError, match="outside its execution clock"):
        SequencedExecutionBackend().run(request)


def test_sequence_rejects_future_pricing_and_overweight_target() -> None:
    request = _request()
    request.pricing.loc[0, "trade_date"] = "2020-01-09"
    with pytest.raises(ValueError, match="pricing extends past"):
        SequencedExecutionBackend().run(request)

    request = _request()
    request.positions.loc[0, "weight"] = 1.2
    with pytest.raises(ValueError, match="exceed full investment"):
        SequencedExecutionBackend().run(request)


def test_single_clock_bundle_cannot_mislabel_a_sequence(tmp_path) -> None:
    result = SequencedExecutionBackend().run(_request())
    with pytest.raises(ValueError, match="per-decision clock bundle schema"):
        write_execution_aware_result_bundle(
            tmp_path,
            result=result,
            run_id="synthetic-sequence",
            research_clock=_clock("2020-01-02", "2020-01-03"),
            producer={"backend": result.backend_name},
            configuration_sha256="0" * 64,
            input_refs=[{"artifact_id": "synthetic", "sha256": "1" * 64}],
        )
