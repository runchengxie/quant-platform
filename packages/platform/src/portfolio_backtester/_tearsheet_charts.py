"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_cumulative_frame",
    "_drawdown_chart_svg",
    "_escape",
    "_format_axis_value",
    "_layer_nav_frame",
    "_line_chart_svg",
    "_rolling_sharpe_frame",
    "_tearsheet_charts",
    "_tick_values",
    "_x_tick_positions",
    "annotations",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._tearsheet_charts import (
        _cumulative_frame,
        _drawdown_chart_svg,
        _escape,
        _format_axis_value,
        _layer_nav_frame,
        _line_chart_svg,
        _rolling_sharpe_frame,
        _tearsheet_charts,
        _tick_values,
        _x_tick_positions,
        annotations,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._tearsheet_charts")
