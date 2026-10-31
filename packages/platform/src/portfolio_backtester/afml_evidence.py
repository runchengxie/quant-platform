"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "HrpConfig",
    "Mapping",
    "Path",
    "SupportsFloat",
    "_evidence_entry",
    "_infer_periods_per_year",
    "_load_run_config",
    "_mapping",
    "_optional_artifact",
    "_optional_float",
    "_read_return_series",
    "_read_returns_matrix",
    "_resolve_positions_path",
    "_write_hrp_receipt",
    "_write_sizing_receipt",
    "_write_strategy_risk_report",
    "annotations",
    "build_portfolio_sizing_receipt",
    "cast",
    "generate_run_afml_evidence",
    "hierarchical_risk_parity",
    "implementation_shortfall_metrics",
    "maybe_generate_run_afml_evidence",
    "merge_evidence_fragment",
    "sha256_file",
    "summarize_strategy_risk",
    "write_receipt",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.afml_evidence import (
        Any,
        HrpConfig,
        Mapping,
        Path,
        SupportsFloat,
        _evidence_entry,
        _infer_periods_per_year,
        _load_run_config,
        _mapping,
        _optional_artifact,
        _optional_float,
        _read_return_series,
        _read_returns_matrix,
        _resolve_positions_path,
        _write_hrp_receipt,
        _write_sizing_receipt,
        _write_strategy_risk_report,
        annotations,
        build_portfolio_sizing_receipt,
        cast,
        generate_run_afml_evidence,
        hierarchical_risk_parity,
        implementation_shortfall_metrics,
        maybe_generate_run_afml_evidence,
        merge_evidence_fragment,
        sha256_file,
        summarize_strategy_risk,
        write_receipt,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.afml_evidence")
