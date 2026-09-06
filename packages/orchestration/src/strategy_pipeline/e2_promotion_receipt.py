from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = "strategy_promotion_evidence.v2"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_STATUS = {"passed", "failed", "pending", "diagnostic", "superseded"}
_ALLOWED_SOURCE_LOCATIONS = {"workspace", "data_platform"}


def _mapping(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return {str(key): item for key, item in value.items()}


def _string(value: object, *, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} must be a non-empty string")
    return text


def _safe_path(root: Path, value: object, *, label: str) -> Path:
    text = _string(value, label=label)
    relative = Path(text)
    if relative.is_absolute():
        raise ValueError(f"{label} must be a safe relative path")
    base = root.expanduser().resolve()
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"{label} must be a safe relative path") from exc
    return resolved


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"declared input does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hashed_entry(entry: object, *, root: Path, label: str) -> dict[str, Any]:
    payload = _mapping(entry, label=label)
    path_text = _string(payload.get("path"), label=f"{label}.path")
    path = _safe_path(root, path_text, label=f"{label}.path")
    out = copy.deepcopy(payload)
    out["path"] = path_text
    out["sha256"] = _sha256_file(path)
    return out


def _repositories(value: object, *, producer_repository: str) -> dict[str, str]:
    payload = _mapping(value, label="lineage.repositories")
    repositories: dict[str, str] = {}
    for name, raw_sha in payload.items():
        sha = str(raw_sha or "").strip()
        if not _SHA40.fullmatch(sha):
            raise ValueError(
                f"lineage.repositories.{name} must be a 40-char lowercase git SHA"
            )
        repositories[name] = sha
    if producer_repository not in repositories:
        raise ValueError(
            "lineage.producer_repository must appear in lineage.repositories"
        )
    return repositories


def _data_root(data_platform_root: Path | None) -> Path:
    if data_platform_root is None:
        raise ValueError("data_platform_root is required for canonical A-share lineage")
    return data_platform_root


def _materialize_lineage(
    lineage: Mapping[str, Any],
    *,
    workspace_root: Path,
    data_root: Path,
) -> dict[str, Any]:
    producer = _string(
        lineage.get("producer_repository"),
        label="lineage.producer_repository",
    )
    repositories = _repositories(
        lineage.get("repositories"),
        producer_repository=producer,
    )
    config = _hashed_entry(
        lineage.get("config"),
        root=workspace_root,
        label="lineage.config",
    )
    current_contract = _hashed_entry(
        lineage.get("current_contract"),
        root=data_root,
        label="lineage.current_contract",
    )

    raw_manifests = lineage.get("data_manifests")
    if not isinstance(raw_manifests, list):
        raise TypeError("lineage.data_manifests must be a list")
    data_manifests = [
        _hashed_entry(item, root=data_root, label=f"lineage.data_manifests[{index}]")
        for index, item in enumerate(raw_manifests)
    ]

    raw_sources = lineage.get("source_artifacts")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ValueError("lineage.source_artifacts must be a non-empty list")
    source_artifacts: list[dict[str, Any]] = []
    for index, item in enumerate(raw_sources):
        payload = _mapping(item, label=f"lineage.source_artifacts[{index}]")
        location = _string(
            payload.get("location"),
            label=f"lineage.source_artifacts[{index}].location",
        )
        if location not in _ALLOWED_SOURCE_LOCATIONS:
            raise ValueError(f"unsupported source artifact location: {location}")
        root = workspace_root if location == "workspace" else data_root
        source_artifacts.append(
            _hashed_entry(
                payload,
                root=root,
                label=f"lineage.source_artifacts[{index}]",
            )
        )
    return {
        "producer_repository": producer,
        "repositories": repositories,
        "config": config,
        "current_contract": current_contract,
        "data_manifests": data_manifests,
        "source_artifacts": source_artifacts,
    }


def materialize_promotion_receipt(
    spec: Mapping[str, Any],
    *,
    workspace_root: Path,
    data_platform_root: Path | None,
) -> dict[str, Any]:
    """Materialize a hash-pinned canonical promotion receipt from an explicit spec.

    The writer never infers a research verdict. ``status`` and per-check statuses
    must already be present in the input spec; this function only validates the
    receipt identity and pins every declared lineage path by SHA-256.
    """

    source = _mapping(spec, label="spec")
    strategy_id = _string(source.get("strategy_id"), label="strategy_id")
    profile_id = _string(source.get("profile_id"), label="profile_id")
    review_id = _string(source.get("review_id"), label="review_id")
    generated_at = _string(source.get("generated_at"), label="generated_at")
    status = _string(source.get("status"), label="status")
    if status not in _ALLOWED_STATUS:
        raise ValueError(f"unsupported promotion receipt status: {status}")

    research_window = _mapping(source.get("research_window"), label="research_window")
    _string(
        research_window.get("configured_start_date"),
        label="research_window.configured_start_date",
    )
    _string(research_window.get("end_date"), label="research_window.end_date")

    lineage = _mapping(source.get("lineage"), label="lineage")
    data_root = _data_root(data_platform_root)
    materialized_lineage = _materialize_lineage(
        lineage,
        workspace_root=workspace_root,
        data_root=data_root,
    )

    checks = _mapping(source.get("checks"), label="checks")
    if not checks:
        raise ValueError("checks must not be empty")
    limitations = source.get("limitations", [])
    if not isinstance(limitations, list):
        raise TypeError("limitations must be a list")

    return {
        "schema_version": _SCHEMA_VERSION,
        "strategy_id": strategy_id,
        "profile_id": profile_id,
        "review_id": review_id,
        "generated_at": generated_at,
        "status": status,
        "research_window": copy.deepcopy(research_window),
        "lineage": materialized_lineage,
        "checks": copy.deepcopy(checks),
        "limitations": copy.deepcopy(limitations),
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize a SHA256-pinned canonical E2 promotion receipt."
    )
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--data-platform-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = materialize_promotion_receipt(
        _load_json(args.spec),
        workspace_root=args.workspace_root,
        data_platform_root=args.data_platform_root,
    )
    _write_json(args.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
