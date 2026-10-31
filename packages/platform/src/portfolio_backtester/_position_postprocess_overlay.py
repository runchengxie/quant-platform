"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Literal",
    "Mapping",
    "_apply_cash_gross_overlay",
    "_as_mapping",
    "_build_overlay_diagnostics",
    "_cfg_enabled",
    "_condition_matches",
    "_conditions_match",
    "_date_key_series",
    "_default_cash_overlay_gross",
    "_gross_by_rebalance",
    "_load_table",
    "_merge_eval_date_features",
    "_merge_overlay_source",
    "_numeric_condition_matches",
    "_overlay_date_col",
    "_resolve_target_gross_by_date",
    "_target_gross_for_row",
    "_target_gross_series",
    "_tier_conditions",
    "_validate_target_gross",
    "annotations",
    "logger",
    "resolve_data_input_path",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._position_postprocess_overlay import (
        Any,
        Literal,
        Mapping,
        _apply_cash_gross_overlay,
        _as_mapping,
        _build_overlay_diagnostics,
        _cfg_enabled,
        _condition_matches,
        _conditions_match,
        _date_key_series,
        _default_cash_overlay_gross,
        _gross_by_rebalance,
        _load_table,
        _merge_eval_date_features,
        _merge_overlay_source,
        _numeric_condition_matches,
        _overlay_date_col,
        _resolve_target_gross_by_date,
        _target_gross_for_row,
        _target_gross_series,
        _tier_conditions,
        _validate_target_gross,
        annotations,
        logger,
        resolve_data_input_path,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._position_postprocess_overlay")
