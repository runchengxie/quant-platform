from __future__ import annotations

import json
from pathlib import Path

from research_contracts import validate_artifact_contract_manifest
from research_contracts.artifact_contracts import (
    ARTIFACT_CONTRACT_SCHEMA_VERSION,
    ARTIFACT_ENVELOPE_SCHEMA_VERSION,
    CORE_ARTIFACTS,
)


def _manifest() -> dict[str, object]:
    return {
        "schema_version": ARTIFACT_CONTRACT_SCHEMA_VERSION,
        "artifact_envelope": {
            "schema_version": ARTIFACT_ENVELOPE_SCHEMA_VERSION,
            "write_mode": "opt_in",
            "container_key": "artifact_envelope",
            "required_fields": ["artifact_id", "content_sha256"],
        },
        "artifacts": [
            {
                "artifact": artifact,
                "contract": f"{artifact}.v1",
                "owner": "research-workspace",
                "required_fields": ["run_id"],
                "canonical_files": ["docs/contracts.md"],
                "entrypoints": [{"repo": "research-workspace", "path": "src/owner.py"}],
            }
            for artifact in sorted(CORE_ARTIFACTS)
        ],
    }


def _write_fixture(root: Path, manifest: dict[str, object]) -> tuple[Path, Path]:
    docs = root / "docs" / "contracts.md"
    docs.parent.mkdir(parents=True)
    entrypoint = root / "src" / "owner.py"
    entrypoint.parent.mkdir()
    entrypoint.write_text("pass\n", encoding="utf-8")
    docs.write_text(
        "\n".join(
            [
                "signals.parquet signals.parquet.v1 research-workspace",
                "signals.meta.json signals.meta.json.v1 research-workspace",
                "positions_by_rebalance.csv positions_by_rebalance.csv.v1 research-workspace",
                "targets.json targets.json.v1 research-workspace",
                "docs/contracts.md",
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = root / "artifact-contracts.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, docs


def test_artifact_contract_manifest_accepts_complete_synthetic_contracts(tmp_path: Path) -> None:
    manifest_path, docs = _write_fixture(tmp_path, _manifest())

    result = validate_artifact_contract_manifest(
        root=tmp_path, manifest_path=manifest_path, docs_path=docs
    )

    assert result.ok
    assert result.issues == ()


def test_artifact_contract_manifest_reports_invalid_metadata_and_missing_core_artifacts(
    tmp_path: Path,
) -> None:
    payload = _manifest()
    payload["schema_version"] = "unsupported"
    payload["artifacts"] = [
        {
            "artifact": "custom.json",
            "contract": "",
            "owner": "unknown",
            "required_fields": [],
            "entrypoints": [],
        }
    ]
    manifest_path, docs = _write_fixture(tmp_path, payload)

    result = validate_artifact_contract_manifest(
        root=tmp_path, manifest_path=manifest_path, docs_path=docs
    )

    assert not result.ok
    assert "unexpected schema_version" in result.issues
    assert "custom.json: contract is required" in result.issues
    assert "custom.json: unknown owner 'unknown'" in result.issues
    assert "custom.json: required_fields must be non-empty" in result.issues
    assert "custom.json: entrypoints must be non-empty" in result.issues
    assert any(issue.startswith("missing core artifacts:") for issue in result.issues)


def test_artifact_contract_manifest_rejects_non_object_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / "invalid.json"
    manifest_path.write_text("[]", encoding="utf-8")
    docs = tmp_path / "contracts.md"
    docs.write_text("", encoding="utf-8")

    result = validate_artifact_contract_manifest(
        root=tmp_path, manifest_path=manifest_path, docs_path=docs
    )

    assert not result.ok
    assert "artifact contract manifest must be a JSON object" in result.issues[0]
