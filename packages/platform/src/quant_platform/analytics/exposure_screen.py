"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "FIELDNAMES",
    "STYLE_FACTORS",
    "Any",
    "Path",
    "_active_summary_from_summary",
    "_check_row",
    "_finite_float",
    "_nested_mapping",
    "_read_json",
    "_resolve_path",
    "_row_id",
    "_screen_rows",
    "add_exposure_screen_args",
    "annotations",
    "build_exposure_screen",
    "run",
    "write_csv",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.exposure_screen import (
        FIELDNAMES,
        STYLE_FACTORS,
        Any,
        Path,
        _active_summary_from_summary,
        _check_row,
        _finite_float,
        _nested_mapping,
        _read_json,
        _resolve_path,
        _row_id,
        _screen_rows,
        add_exposure_screen_args,
        annotations,
        build_exposure_screen,
        run,
        write_csv,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.exposure_screen")
