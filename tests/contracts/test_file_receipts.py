from __future__ import annotations

from pathlib import Path

import pytest
from research_contracts import (
    FileReceipt,
    build_file_receipts,
    file_receipt_payload,
    validate_file_receipts,
)


def test_file_receipts_hash_and_validate_required_files(tmp_path: Path) -> None:
    artifact = tmp_path / "bundle" / "targets.json"
    artifact.parent.mkdir()
    artifact.write_text('{"targets": []}\n', encoding="utf-8")

    receipts = build_file_receipts(artifact.parent, [artifact])
    payload = file_receipt_payload(receipts)

    assert receipts[0].path == "targets.json"
    assert (
        validate_file_receipts(artifact.parent, payload, required_files=["targets.json"])
        == receipts
    )


def test_file_receipts_reject_missing_file(tmp_path: Path) -> None:
    artifact = tmp_path / "targets.json"
    artifact.write_text("targets", encoding="utf-8")
    payload = file_receipt_payload(build_file_receipts(tmp_path, [artifact]))
    artifact.unlink()

    with pytest.raises(ValueError, match=r"artifact file is missing: targets.json"):
        validate_file_receipts(tmp_path, payload)


def test_file_receipts_reject_same_size_content_tampering(tmp_path: Path) -> None:
    artifact = tmp_path / "targets.json"
    artifact.write_text("first", encoding="utf-8")
    payload = file_receipt_payload(build_file_receipts(tmp_path, [artifact]))
    artifact.write_text("other", encoding="utf-8")

    with pytest.raises(ValueError, match=r"artifact file SHA-256 mismatch: targets.json"):
        validate_file_receipts(tmp_path, payload)


def test_file_receipts_reject_unsafe_relative_paths() -> None:
    with pytest.raises(ValueError, match="safe relative path"):
        FileReceipt.from_mapping({"path": "../outside.txt", "sha256": "a" * 64, "size": 1})


def test_file_receipts_reject_inventory_digest_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "targets.json"
    artifact.write_text("targets", encoding="utf-8")
    payload = file_receipt_payload(build_file_receipts(tmp_path, [artifact]))
    payload["inventory_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="inventory SHA-256 mismatch"):
        validate_file_receipts(tmp_path, payload)
