"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "GRID_RESULT_FIELDS",
    "Path",
    "annotations",
    "get_rebalance_dates",
    "init_grid_row",
    "parse_date_list",
    "resolve_output_path",
    "resolve_rebalance_dates",
    "safe_run_name",
    "write_grid_rows",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.grid_support import (
        GRID_RESULT_FIELDS,
        Path,
        annotations,
        get_rebalance_dates,
        init_grid_row,
        parse_date_list,
        resolve_output_path,
        resolve_rebalance_dates,
        safe_run_name,
        write_grid_rows,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.grid_support")
