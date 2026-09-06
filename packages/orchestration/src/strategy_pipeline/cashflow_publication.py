"""Publication boundary for the cashflow Feishu shadow signal."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "strategy_app.cashflow.selection.v1"
STRATEGY_ID = "cashflow_quality_top50_v1"
POLICY_ID = "cashflow_quality_top50_v1.quarterly_fcf_cap10.v1"
EXPECTED_POLICY = {
    "strategy_id": STRATEGY_ID,
    "policy_id": POLICY_ID,
    "top_n": 50,
    "max_weight": 0.10,
    "rebalance_frequency": "quarterly",
    "signal_timing": "source_close_to_next_open",
}


@dataclass(frozen=True)
class CashflowPublication:
    """Paths for one immutable shadow publication."""

    targets_path: Path
    receipt_path: Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _validate_readiness(
    readiness: dict[str, Any], *, allow_reconstructed_pit: bool = False
) -> None:
    if readiness.get("schema_version") != "cashflow_readiness.v1":
        raise ValueError("cashflow readiness schema is unsupported")
    if readiness.get("strategy_id") != STRATEGY_ID:
        raise ValueError("cashflow readiness strategy is unsupported")
    reconstructed = (
        allow_reconstructed_pit
        and readiness.get("decision") == "continue_shadow"
        and readiness.get("eligible_for_gray_push") is False
        and "pit" in (readiness.get("failed_gates") or [])
    )
    if readiness.get("eligible_for_gray_push") is not True and not reconstructed:
        raise ValueError("cashflow readiness is not eligible for gray push")
    if readiness.get("decision") != "candidate_for_gray_push" and not reconstructed:
        raise ValueError("cashflow readiness decision is not a gray-push candidate")
    if readiness.get("failed_gates") != [] and not reconstructed:
        raise ValueError("cashflow readiness has failed gates")
    if not reconstructed:
        attestation = readiness.get("evidence_attestation")
        if not isinstance(attestation, dict) or attestation.get("status") != "verified":
            raise ValueError("cashflow readiness evidence attestation is not verified")
        if re.fullmatch(r"[0-9a-f]{64}", str(attestation.get("bundle_sha256") or "")) is None:
            raise ValueError("cashflow readiness evidence attestation hash is invalid")
    if readiness.get("production_eligible") is not False:
        raise ValueError("cashflow readiness must remain non-production")


def _validate(
    selection: dict[str, Any],
    readiness: dict[str, Any],
    *,
    allow_reconstructed_pit: bool = False,
) -> None:
    if selection.get("schema_version") != EXPECTED_SCHEMA:
        raise ValueError("cashflow selection schema is unsupported")
    if selection.get("strategy_id") != STRATEGY_ID:
        raise ValueError("cashflow selection strategy is unsupported")
    if selection.get("policy_id") != POLICY_ID:
        raise ValueError("cashflow selection policy is unsupported")
    if selection.get("policy") != EXPECTED_POLICY:
        raise ValueError("cashflow selection policy mapping is not frozen")
    if selection.get("status") != "passed":
        raise ValueError("cashflow selection is not passed")
    if selection.get("eligible_for_live") is True:
        raise ValueError("cashflow selection is live-eligible")
    _validate_readiness(readiness, allow_reconstructed_pit=allow_reconstructed_pit)
    if allow_reconstructed_pit and selection.get("pit_quality") != "reconstructed":
        raise ValueError("reconstructed publication requires reconstructed selection PIT quality")
    targets = selection.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("cashflow selection has no targets")


def publish_cashflow_shadow(
    selection_path: str | Path,
    *,
    readiness_path: str | Path,
    output_root: str | Path,
    allow_reconstructed_pit: bool = False,
) -> CashflowPublication:
    """Publish a readiness-approved selection for Feishu shadow delivery."""
    selection_file = Path(selection_path)
    readiness_file = Path(readiness_path)
    selection = json.loads(selection_file.read_text(encoding="utf-8"))
    readiness = json.loads(readiness_file.read_text(encoding="utf-8"))
    _validate(selection, readiness, allow_reconstructed_pit=allow_reconstructed_pit)

    selection_sha = _sha256(selection_file)
    readiness_sha = _sha256(readiness_file)
    identity = {
        "strategy_id": STRATEGY_ID,
        "policy_id": selection["policy_id"],
        "source_date": selection["source_date"],
        "signal_date": selection["signal_date"],
        "selection_sha256": selection_sha,
        "readiness_sha256": readiness_sha,
    }
    publication_hash = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    root = Path(output_root).resolve()
    run_root = root / "publications" / f'{selection["signal_date"]}_{publication_hash[:16]}'
    targets_path = run_root / "targets.json"
    receipt_path = run_root / "receipt.json"
    receipt = {
        "schema_version": "strategy_pipeline.cashflow.publication.v1",
        "publication_tier": "feishu_shadow",
        "status": "passed",
        "research_only": True,
        "eligible_for_live": False,
        **identity,
        "publication_sha256": publication_hash,
    }
    if targets_path.exists() or receipt_path.exists():
        if not targets_path.is_file() or not receipt_path.is_file():
            raise ValueError("cashflow publication is incomplete")
        existing = json.loads(receipt_path.read_text(encoding="utf-8"))
        if existing != receipt or _sha256(targets_path) != selection_sha:
            raise ValueError("cashflow publication is immutable and was modified")
        return CashflowPublication(targets_path, receipt_path)

    run_root.mkdir(parents=True, exist_ok=False)
    try:
        shutil.copyfile(selection_file, targets_path)
        # The delivery adapter consumes the original selection payload.  The
        # receipt pins its exact bytes so a copied/edited target cannot pass.
        if _sha256(targets_path) != selection_sha:
            raise ValueError("cashflow target copy hash mismatch")
        _write_json(receipt_path, receipt)
        latest = root / "latest"
        if latest.exists() and not latest.is_symlink():
            raise ValueError("cashflow publication latest pointer is not a symlink")
        temporary = root / f".latest.{os.getpid()}.tmp"
        temporary.unlink(missing_ok=True)
        temporary.symlink_to(os.path.relpath(run_root, root), target_is_directory=True)
        temporary.replace(latest)
    except Exception:
        for path in (targets_path, receipt_path):
            path.unlink(missing_ok=True)
        run_root.rmdir()
        raise
    return CashflowPublication(targets_path, receipt_path)


__all__ = ["CashflowPublication", "publish_cashflow_shadow"]
