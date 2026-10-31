"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Path",
    "_coerce_bool",
    "_first_non_empty",
    "_get_nested",
    "_load_json",
    "_load_pricing_data",
    "_load_scored_data",
    "_load_yaml",
    "_parse_date_list",
    "_parse_date_series",
    "_periods_per_year",
    "_read_returns_file",
    "_resolve_path",
    "_resolve_rebalance_dates",
    "annotations",
    "canonicalize_symbol_columns",
    "cast",
    "get_rebalance_dates",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._construction_grid_io import (
        Any,
        Path,
        _coerce_bool,
        _first_non_empty,
        _get_nested,
        _load_json,
        _load_pricing_data,
        _load_scored_data,
        _load_yaml,
        _parse_date_list,
        _parse_date_series,
        _periods_per_year,
        _read_returns_file,
        _resolve_path,
        _resolve_rebalance_dates,
        annotations,
        canonicalize_symbol_columns,
        cast,
        get_rebalance_dates,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._construction_grid_io")
