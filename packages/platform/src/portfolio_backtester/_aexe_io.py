"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "CACHE_FILE_TEMPLATE",
    "Any",
    "Path",
    "_adv_bucket",
    "_adv_notional",
    "_avg_impact_bps",
    "_blocked_trade_count",
    "_date8",
    "_holding_values",
    "_market_rows_by_symbol",
    "_rank_map",
    "_row_value",
    "_trade_notional",
    "_turnover_action_order",
    "annotations",
    "compute_stats",
    "load_positions",
    "load_prices",
    "portfolio_value",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._aexe_io import (
        CACHE_FILE_TEMPLATE,
        Any,
        Path,
        _adv_bucket,
        _adv_notional,
        _avg_impact_bps,
        _blocked_trade_count,
        _date8,
        _holding_values,
        _market_rows_by_symbol,
        _rank_map,
        _row_value,
        _trade_notional,
        _turnover_action_order,
        annotations,
        compute_stats,
        load_positions,
        load_prices,
        portfolio_value,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._aexe_io")
