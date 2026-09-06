from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from research_contracts import (
    build_platform_publication,
    file_sha256,
    load_platform_publication_manifest,
)


def test_publication_builder_copies_projection_without_source_path(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"status":"pass"}\n', encoding="utf-8")
    bundle = tmp_path / "bundle"

    manifest = build_platform_publication(
        artifacts=[
            {
                "source_path": source,
                "artifact_id": "strategy.evidence",
                "relative_path": "strategies/evidence.json",
                "schema_version": "strategy.evidence.v1",
                "media_type": "application/json",
                "audience": "internal",
                "consumers": ["market-intel"],
            }
        ],
        output_root=bundle,
        generated_at=datetime(2026, 9, 6, 5, 0, tzinfo=UTC),
        producer_repository="runchengxie/quant-research",
        producer_commit="private-staging",
        run_id="run-1",
    )

    payload = json.loads((bundle / "platform-publication.json").read_text(encoding="utf-8"))
    assert manifest.schema_version == "research.platform-publication.v1"
    assert "source_path" not in payload["artifacts"][0]
    assert payload["artifacts"][0]["sha256"] == file_sha256(bundle / "strategies/evidence.json")
    assert load_platform_publication_manifest(payload).artifacts[0].artifact_id == (
        "strategy.evidence"
    )


def test_publication_manifest_rejects_path_escape() -> None:
    with pytest.raises(ValueError, match="relative_path"):
        load_platform_publication_manifest(
            {
                "schema_version": "research.platform-publication.v1",
                "generated_at": "2026-09-06T05:00:00+00:00",
                "producer_repository": "runchengxie/quant-research",
                "producer_commit": "private-staging",
                "run_id": "run-1",
                "artifacts": [
                    {
                        "artifact_id": "bad",
                        "relative_path": "../outside.json",
                        "schema_version": "bad.v1",
                        "sha256": "0" * 64,
                        "media_type": "application/json",
                        "audience": "internal",
                        "consumers": ["market-intel"],
                    }
                ],
            }
        )
