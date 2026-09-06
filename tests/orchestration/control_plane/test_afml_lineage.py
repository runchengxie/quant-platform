from __future__ import annotations

import hashlib
import json
from pathlib import Path

from strategy_pipeline.control_plane.afml_lineage import attach_afml_evidence_to_lineage


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_afml_evidence_is_bound_to_targets_lineage(tmp_path: Path) -> None:
    lineage = tmp_path / "targets.json.lineage.json"
    lineage.write_text(
        json.dumps({"targets_file": "targets.json", "source": {"run_dir": str(tmp_path)}}),
        encoding="utf-8",
    )
    protocol = tmp_path / "research_protocol_report.json"
    protocol.write_text(
        json.dumps(
            {
                "level": "release",
                "status": "pass",
                "manifest_sha256": "manifest-hash",
            }
        ),
        encoding="utf-8",
    )
    sizing = tmp_path / "sizing_receipt.json"
    sizing.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    risk = tmp_path / "strategy_risk_report.json"
    risk.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")

    payload = attach_afml_evidence_to_lineage(lineage, run_dir=tmp_path)

    assert payload["research_protocol"]["status"] == "pass"
    assert payload["research_protocol"]["sha256"] == _sha256(protocol)
    assert payload["sizing_receipt"]["sha256"] == _sha256(sizing)
    assert payload["strategy_risk"]["sha256"] == _sha256(risk)
    assert payload["afml_evidence"]["run_dir"] == str(tmp_path)


def test_lineage_binding_rejects_non_release_protocol(tmp_path: Path) -> None:
    lineage = tmp_path / "targets.json.lineage.json"
    lineage.write_text(json.dumps({"targets_file": "targets.json"}), encoding="utf-8")
    (tmp_path / "research_protocol_report.json").write_text(
        json.dumps({"level": "candidate", "status": "pass"}),
        encoding="utf-8",
    )

    try:
        attach_afml_evidence_to_lineage(lineage, run_dir=tmp_path)
    except ValueError as exc:
        assert "passed release report" in str(exc)
    else:
        raise AssertionError("candidate protocol must not be bound as release evidence")
