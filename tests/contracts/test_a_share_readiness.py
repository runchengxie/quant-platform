from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_contracts.a_share_readiness import (
    READINESS_LEVELS,
    build_readiness_report,
    main,
)


def _profile() -> dict[str, Any]:
    return {
        "configured_start_date": "2020-01-01",
        "universe": {"mode": "by_date", "point_in_time": True},
        "fundamentals": {
            "statement_features_enabled": True,
            "point_in_time": True,
            "report_period": True,
            "disclosure_date": True,
            "availability_delay": True,
            "field_mapping": True,
        },
        "industry": {
            "historical_backtest_enabled": True,
            "historical_membership": True,
            "effective_date": True,
        },
        "trading_rules": dict.fromkeys(
            (
                "t_plus_one",
                "st_state",
                "suspension",
                "listing_age",
                "board_lot",
                "board_specific",
                "limit_up_buy",
                "limit_down_sell",
            ),
            True,
        ),
    }


def _report(tmp_path: Path, profile: dict[str, Any]) -> dict[str, Any]:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps({"research_profile": profile}), encoding="utf-8")
    return build_readiness_report(tmp_path / "artifacts", evidence_manifest=evidence_path)


def test_a_share_readiness_reports_profile_readiness_from_synthetic_evidence(
    tmp_path: Path,
) -> None:
    report = _report(tmp_path, _profile())
    data_checks = report["levels"]["complete_pit_research_data"]["checks"]
    strategy_checks = report["levels"]["production_strategy_evidence"]["checks"]
    profile_checks = {
        check["id"]: check
        for check in (*data_checks, *strategy_checks)
        if check["id"].startswith("profile:")
    }

    assert report["schema_version"] == 1
    assert report["market"] == "a_share"
    assert set(report["summary"]["failed_levels"]) >= set(READINESS_LEVELS)
    assert all(
        profile_checks[f"profile:{name}"]["passed"]
        for name in (
            "pit_universe",
            "pit_fundamentals",
            "historical_industry",
            "side_aware_trading",
        )
    )


def test_a_share_readiness_identifies_missing_pit_and_trading_rules(tmp_path: Path) -> None:
    profile = _profile()
    profile["fundamentals"]["disclosure_date"] = False
    profile["trading_rules"]["t_plus_one"] = False
    report = _report(tmp_path, profile)
    data_checks = report["levels"]["complete_pit_research_data"]["checks"]
    strategy_checks = report["levels"]["production_strategy_evidence"]["checks"]
    profile_checks = {
        check["id"]: check
        for check in (*data_checks, *strategy_checks)
        if check["id"].startswith("profile:")
    }

    assert profile_checks["profile:pit_fundamentals"]["passed"] is False
    assert (
        "disclosure_date" in profile_checks["profile:pit_fundamentals"]["details"]["missing_rules"]
    )
    assert profile_checks["profile:side_aware_trading"]["passed"] is False
    assert "t_plus_one" in profile_checks["profile:side_aware_trading"]["details"]["missing_rules"]


def test_a_share_readiness_cli_writes_report_and_enforces_requested_level(
    tmp_path: Path, capsys: Any
) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps({"research_profile": _profile()}), encoding="utf-8")
    output_path = tmp_path / "report.json"
    args = [
        "--artifacts-root",
        str(tmp_path / "artifacts"),
        "--evidence-manifest",
        str(evidence_path),
        "--out",
        str(output_path),
        "--pretty",
    ]

    assert main(args) == 0
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["market"] == "a_share"
    assert json.loads(capsys.readouterr().out)["schema_version"] == 1
    assert main([*args, "--require", "baseline_reproducible"]) == 2


def test_a_share_readiness_reads_current_contract_and_registry(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    current_path = root / "metadata" / "current_assets" / "a_share_current.json"
    current_path.parent.mkdir(parents=True)
    asset_names = (
        "instruments",
        "daily_clean",
        "universe_by_date",
        "universe_symbols",
        "universe_meta",
        "pit_fundamentals",
        "industry_changes",
    )
    current_path.write_text(
        json.dumps(
            {
                "contract": {
                    "market": "a_share",
                    "provider": "synthetic",
                    "target_date": "2026-09-24",
                },
                "assets": {
                    name: {
                        "exists": True,
                        "manifest_path": f"manifests/{name}.json",
                        "manifest": {
                            "status": "completed",
                            "query": {
                                "start_date": "2018-01-01",
                                "end_date": "2026-09-24",
                            },
                        },
                    }
                    for name in asset_names
                },
            }
        ),
        encoding="utf-8",
    )
    (root / "metadata" / "dataset_registry.csv").write_text(
        "dataset_name\na_share_current_contract\n", encoding="utf-8"
    )

    report = _report(tmp_path, _profile())

    assert report["contract"]["effective_start_date"] == "20180101"
    assert report["contract"]["effective_end_date"] == "20260924"
    assert report["contract"]["assets"]["daily_clean"]["manifest_status"] == "completed"
