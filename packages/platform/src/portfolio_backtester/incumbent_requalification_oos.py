"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_SCORE_COLUMN",
    "IncumbentRequalificationConfig",
    "IncumbentRequalificationPolicy",
    "Literal",
    "SelectionStateMode",
    "_canonical_selected",
    "_incumbent_requalification_daily_rows",
    "_numeric_series",
    "_required_columns",
    "_series",
    "_validate_scored",
    "annotations",
    "cast",
    "portfolio_daily_row",
    "select_incumbent_requalified_portfolio",
    "stateful_incumbent_requalification_daily_rows",
    "stateless_incumbent_requalification_daily_rows",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.incumbent_requalification_oos import (
        DEFAULT_SCORE_COLUMN,
        IncumbentRequalificationConfig,
        IncumbentRequalificationPolicy,
        Literal,
        SelectionStateMode,
        _canonical_selected,
        _incumbent_requalification_daily_rows,
        _numeric_series,
        _required_columns,
        _series,
        _validate_scored,
        annotations,
        cast,
        portfolio_daily_row,
        select_incumbent_requalified_portfolio,
        stateful_incumbent_requalification_daily_rows,
        stateless_incumbent_requalification_daily_rows,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.incumbent_requalification_oos")
