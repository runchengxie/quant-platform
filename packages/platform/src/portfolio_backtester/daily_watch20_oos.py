"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_SCORE_COLUMN",
    "Any",
    "IncumbentRequalificationConfig",
    "IncumbentRequalificationPolicy",
    "SelectionConfig",
    "_flag_masks",
    "_numeric_series",
    "_portfolio_daily_row",
    "_portfolio_daily_rows",
    "_series",
    "_trade_audit",
    "annotations",
    "cast",
    "guarded_a4b16_daily_rows",
    "incumbent_requalification_daily_rows",
    "name_turnover",
    "portfolio_daily_row",
    "portfolio_daily_rows",
    "portfolio_summary_fields",
    "select_daily_watch20",
    "select_incumbent_requalified_portfolio",
    "trade_audit",
    "turnover_from_trade_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.daily_watch20_oos import (
        DEFAULT_SCORE_COLUMN,
        Any,
        IncumbentRequalificationConfig,
        IncumbentRequalificationPolicy,
        SelectionConfig,
        _flag_masks,
        _numeric_series,
        _portfolio_daily_row,
        _portfolio_daily_rows,
        _series,
        _trade_audit,
        annotations,
        cast,
        guarded_a4b16_daily_rows,
        incumbent_requalification_daily_rows,
        name_turnover,
        portfolio_daily_row,
        portfolio_daily_rows,
        portfolio_summary_fields,
        select_daily_watch20,
        select_incumbent_requalified_portfolio,
        trade_audit,
        turnover_from_trade_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.daily_watch20_oos")
