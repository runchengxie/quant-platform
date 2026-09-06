import json

import pytest

from strategy_pipeline.control_plane.targets import export_targets


def test_export_targets_writes_canonical_json_and_lineage(tmp_path):
    holdings = tmp_path / "holdings.json"
    holdings.write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "as_of": "2026-09-05",
                "holdings": [
                    {"symbol": "600000.SH", "weight": 0.6},
                    {"symbol": "000001.SZ", "weight": 0.3},
                ],
            }
        ),
        encoding="utf-8",
    )
    targets = tmp_path / "out" / "targets.json"

    lineage_path = export_targets(holdings, targets)

    assert json.loads(targets.read_text(encoding="utf-8")) == {
        "asof": "2026-09-05",
        "source": "strategy-pipeline",
        "target_gross_exposure": 0.99,
        "targets": [
            {"symbol": "600000", "market": "CN", "target_weight": 0.6},
            {"symbol": "000001", "market": "CN", "target_weight": 0.3},
        ],
    }
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    assert lineage["run_id"] == "run-1"
    assert lineage["target_count"] == 2
    assert lineage["content_sha256"]
    assert (
        lineage["artifact_envelope"]["schema_version"]
        == "research.artifact-envelope.v2"
    )


def test_export_targets_rejects_short_holdings(tmp_path):
    holdings = tmp_path / "holdings.json"
    holdings.write_text(
        json.dumps({"holdings": [{"symbol": "A", "weight": 1, "side": "short"}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="long-only"):
        export_targets(holdings, tmp_path / "targets.json")
