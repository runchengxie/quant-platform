"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_construction_grid_reports",
    "_load_yaml",
    "_resolve_backtest_topk_fn",
    "_resolve_path",
    "add_construction_grid_args",
    "annotations",
    "build_construction_grid",
    "run",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._construction_grid_cli import (
        Any,
        _construction_grid_reports,
        _load_yaml,
        _resolve_backtest_topk_fn,
        _resolve_path,
        add_construction_grid_args,
        annotations,
        build_construction_grid,
        run,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._construction_grid_cli")
