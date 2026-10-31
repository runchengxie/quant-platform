"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Path",
    "_apply_risk_penalty",
    "_build_base_context",
    "_construction_grid_config",
    "_first_non_empty",
    "_get_nested",
    "_load_grid_data_inputs",
    "_load_json",
    "_load_pricing_data",
    "_load_scored_data",
    "_prepare_signal_column",
    "_resolve_grid_columns",
    "_resolve_grid_rebalance_dates",
    "_resolve_path",
    "_resolve_rebalance_dates",
    "_validated_variants",
    "annotations",
    "apply_score_postprocess",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._construction_grid_signal import (
        Any,
        Path,
        _apply_risk_penalty,
        _build_base_context,
        _construction_grid_config,
        _first_non_empty,
        _get_nested,
        _load_grid_data_inputs,
        _load_json,
        _load_pricing_data,
        _load_scored_data,
        _prepare_signal_column,
        _resolve_grid_columns,
        _resolve_grid_rebalance_dates,
        _resolve_path,
        _resolve_rebalance_dates,
        _validated_variants,
        annotations,
        apply_score_postprocess,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._construction_grid_signal")
