"""Publish a complete canonical backend result as official execution evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ..backtest_bundle import BacktestBundleManifest, BacktestEvidenceTier
from ..backtest_bundle_io import write_backtest_bundle
from .base import CanonicalBacktestResult


def write_execution_aware_result_bundle(
    output_dir: Path,
    *,
    result: CanonicalBacktestResult,
    run_id: str,
    research_clock: Mapping[str, Any],
    producer: Mapping[str, Any],
    configuration_sha256: str,
    input_refs: Sequence[Mapping[str, Any]] = (),
    diagnostics: Mapping[str, Any] | None = None,
) -> BacktestBundleManifest:
    """Write a hash-verified bundle from a backend's full execution ledger.

    The returned manifest is official execution-aware evidence only after the
    existing bundle writer validates capabilities, clock, and reconciliation.
    """

    result.validate()
    ledger = result.unified_ledger
    if ledger is None:
        raise ValueError("Execution-aware bundle requires a full execution ledger.")
    if producer.get("backend") != result.backend_name:
        raise ValueError("producer.backend must match the canonical result backend")
    return write_backtest_bundle(
        output_dir,
        run_id=run_id,
        evidence_tier=BacktestEvidenceTier.EXECUTION_AWARE,
        ledger=ledger,
        research_clock=research_clock,
        backend={
            "name": result.backend_name,
            "version": producer.get("version"),
            "result_schema": result.schema_version,
        },
        backend_capabilities=result.capabilities.to_mapping(),
        producer=producer,
        configuration_sha256=configuration_sha256,
        input_refs=input_refs,
        diagnostics=diagnostics,
    )


__all__ = ["write_execution_aware_result_bundle"]
