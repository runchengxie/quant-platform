"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "FIELDNAMES",
    "Any",
    "Path",
    "_finite_float",
    "annotations",
    "build_inertia_selection_report",
    "select_construction_variant_with_inertia",
    "write_reports",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.construction_grid_reports import (
        FIELDNAMES,
        Any,
        Path,
        _finite_float,
        annotations,
        build_inertia_selection_report,
        select_construction_variant_with_inertia,
        write_reports,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.construction_grid_reports")
