from __future__ import annotations

import json
from pathlib import Path

from research_contracts import validate_contract_ownership


def _record() -> dict[str, object]:
    return {
        "name": "research.clock.v1",
        "schema": "research.clock.v1",
        "producer": "quant-research",
        "consumers": ["quant-platform", "quant-intel-platform"],
        "versioning": "semver",
        "compatibility": "additive-only",
        "test_command": "uv run pytest tests/contracts",
        "rollback": "restore previous manifest",
    }


def _write_registry(path: Path, records: list[object]) -> None:
    path.write_text(
        json.dumps({"schema_version": "contract_ownership.v1", "contracts": records}),
        encoding="utf-8",
    )


def test_contract_ownership_accepts_valid_registry(tmp_path: Path) -> None:
    registry = tmp_path / "ownership.json"
    _write_registry(registry, [_record()])

    result = validate_contract_ownership(registry_path=registry)

    assert result.ok
    assert result.issues == ()


def test_contract_ownership_rejects_duplicate_names(tmp_path: Path) -> None:
    registry = tmp_path / "ownership.json"
    _write_registry(registry, [_record(), _record()])

    result = validate_contract_ownership(registry_path=registry)

    assert not result.ok
    assert "research.clock.v1: duplicate name" in result.issues


def test_contract_ownership_rejects_invalid_record_types(tmp_path: Path) -> None:
    registry = tmp_path / "ownership.json"
    invalid = _record()
    invalid["consumers"] = ["quant-platform", 7]
    _write_registry(registry, [invalid])

    result = validate_contract_ownership(registry_path=registry)

    assert not result.ok
    assert "contracts[0].consumers[1]: must be a string" in result.issues


def test_contract_ownership_reports_artifact_manifest_mismatch(tmp_path: Path) -> None:
    registry = tmp_path / "ownership.json"
    manifest = tmp_path / "artifacts.json"
    _write_registry(registry, [_record()])
    manifest.write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "artifact": "research.clock.v1",
                        "contract": "research.clock.v2",
                        "producer": "quant-research",
                        "consumers": ["quant-platform", "quant-intel-platform"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = validate_contract_ownership(registry_path=registry, artifact_manifest_path=manifest)

    assert not result.ok
    assert "research.clock.v1: schema differs from artifact manifest" in result.issues


def test_contract_ownership_returns_missing_registry_issue(tmp_path: Path) -> None:
    result = validate_contract_ownership(registry_path=tmp_path / "missing.json")

    assert not result.ok
    assert "No such file or directory" in result.issues[0]
