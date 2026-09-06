from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from strategy_pipeline.e2_promotion_receipt import materialize_promotion_receipt


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _receipt_spec() -> dict[str, object]:
    return {
        "strategy_id": "synthetic_strategy",
        "profile_id": "public_example",
        "review_id": "example-20260825",
        "generated_at": "2026-08-25T11:00:00+00:00",
        "status": "passed",
        "research_window": {
            "configured_start_date": "20150101",
            "end_date": "20260821",
        },
        "lineage": {
            "producer_repository": "strategy-pipeline",
            "repositories": {"strategy-pipeline": "a" * 40},
            "config": {"path": "configs/example.yml"},
            "current_contract": {"path": "metadata/current.json"},
            "data_manifests": [{"path": "assets/manifest.json"}],
            "source_artifacts": [
                {"location": "workspace", "path": "evidence/source.json"},
                {"location": "data_platform", "path": "assets/coverage.json"},
            ],
        },
        "checks": {"cost": {"status": "passed"}},
        "limitations": [],
    }


def test_materialize_promotion_receipt_hashes_declared_inputs(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    data_root = tmp_path / "data-platform"
    config = workspace_root / "configs/example.yml"
    workspace_source = workspace_root / "evidence/source.json"
    current_contract = data_root / "metadata/current.json"
    daily_manifest = data_root / "assets/manifest.json"
    data_source = data_root / "assets/coverage.json"

    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("example: true\n", encoding="utf-8")
    _write_json(workspace_source, {"status": "passed"})
    _write_json(current_contract, {"current": True})
    _write_json(daily_manifest, {"dataset": "example"})
    _write_json(data_source, {"coverage": "example"})

    receipt = materialize_promotion_receipt(
        _receipt_spec(),
        workspace_root=workspace_root,
        data_platform_root=data_root,
    )

    lineage = receipt["lineage"]
    assert lineage["config"]["sha256"] == _sha256(config)
    assert lineage["current_contract"]["sha256"] == _sha256(current_contract)
    assert lineage["data_manifests"][0]["sha256"] == _sha256(daily_manifest)
    assert lineage["source_artifacts"][0]["sha256"] == _sha256(workspace_source)
    assert lineage["source_artifacts"][1]["sha256"] == _sha256(data_source)
    assert receipt["schema_version"] == "strategy_promotion_evidence.v2"


@pytest.mark.parametrize(
    "bad_path",
    ["/tmp/absolute.yml", "../escape.yml", "configs/../../escape.yml"],
)
def test_materialize_promotion_receipt_rejects_unsafe_paths(
    tmp_path: Path,
    bad_path: str,
) -> None:
    spec = _receipt_spec()
    lineage = cast(dict[str, Any], spec["lineage"])
    config = cast(dict[str, Any], lineage["config"])
    config["path"] = bad_path

    with pytest.raises(ValueError, match="safe relative path"):
        materialize_promotion_receipt(
            spec,
            workspace_root=tmp_path / "workspace",
            data_platform_root=tmp_path / "data-platform",
        )
