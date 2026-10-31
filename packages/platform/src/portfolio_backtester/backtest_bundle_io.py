"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BACKTEST_BUNDLE_SCHEMA_VERSION",
    "UTC",
    "_FRAME_FILES",
    "Any",
    "BacktestBundleInventoryItem",
    "BacktestBundleManifest",
    "BacktestEvidenceTier",
    "Mapping",
    "Path",
    "Sequence",
    "UnifiedLedger",
    "_diagnostic_reconciliation",
    "_evidence_tier",
    "_file_sha256",
    "_inventory_content_sha256",
    "_json_payload",
    "_lineage_inputs",
    "_shared_contracts",
    "_write_json",
    "annotations",
    "datetime",
    "read_backtest_bundle",
    "reconcile_unified_ledger",
    "validate_execution_aware_bundle_inputs",
    "write_backtest_bundle",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backtest_bundle_io import (
        _FRAME_FILES,
        BACKTEST_BUNDLE_SCHEMA_VERSION,
        UTC,
        Any,
        BacktestBundleInventoryItem,
        BacktestBundleManifest,
        BacktestEvidenceTier,
        Mapping,
        Path,
        Sequence,
        UnifiedLedger,
        _diagnostic_reconciliation,
        _evidence_tier,
        _file_sha256,
        _inventory_content_sha256,
        _json_payload,
        _lineage_inputs,
        _shared_contracts,
        _write_json,
        annotations,
        datetime,
        read_backtest_bundle,
        reconcile_unified_ledger,
        validate_execution_aware_bundle_inputs,
        write_backtest_bundle,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backtest_bundle_io")
