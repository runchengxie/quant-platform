"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BACKTEST_BUNDLE_SCHEMA_VERSION",
    "EXECUTION_AWARE_BUNDLE_FILES",
    "_EXECUTION_CLOCK_FIELDS",
    "_SHA256",
    "Any",
    "BacktestBundleInventoryItem",
    "BacktestBundleManifest",
    "BacktestEvidenceTier",
    "Mapping",
    "Path",
    "StrEnum",
    "UnifiedLedger",
    "_mapping",
    "_mapping_list",
    "_require_columns",
    "_require_ledger_frames",
    "_required_text",
    "_sha256",
    "_validate_execution_metadata",
    "_validate_tca_calibration",
    "annotations",
    "cast",
    "dataclass",
    "reconcile_unified_ledger",
    "validate_execution_aware_bundle_inputs",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backtest_bundle import (
        _EXECUTION_CLOCK_FIELDS,
        _SHA256,
        BACKTEST_BUNDLE_SCHEMA_VERSION,
        EXECUTION_AWARE_BUNDLE_FILES,
        Any,
        BacktestBundleInventoryItem,
        BacktestBundleManifest,
        BacktestEvidenceTier,
        Mapping,
        Path,
        StrEnum,
        UnifiedLedger,
        _mapping,
        _mapping_list,
        _require_columns,
        _require_ledger_frames,
        _required_text,
        _sha256,
        _validate_execution_metadata,
        _validate_tca_calibration,
        annotations,
        cast,
        dataclass,
        reconcile_unified_ledger,
        validate_execution_aware_bundle_inputs,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backtest_bundle")
