from __future__ import annotations

import json
from pathlib import Path

import pytest
from research_contracts import (
    MANIFEST_FILENAME,
    build_research_run_manifest,
    validate_research_run_manifest,
)
from research_contracts import research_run_manifest_writer as manifest_writer

_SHA = "a" * 64


def _clock() -> dict[str, str]:
    return {
        "schema_version": "research.clock.v1",
        "timezone": "UTC",
        "information_cutoff_at": "2026-09-25T09:00:00+00:00",
        "signal_at": "2026-09-25T09:01:00+00:00",
        "decision_at": "2026-09-25T09:02:00+00:00",
        "valuation_at": "2026-09-25T09:03:00+00:00",
        "timing_policy_id": "next_bar_open",
        "trading_calendar_ref": "synthetic-calendar-v1",
    }


def _run_dir(path: Path) -> Path:
    (path / "backtest_bundle").mkdir(parents=True)
    (path / "config.used.yml").write_text("seed: 1\n", encoding="utf-8")
    (path / "backtest_bundle" / "manifest.json").write_text("{}\n", encoding="utf-8")
    (path / "input.parquet").write_bytes(b"input")
    (path / "signal.json").write_text('{"signal": 1}\n', encoding="utf-8")
    return path


def _build(path: Path, *, clock: dict[str, str] | None = None) -> Path:
    return build_research_run_manifest(
        path,
        run_id="run-1",
        strategy_ref="strategy:synthetic-v1",
        research_purpose="contract test",
        evidence_tier="diagnostic",
        clock=clock or _clock(),
        producer_versions=[{"repository": "quant-platform", "commit": "012345"}],
        data_refs=[{"path": "input.parquet", "artifact_id": "input-1"}],
        signal_refs=[{"path": "signal.json", "artifact_id": "signal-1"}],
    )


def test_research_run_manifest_builds_and_validates_local_artifact_hashes(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)

    manifest_path = _build(run_dir)
    manifest = validate_research_run_manifest(manifest_path)

    assert manifest_path.name == MANIFEST_FILENAME
    assert manifest.run_id == "run-1"
    assert (
        manifest.data_refs[0].sha256 == manifest.signal_refs[0].sha256
        or len(manifest.data_refs[0].sha256) == 64
    )


def test_research_run_manifest_rejects_clock_causality_failure(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    clock = _clock()
    clock["information_cutoff_at"] = "2026-09-25T09:02:30+00:00"

    with pytest.raises(ValueError, match="information_cutoff_at must be <= signal_at"):
        _build(run_dir, clock=clock)


def test_research_run_manifest_requires_provenance_for_execution_aware_tier(
    tmp_path: Path,
) -> None:
    payload = {
        "schema_version": "research.backtest-run.v1",
        "run_id": "run-1",
        "strategy_ref": "strategy:synthetic-v1",
        "research_purpose": "contract test",
        "evidence_tier": "execution_aware",
        "clock": {
            **_clock(),
            "earliest_order_at": "2026-09-25T09:03:00+00:00",
            "execution_window_start_at": "2026-09-25T09:03:00+00:00",
            "execution_window_end_at": "2026-09-25T09:04:00+00:00",
            "valuation_at": "2026-09-25T09:05:00+00:00",
        },
        "configuration_sha256": _SHA,
        "producer_versions": [],
        "data_refs": [],
        "signal_refs": [],
        "portfolio_result_ref": {"artifact_id": "portfolio", "sha256": _SHA},
        "created_at": "2026-09-25T09:05:00+00:00",
        "provenance": {},
    }

    with pytest.raises(ValueError, match="provenance missing required fields"):
        from research_contracts import ResearchRunManifest

        ResearchRunManifest.from_mapping(payload)


def test_research_run_manifest_writer_cleans_temporary_file_after_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir = _run_dir(tmp_path)
    destination = tmp_path / "published" / MANIFEST_FILENAME

    def fail_replace(source: str | Path, target: str | Path) -> None:
        raise OSError("simulated atomic replace failure")

    monkeypatch.setattr(manifest_writer.os, "replace", fail_replace)

    with pytest.raises(OSError, match="simulated atomic replace failure"):
        build_research_run_manifest(
            run_dir,
            run_id="run-1",
            strategy_ref="strategy:synthetic-v1",
            research_purpose="atomic write test",
            evidence_tier="diagnostic",
            clock=_clock(),
            producer_versions=[],
            data_refs=[],
            signal_refs=[],
            output_path=destination,
        )

    assert not destination.exists()
    assert not list(destination.parent.glob(f".{destination.name}.*.tmp"))


def test_research_run_manifest_validator_rejects_noncanonical_optional_field(
    tmp_path: Path,
) -> None:
    run_dir = _run_dir(tmp_path)
    manifest_path = _build(run_dir)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["benchmark_ref"] = None
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="not canonical JSON"):
        validate_research_run_manifest(manifest_path)
