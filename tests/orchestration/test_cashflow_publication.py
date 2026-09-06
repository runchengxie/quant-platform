from __future__ import annotations

import json
from pathlib import Path

import pytest
from strategy_pipeline.cashflow_publication import publish_cashflow_shadow


def _selection(path: Path, *, eligible_for_live: bool = False) -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "strategy_app.cashflow.selection.v1",
                "status": "passed",
                "research_only": True,
                "eligible_for_live": eligible_for_live,
                "strategy_id": "cashflow_quality_top50_v1",
                "policy_id": "cashflow_quality_top50_v1.quarterly_fcf_cap10.v1",
                "policy": {
                    "strategy_id": "cashflow_quality_top50_v1",
                    "policy_id": "cashflow_quality_top50_v1.quarterly_fcf_cap10.v1",
                    "top_n": 50,
                    "max_weight": 0.10,
                    "rebalance_frequency": "quarterly",
                    "signal_timing": "source_close_to_next_open",
                },
                "source_date": "20260820",
                "signal_date": "20260821",
                "content_sha256": "a" * 64,
                "targets": [
                    {
                        "symbol": "000001.SZ",
                        "target_weight": 1.0,
                        "selection_rank": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _readiness(path: Path, *, passed: bool = True) -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "cashflow_readiness.v1",
                "strategy_id": "cashflow_quality_top50_v1",
                "evidence_attestation": {"status": "verified", "bundle_sha256": "a" * 64},
                "decision": "candidate_for_gray_push" if passed else "continue_shadow",
                "eligible_for_gray_push": passed,
                "production_eligible": False,
                "failed_gates": [] if passed else ["pit"],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_publish_cashflow_shadow_writes_immutable_targets_and_receipt(tmp_path: Path) -> None:
    output = publish_cashflow_shadow(
        _selection(tmp_path / "selection.json"),
        readiness_path=_readiness(tmp_path / "readiness.json"),
        output_root=tmp_path / "published",
    )

    receipt = json.loads(output.receipt_path.read_text(encoding="utf-8"))
    assert output.targets_path.is_file()
    assert receipt["publication_tier"] == "feishu_shadow"
    assert receipt["eligible_for_live"] is False
    assert (tmp_path / "published" / "latest").is_symlink()


def test_publish_cashflow_shadow_rejects_failed_readiness(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="readiness is not eligible"):
        publish_cashflow_shadow(
            _selection(tmp_path / "selection.json"),
            readiness_path=_readiness(tmp_path / "readiness.json", passed=False),
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_allows_reconstructed_research_mode_only_when_explicit(
    tmp_path: Path,
) -> None:
    selection = _selection(tmp_path / "selection.json")
    payload = json.loads(selection.read_text(encoding="utf-8"))
    payload["pit_quality"] = "reconstructed"
    selection.write_text(json.dumps(payload), encoding="utf-8")

    output = publish_cashflow_shadow(
        selection,
        readiness_path=_readiness(tmp_path / "readiness.json", passed=False),
        output_root=tmp_path / "published",
        allow_reconstructed_pit=True,
    )

    receipt = json.loads(output.receipt_path.read_text(encoding="utf-8"))
    assert receipt["research_only"] is True
    assert receipt["eligible_for_live"] is False


def test_publish_cashflow_shadow_rejects_live_eligible_selection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="live-eligible"):
        publish_cashflow_shadow(
            _selection(tmp_path / "selection.json", eligible_for_live=True),
            readiness_path=_readiness(tmp_path / "readiness.json"),
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_unknown_policy(tmp_path: Path) -> None:
    selection = _selection(tmp_path / "selection.json")
    payload = json.loads(selection.read_text(encoding="utf-8"))
    payload["policy_id"] = "cashflow_quality_top50_v1.weekly_uncapped.v0"
    selection.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="policy"):
        publish_cashflow_shadow(
            selection,
            readiness_path=_readiness(tmp_path / "readiness.json"),
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_policy_mapping_drift(tmp_path: Path) -> None:
    selection = _selection(tmp_path / "selection.json")
    payload = json.loads(selection.read_text(encoding="utf-8"))
    payload["policy"]["max_weight"] = 0.20
    selection.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="policy mapping"):
        publish_cashflow_shadow(
            selection,
            readiness_path=_readiness(tmp_path / "readiness.json"),
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_unattested_readiness(tmp_path: Path) -> None:
    readiness = _readiness(tmp_path / "readiness.json")
    payload = json.loads(readiness.read_text(encoding="utf-8"))
    payload.pop("evidence_attestation")
    readiness.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="attestation"):
        publish_cashflow_shadow(
            _selection(tmp_path / "selection.json"),
            readiness_path=readiness,
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_contradictory_readiness(tmp_path: Path) -> None:
    readiness = _readiness(tmp_path / "readiness.json")
    payload = json.loads(readiness.read_text(encoding="utf-8"))
    payload["failed_gates"] = ["pit"]
    readiness.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="failed gates"):
        publish_cashflow_shadow(
            _selection(tmp_path / "selection.json"),
            readiness_path=readiness,
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_unknown_readiness_schema(tmp_path: Path) -> None:
    readiness = _readiness(tmp_path / "readiness.json")
    payload = json.loads(readiness.read_text(encoding="utf-8"))
    payload["schema_version"] = "cashflow_readiness.v0"
    readiness.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="schema"):
        publish_cashflow_shadow(
            _selection(tmp_path / "selection.json"),
            readiness_path=readiness,
            output_root=tmp_path / "published",
        )


def test_publish_cashflow_shadow_rejects_tampered_existing_artifact(tmp_path: Path) -> None:
    selection = _selection(tmp_path / "selection.json")
    readiness = _readiness(tmp_path / "readiness.json")
    output = publish_cashflow_shadow(
        selection,
        readiness_path=readiness,
        output_root=tmp_path / "published",
    )
    output.targets_path.write_text("tampered", encoding="utf-8")

    with pytest.raises(ValueError, match="immutable"):
        publish_cashflow_shadow(
            selection,
            readiness_path=readiness,
            output_root=tmp_path / "published",
        )
