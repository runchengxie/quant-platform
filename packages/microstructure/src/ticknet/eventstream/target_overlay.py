"""Load a point-in-time target overlay manifest for materialized windows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


def _read_manifest(manifest_path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"无法读取标签覆盖层清单：{manifest_path}") from error
    if not isinstance(manifest, dict):
        raise ValueError("标签覆盖层清单必须是 JSON 对象")
    return cast(dict[str, Any], manifest)


def _validate_manifest_binding(
    manifest: dict[str, Any], *, expected_materialized_fingerprint: str, expected_partition: str
) -> list[dict[str, Any]]:
    if manifest.get("materialized_fingerprint") != expected_materialized_fingerprint:
        raise ValueError("标签覆盖层与物化训练集 fingerprint 不一致")
    if manifest.get("partition") != expected_partition:
        raise ValueError("标签覆盖层分区与物化训练集不一致")
    fingerprint = manifest.get("dataset_fingerprint")
    files = manifest.get("files")
    if not isinstance(fingerprint, str) or not fingerprint:
        raise ValueError("标签覆盖层缺少 dataset_fingerprint")
    if not isinstance(files, list):
        raise ValueError("标签覆盖层 files 必须是列表")
    return cast(list[dict[str, Any]], files)


def _validate_shard_record(index: int, raw_record: object, root: Path) -> dict[str, Any]:
    if not isinstance(raw_record, dict):
        raise ValueError(f"标签覆盖层第 {index} 个分片记录必须是对象")
    month = raw_record.get("month")
    samples = raw_record.get("samples")
    shard_path = raw_record.get("path")
    if not isinstance(month, str) or not month:
        raise ValueError(f"标签覆盖层第 {index} 个分片缺少 month")
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 0:
        raise ValueError(f"标签覆盖层第 {index} 个分片 samples 无效")
    if not isinstance(shard_path, str) or not shard_path:
        raise ValueError(f"标签覆盖层第 {index} 个分片缺少 path")
    resolved_path = (root / shard_path).resolve()
    if not resolved_path.is_relative_to(root):
        raise ValueError(f"标签覆盖层第 {index} 个分片路径越界")
    return cast(dict[str, Any], raw_record)


def load_target_overlay_manifest(
    root: Path,
    *,
    expected_materialized_fingerprint: str,
    expected_partition: str,
) -> dict[str, Any]:
    """Validate and return an overlay manifest before loading its NumPy shards.

    The manifest binds one target overlay to the exact materialized dataset and
    partition it was generated for. Shard paths are restricted to the overlay
    directory so an edited manifest cannot point dataset loading outside it.
    """
    root_path = Path(root).expanduser().resolve()
    manifest = _read_manifest(root_path / "manifest.json")
    files = _validate_manifest_binding(
        manifest,
        expected_materialized_fingerprint=expected_materialized_fingerprint,
        expected_partition=expected_partition,
    )
    records = [
        _validate_shard_record(index, record, root_path) for index, record in enumerate(files)
    ]
    return {**manifest, "files": records}
