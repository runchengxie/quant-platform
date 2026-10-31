"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "BacktestTopKFn",
    "Callable",
    "DynamicEnsembleFn",
    "_construction_grid_reports",
    "_read_returns_file",
    "add_construction_grid_args",
    "annotations",
    "build_construction_grid",
    "build_inertia_selection_report",
    "run",
    "select_construction_variant_with_inertia",
    "write_reports",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.construction_grid import (
        Any,
        BacktestTopKFn,
        Callable,
        DynamicEnsembleFn,
        _construction_grid_reports,
        _read_returns_file,
        add_construction_grid_args,
        annotations,
        build_construction_grid,
        build_inertia_selection_report,
        run,
        select_construction_variant_with_inertia,
        write_reports,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.construction_grid")
