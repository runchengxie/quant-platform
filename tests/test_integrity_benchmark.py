import os
from pathlib import Path

import pytest

from scripts.benchmarks.execution_integrity import pooled_capacity_probe, run_prefix_comparison


def test_pooled_account_consumes_one_bar_budget_and_retains_one_impact_state():
    row = pooled_capacity_probe()
    assert row["pooled_filled_shares"] == 200
    assert row["isolated_filled_shares_sum"] == 400
    assert row["same_total_initial_cash"]
    assert row["pooled_impact_permanent"] == pytest.approx(0.2)


@pytest.mark.parametrize("case", ["roundtrip", "valuation_difference", "ioc_continuation"])
def test_real_engine_comparison_retains_declared_semantic_differences(case):
    binary, digest = os.getenv("SESSION_ENGINE_BINARY"), os.getenv("SESSION_ENGINE_SHA256")
    if not binary or not digest:
        pytest.skip("explicit pinned engine required")
    row = run_prefix_comparison(Path(binary), digest, case)
    assert row["expectation_met"], row
    if case == "ioc_continuation":
        assert row["prefix_differences"]
    elif case == "valuation_difference":
        assert not row["prefix_differences"]
        assert row["daily_differences"]


def test_expected_valuation_difference_does_not_hide_additional_cash_error(monkeypatch):
    from quant_backtest_engine import EngineClient

    binary, digest = os.getenv("SESSION_ENGINE_BINARY"), os.getenv("SESSION_ENGINE_SHA256")
    if not binary or not digest:
        pytest.skip("explicit pinned engine required")
    original = EngineClient.run_sessions

    def extra_cash_error(client, request):
        result = original(client, request)
        result["daily_ledger"][0]["cash"] = "9000"
        return result

    monkeypatch.setattr(EngineClient, "run_sessions", extra_cash_error)
    report = run_prefix_comparison(Path(binary), digest, "valuation_difference")
    assert not report["expectation_met"]
    assert any(r["field"] == "[0].cash" for r in report["daily_differences"])
