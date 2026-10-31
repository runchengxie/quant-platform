"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_MONTH_LABELS",
    "Any",
    "Mapping",
    "_date_range",
    "_escape",
    "_format_axis_value",
    "_format_date",
    "_format_metric",
    "_format_number",
    "_format_percent",
    "_heat_class",
    "_is_finite",
    "_metric",
    "_stylesheet",
    "_tick_values",
    "_x_tick_positions",
    "_year_value",
    "annotations",
    "cast",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._tearsheet_render import (
        _MONTH_LABELS,
        Any,
        Mapping,
        _date_range,
        _escape,
        _format_axis_value,
        _format_date,
        _format_metric,
        _format_number,
        _format_percent,
        _heat_class,
        _is_finite,
        _metric,
        _stylesheet,
        _tick_values,
        _x_tick_positions,
        _year_value,
        annotations,
        cast,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._tearsheet_render")
