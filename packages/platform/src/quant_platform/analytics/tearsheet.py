"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "Path",
    "_date_range",
    "_format_number",
    "_merge_stats",
    "_prepare_returns",
    "_render_tearsheet_html",
    "_resolve_periods_per_year",
    "_subtitle_parts",
    "_summarize_series",
    "_tearsheet_charts",
    "annotations",
    "build_backtest_layer_comparison_frame",
    "build_backtest_tearsheet_html",
    "datetime",
    "write_backtest_tearsheet",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.tearsheet import (
        Any,
        Mapping,
        Path,
        _date_range,
        _format_number,
        _merge_stats,
        _prepare_returns,
        _render_tearsheet_html,
        _resolve_periods_per_year,
        _subtitle_parts,
        _summarize_series,
        _tearsheet_charts,
        annotations,
        build_backtest_layer_comparison_frame,
        build_backtest_tearsheet_html,
        datetime,
        write_backtest_tearsheet,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.tearsheet")
