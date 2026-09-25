import json

import pytest
from ticknet.eventstream.target_overlay import load_target_overlay_manifest


def _write_manifest(root, **updates):
    manifest = {
        "dataset_fingerprint": "overlay-sha",
        "materialized_fingerprint": "materialized-sha",
        "partition": "train",
        "files": [{"month": "202401", "samples": 12, "path": "labels-202401.npy"}],
    }
    manifest.update(updates)
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_load_target_overlay_manifest_validates_binding_and_shards(tmp_path):
    _write_manifest(tmp_path)

    manifest = load_target_overlay_manifest(
        tmp_path,
        expected_materialized_fingerprint="materialized-sha",
        expected_partition="train",
    )

    assert manifest["dataset_fingerprint"] == "overlay-sha"
    assert manifest["files"] == [{"month": "202401", "samples": 12, "path": "labels-202401.npy"}]


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"materialized_fingerprint": "other"}, "fingerprint"),
        ({"partition": "validation"}, "分区"),
        ({"files": [{"month": "202401", "samples": -1, "path": "labels.npy"}]}, "samples"),
        ({"files": [{"month": "202401", "samples": 1, "path": "../outside.npy"}]}, "越界"),
    ],
)
def test_load_target_overlay_manifest_rejects_invalid_bindings_and_shards(
    tmp_path, updates, message
):
    _write_manifest(tmp_path, **updates)

    with pytest.raises(ValueError, match=message):
        load_target_overlay_manifest(
            tmp_path,
            expected_materialized_fingerprint="materialized-sha",
            expected_partition="train",
        )
