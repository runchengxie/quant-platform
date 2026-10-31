"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_MONTH_LABELS",
    "Any",
    "Mapping",
    "_drawdown_period_record",
    "_drawdown_periods",
    "_drawdown_table",
    "_eoy_returns_table",
    "_escape",
    "_format_date",
    "_format_metric",
    "_format_number",
    "_format_percent",
    "_heat_class",
    "_is_finite",
    "_layer_comparison_table",
    "_metric",
    "_metrics_table",
    "_monthly_returns_table",
    "_render_tearsheet_html",
    "_stylesheet",
    "_year_value",
    "annotations",
    "cast",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._tearsheet_tables import (
        _MONTH_LABELS,
        Any,
        Mapping,
        _drawdown_period_record,
        _drawdown_periods,
        _drawdown_table,
        _eoy_returns_table,
        _escape,
        _format_date,
        _format_metric,
        _format_number,
        _format_percent,
        _heat_class,
        _is_finite,
        _layer_comparison_table,
        _metric,
        _metrics_table,
        _monthly_returns_table,
        _render_tearsheet_html,
        _stylesheet,
        _year_value,
        annotations,
        cast,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._tearsheet_tables")
