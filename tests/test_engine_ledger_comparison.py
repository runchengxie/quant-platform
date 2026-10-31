"""Financial comparison evidence, including mismatches that final returns can hide."""

from __future__ import annotations

import copy
import os
from decimal import Decimal
from pathlib import Path

import pytest

from scripts.benchmarks.compare_engine_ledgers import (
    compare,
    normalize_engine,
    normalize_python,
    python_ledger,
    run_comparison,
    session_request,
)


def test_python_roundtrip_matches_hand_calculated_cash_ledger():
    evidence = normalize_python(python_ledger())
    assert evidence["daily"] == [
        {
            "date": "2025-01-02",
            "cash": Decimal("8999"),
            "quantity": Decimal("100"),
            "positions_value": Decimal("1000"),
            "nav": Decimal("9999"),
            "commission": Decimal("1"),
        },
        {
            "date": "2025-01-03",
            "cash": Decimal("10197.8"),
            "quantity": Decimal("0"),
            "positions_value": Decimal("0"),
            "nav": Decimal("10197.8"),
            "commission": Decimal("1.2"),
        },
    ]
    assert [row["quantity"] for row in evidence["fills"]] == [100, 100]
    assert [row["status"] for row in evidence["orders"]] == ["filled", "filled"]


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("daily", "cash"),
        ("daily", "positions_value"),
        ("daily", "quantity"),
        ("daily", "commission"),
        ("daily", "nav"),
        ("orders", "filled_quantity"),
        ("fills", "price"),
        ("fills", "quantity"),
        ("fills", "commission"),
    ],
)
def test_comparison_detects_interior_mismatch_with_unchanged_final_nav(section, field):
    expected = normalize_python(python_ledger())
    changed = copy.deepcopy(expected)
    changed[section][0][field] += Decimal("0.01")
    assert changed["daily"][-1]["nav"] == expected["daily"][-1]["nav"]
    assert compare(expected, changed) == [
        {
            "field": f".{section}[0].{field}",
            "python": expected[section][0][field],
            "engine": changed[section][0][field],
        }
    ]


def test_comparison_detects_missing_order_and_wrong_status():
    expected = normalize_python(python_ledger())
    changed = copy.deepcopy(expected)
    changed["orders"][0]["status"] = "rejected"
    changed["fills"].pop()
    fields = {row["field"] for row in compare(expected, changed)}
    assert ".orders[0].status" in fields
    assert ".fills.length" in fields


def test_normalization_detects_changed_raw_python_fill_notional():
    actual = python_ledger()
    expected = normalize_python(actual)
    changed = copy.deepcopy(actual)
    changed.fills.loc[0, "filled_notional"] = 990.0
    evidence = normalize_python(changed)
    fields = {row["field"] for row in compare(expected, evidence)}
    assert ".fills[0].quantity" in fields
    assert ".daily[0].quantity" in fields
    assert evidence["fills"][0]["quantity"] == Decimal("99")
    assert evidence["daily"][-1]["nav"] == expected["daily"][-1]["nav"]


def _binary() -> tuple[Path, str]:
    binary, digest = os.getenv("SESSION_ENGINE_BINARY"), os.getenv("SESSION_ENGINE_SHA256")
    if not binary or not digest:
        pytest.skip("real engine requires SESSION_ENGINE_BINARY and SESSION_ENGINE_SHA256")
    return Path(binary), digest


def test_real_backends_match_orders_fills_and_daily_balances():
    binary, digest = _binary()
    report = run_comparison(binary, digest)
    assert report["matched"], report["mismatches"]
    assert len(report["engine"]["orders"]) == 2
    assert len(report["engine"]["fills"]) == 2
    assert len(report["engine"]["daily"]) == 2
    assert report["engine"]["daily"][-1]["nav"] == Decimal("10197.8")


def test_real_different_valuation_quote_exposes_daily_divergence():
    binary, digest = _binary()
    from quant_backtest_engine import EngineClient

    request = session_request(first_mark="11")
    result = EngineClient(binary, digest).run_sessions(request)
    mismatches = compare(normalize_python(python_ledger()), normalize_engine(result, request))
    assert {row["field"] for row in mismatches} == {
        ".daily[0].positions_value",
        ".daily[0].nav",
    }
    assert {row["engine"] - row["python"] for row in mismatches} == {Decimal("100")}
