"""Small, dependency-light publication handoff owned by quant-platform."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: object, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{field} is required")
    return result


def _relative_path(value: object) -> str:
    result = _text(value, "relative_path")
    path = PurePosixPath(result)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("relative_path must stay below the bundle root")
    return path.as_posix()


def _consumers(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError("consumers must be a list")
    consumers = [_text(item, "consumers[]") for item in value]
    if not consumers:
        raise ValueError("consumers must not be empty")
    return consumers


def build_platform_publication(
    *,
    artifacts: Sequence[Mapping[str, Any]],
    output_root: str | Path,
    generated_at: datetime,
    producer_repository: str,
    producer_commit: str,
    run_id: str,
) -> dict[str, Any]:
    """Copy approved projections and write a path-free publication manifest."""

    if not artifacts:
        raise ValueError("artifacts must not be empty")
    destination = Path(output_root).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.staging-", dir=destination.parent))
    try:
        manifest_artifacts = []
        for spec in artifacts:
            source = Path(spec.get("source_path", "")).expanduser().resolve()
            if not source.is_file():
                raise FileNotFoundError(f"publication source is missing: {source}")
            relative_path = _relative_path(spec.get("relative_path"))
            target = staging / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            manifest_artifacts.append(
                {
                    "artifact_id": _text(spec.get("artifact_id"), "artifact_id"),
                    "relative_path": relative_path,
                    "schema_version": _text(spec.get("schema_version"), "schema_version"),
                    "sha256": file_sha256(target),
                    "media_type": _text(spec.get("media_type"), "media_type"),
                    "audience": _text(spec.get("audience"), "audience"),
                    "consumers": _consumers(spec.get("consumers")),
                }
            )
        manifest = {
            "schema_version": "research.platform-publication.v1",
            "generated_at": generated_at.isoformat(),
            "producer_repository": _text(producer_repository, "producer_repository"),
            "producer_commit": _text(producer_commit, "producer_commit"),
            "run_id": _text(run_id, "run_id"),
            "artifacts": manifest_artifacts,
        }
        (staging / "platform-publication.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging)
