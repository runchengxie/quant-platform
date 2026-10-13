from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
from ticknet.eventstream.dataset import N_FEATURES
from ticknet.eventstream.materialized import (
    ARRAY_DTYPES,
    MANIFEST_NAME,
    MODE,
    PARTITIONS,
    SCHEMA_VERSION,
    MaterializedWindowDataset,
    _array_contract,
    validate_materialized_manifest,
    verify_materialized_dataset,
)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return _sha256(encoded)


def _fixture_manifest(root: Path) -> dict[str, Any]:
    contract = {
        "seq_len": 2,
        "use_lob_prefix": False,
        "use_session_anchors": False,
        "sampling_policy": "seeded_fixed_window_v1",
        "arrays": _array_contract(2),
    }
    shards = []
    for partition_index, partition in enumerate(PARTITIONS):
        month = f"20260{partition_index + 1}"
        files = []
        for name, dtype in ARRAY_DTYPES.items():
            tail_shape = tuple(contract["arrays"][name]["tail_shape"])
            array = np.zeros((1, *tail_shape), dtype=dtype)
            if name == "x":
                array[..., :N_FEATURES] = partition_index
            relative_path = Path("shards") / f"{partition}-{month}" / f"{name}.npy"
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as stream:
                np.save(stream, array, allow_pickle=False)
            content = path.read_bytes()
            files.append(
                {
                    "path": relative_path.as_posix(),
                    "bytes": len(content),
                    "sha256": _sha256(content),
                }
            )
        shards.append(
            {
                "partition": partition,
                "month": month,
                "samples": 1,
                "days": [20260101 + partition_index],
                "files": files,
            }
        )
    totals = {
        "shards": len(shards),
        "samples": len(shards),
        "bytes": sum(file["bytes"] for shard in shards for file in shard["files"]),
        "partitions": {
            partition: sum(shard["samples"] for shard in shards if shard["partition"] == partition)
            for partition in PARTITIONS
        },
    }
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "status": "complete",
        "contract": contract,
        "contract_sha256": _canonical_sha256(contract),
        "shards": shards,
        "totals": totals,
    }
    manifest["dataset_fingerprint"] = _canonical_sha256(
        {"contract": contract, "shards": shards, "totals": totals}
    )
    (root / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def _rewrite_manifest(root: Path, manifest: dict[str, Any]) -> None:
    manifest["totals"]["bytes"] = sum(
        file["bytes"] for shard in manifest["shards"] for file in shard["files"]
    )
    manifest["dataset_fingerprint"] = _canonical_sha256(
        {
            "contract": manifest["contract"],
            "shards": manifest["shards"],
            "totals": manifest["totals"],
        }
    )
    (root / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")


def test_complete_manifest_and_shard_files_verify(tmp_path: Path) -> None:
    manifest = _fixture_manifest(tmp_path)

    validate_materialized_manifest(manifest)
    result = verify_materialized_dataset(tmp_path)

    assert result["status"] == "complete"
    assert result["partitions"] == list(PARTITIONS)
    assert result["shards"] == len(PARTITIONS)
    assert result["samples"] == len(PARTITIONS)
    assert result["bytes"] == manifest["totals"]["bytes"]


def test_partition_verification_does_not_read_oos_files(tmp_path: Path) -> None:
    manifest = _fixture_manifest(tmp_path)
    oos_record = next(shard for shard in manifest["shards"] if shard["partition"] == "oos")
    oos_path = tmp_path / oos_record["files"][0]["path"]
    content = oos_path.read_bytes()
    oos_path.write_bytes(bytes([content[0] ^ 0x01]) + content[1:])

    train_result = verify_materialized_dataset(tmp_path, partitions=("train",))

    assert train_result["partitions"] == ["train"]
    assert train_result["shards"] == 1
    with pytest.raises(ValueError):
        verify_materialized_dataset(tmp_path)


def test_partition_verification_rejects_wrong_array_shape(tmp_path: Path) -> None:
    manifest = _fixture_manifest(tmp_path)
    train_record = next(shard for shard in manifest["shards"] if shard["partition"] == "train")
    x_record = next(file for file in train_record["files"] if file["path"].endswith("/x.npy"))
    x_path = tmp_path / x_record["path"]
    with x_path.open("wb") as stream:
        np.save(stream, np.zeros((1, 1, N_FEATURES), dtype=np.float32), allow_pickle=False)
    content = x_path.read_bytes()
    x_record["bytes"] = len(content)
    x_record["sha256"] = _sha256(content)
    _rewrite_manifest(tmp_path, manifest)

    with pytest.raises(ValueError):
        verify_materialized_dataset(tmp_path, partitions=("train",))


def test_materialized_dataset_preserves_tensor_contract_and_bounds(tmp_path: Path) -> None:
    _fixture_manifest(tmp_path)
    dataset = MaterializedWindowDataset(tmp_path, "train")

    sample = dataset[0]

    assert len(sample) == 10
    assert sample[0].shape == (2, N_FEATURES)
    assert sample[0].dtype == torch.float32
    assert sample[1].dtype == torch.int64
    assert sample[5].shape == (2, 3)
    assert sample[6].shape == ()
    assert sample[9].shape == ()
    assert len(dataset) == 1
    with pytest.raises(IndexError):
        _ = dataset[1]


def test_complete_manifest_requires_all_partitions(tmp_path: Path) -> None:
    manifest = _fixture_manifest(tmp_path)
    removed_shards = [shard for shard in manifest["shards"] if shard["partition"] == "oos"]
    manifest["shards"] = [shard for shard in manifest["shards"] if shard["partition"] != "oos"]
    manifest["totals"]["shards"] -= 1
    manifest["totals"]["samples"] -= 1
    manifest["totals"]["bytes"] -= sum(
        file["bytes"] for shard in removed_shards for file in shard["files"]
    )
    manifest["totals"]["partitions"]["oos"] = 0
    manifest["dataset_fingerprint"] = _canonical_sha256(
        {
            "contract": manifest["contract"],
            "shards": manifest["shards"],
            "totals": manifest["totals"],
        }
    )

    with pytest.raises(ValueError):
        validate_materialized_manifest(manifest)
