from __future__ import annotations

from typing import Any

import pytest
from research_contracts.promotion_evidence_checks import check_errors


@pytest.mark.parametrize(
    ("check_id", "fields"),
    [
        (
            "pit",
            {
                "pit_universe": True,
                "pit_fundamentals": True,
                "pit_industry_membership": True,
            },
        ),
        ("walk_forward", {"window_count": 2, "metric": "sharpe"}),
        (
            "benchmark_matrix",
            {
                "cells": [
                    {"universe": "a", "horizon": "1m"},
                    {"universe": "b", "horizon": "3m"},
                ]
            },
        ),
        (
            "cost",
            {
                "turnover": 0.2,
                "scenarios": [
                    {"cost_bps": 5, "metric": "return", "value": 0.1},
                    {"cost_bps": 10, "metric": "return", "value": 0.08},
                ],
            },
        ),
        (
            "final_oos",
            {
                "oos_start": "2025-01-01",
                "metric": "sharpe",
                "frozen_before_evaluation": True,
                "retuned_after_freeze": False,
            },
        ),
        ("cpcv", {"n_groups": 6, "test_groups": 2, "metric": "return"}),
        (
            "regime",
            {
                "metric": "return",
                "regimes": [
                    {"id": "bull", "value": 0.1},
                    {"id": "bear", "value": -0.1},
                    {"id": "sideways", "value": 0.0},
                ],
            },
        ),
        (
            "capacity",
            {
                "portfolio_values": [100_000, 1_000_000],
                "participation_rates": [0.01, 0.05],
                "primary_participation_rate": 0.01,
                "recommended_capacity": 100_000,
            },
        ),
    ],
)
def test_promotion_check_accepts_valid_synthetic_fields(
    check_id: str, fields: dict[str, Any]
) -> None:
    receipt = {"checks": {check_id: {"status": "passed", **fields}}}

    assert check_errors(receipt, check_id) == []


@pytest.mark.parametrize(
    ("check_id", "fields"),
    [
        ("pit", {"pit_universe": True}),
        ("walk_forward", {"window_count": 1, "metric": "sharpe"}),
        ("benchmark_matrix", {"cells": [{"universe": "a"}, {"universe": "b"}]}),
        ("cost", {"turnover": -1, "scenarios": []}),
        ("final_oos", {"oos_start": "2025-01-01", "metric": "sharpe"}),
        ("cpcv", {"n_groups": 4, "test_groups": 4, "metric": "return"}),
        ("regime", {"metric": "return", "regimes": [{"id": "bull", "value": 1}]}),
        ("capacity", {"portfolio_values": [], "participation_rates": []}),
    ],
)
def test_promotion_check_rejects_missing_or_invalid_fields(
    check_id: str, fields: dict[str, Any]
) -> None:
    receipt = {"checks": {check_id: {"status": "passed", **fields}}}

    assert check_errors(receipt, check_id) == ["check_fields_invalid"]


def test_promotion_check_requires_passed_status_and_ignores_unknown_checks() -> None:
    assert check_errors({"checks": {"pit": {"status": "failed"}}}, "pit") == ["check_not_passed"]
    assert check_errors({"checks": {"custom": {"status": "passed"}}}, "custom") == []
