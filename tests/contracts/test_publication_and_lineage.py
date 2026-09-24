from __future__ import annotations

import json
from pathlib import Path

import pytest
from research_contracts import (
    PLATFORM_PUBLICATION_SCHEMA_VERSION,
    build_file_receipts,
    file_sha256,
    lineage_inputs,
    load_platform_publication_manifest,
)


def _publication_payload() -> dict[str, object]:
    return {
        "schema_version": PLATFORM_PUBLICATION_SCHEMA_VERSION,
        "generated_at": "2026-09-25T09:10:00+00:00",
        "producer_repository": "quant-research",
        "producer_commit": "0123456789abcdef",
        "run_id": "run-1",
        "artifacts": [
            {
                "artifact_id": "public-metrics",
                "relative_path": "public/metrics.json",
                "schema_version": "metrics.v1",
                "sha256": "a" * 64,
                "media_type": "application/json",
                "audience": "public",
                "consumers": ["quant-platform"],
            },
            {
                "artifact_id": "internal-notes",
                "relative_path": "internal/notes.json",
                "schema_version": "notes.v1",
                "sha256": "b" * 64,
                "media_type": "application/json",
                "audience": "internal",
                "consumers": ["quant-platform"],
            },
        ],
    }


def test_publication_manifest_round_trips_and_filters_public_artifacts() -> None:
    manifest = load_platform_publication_manifest(_publication_payload())

    assert [item.artifact_id for item in manifest.for_consumer("quant-platform")] == [
        "public-metrics"
    ]
    assert len(manifest.for_consumer("quant-platform", allow_internal=True)) == 2


def test_publication_manifest_rejects_internal_artifact_for_public_consumer() -> None:
    with pytest.raises(ValueError, match="internal artifacts cannot be published"):
        load_platform_publication_manifest(
            _publication_payload(), consumer="quant-platform", allow_internal=False
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "schema_version",
            "research.platform-publication.v0",
            "unsupported platform publication schema",
        ),
        ("generated_at", "2026-09-25T09:10:00", "generated_at must be timezone-aware"),
        ("artifacts", [], "artifacts must be a non-empty list"),
        ("artifacts", [None], "each artifact must be an object"),
    ],
)
def test_publication_manifest_rejects_invalid_payload(
    field: str, value: object, message: str
) -> None:
    payload = _publication_payload()
    payload[field] = value

    with pytest.raises(ValueError, match=message):
        load_platform_publication_manifest(payload)


def test_lineage_inputs_capture_hashes_of_existing_run_files(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    summary.write_text(json.dumps({"run_id": "run-1"}), encoding="utf-8")
    positions = tmp_path / "positions.csv"
    positions.write_text("symbol,weight\nAAA,1.0\n", encoding="utf-8")

    inputs = lineage_inputs(
        run_dir=tmp_path,
        holdings_payload={"positions_file": str(positions)},
    )

    assert [item.artifact_id for item in inputs] == [
        "strategy-pipeline.run:summary.json",
        "strategy-pipeline.run:positions_file",
    ]
    assert inputs[0].sha256 == file_sha256(summary)
    assert inputs[1].sha256 == file_sha256(positions)


def test_lineage_inputs_ignores_absent_optional_files(tmp_path: Path) -> None:
    inputs = lineage_inputs(run_dir=tmp_path, holdings_payload={})

    assert inputs == []


def test_file_receipts_sort_paths_before_building_inventory(tmp_path: Path) -> None:
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")

    receipts = build_file_receipts(tmp_path, [second, first])

    assert [receipt.path for receipt in receipts] == ["a.json", "b.json"]
