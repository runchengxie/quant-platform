from __future__ import annotations

import json
from pathlib import Path

from quant_execution_engine.evidence_bundle import create_evidence_bundle


def test_bundle_without_broker_context_marks_trace_not_applicable(tmp_path: Path) -> None:
    audit_dir = tmp_path / "outputs" / "orders"
    audit_dir.mkdir(parents=True)
    (audit_dir / "run.jsonl").write_text(
        json.dumps({"run_id": "run-1", "record_type": "rebalance_summary", "dry_run": True}) + "\n",
        encoding="utf-8",
    )

    result = create_evidence_bundle(
        run_id="run-1",
        project_root=tmp_path,
        output_dir=tmp_path / "bundles",
        created_at="2026-01-01T00:00:00+00:00",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    trace = next(item for item in manifest["artifacts"] if item["name"] == "order_traces")
    assert trace["status"] == "skipped_not_applicable"
    assert manifest["trace_summary"]["trace_count"] == 0
