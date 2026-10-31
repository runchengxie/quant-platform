"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_OUTPUT_COLUMNS",
    "Any",
    "DailyWatch20Config",
    "DailyWatch20Receipt",
    "DailyWatch20Result",
    "DailyWatch20SelectionError",
    "FallbackMode",
    "GuardFactorSpec",
    "Literal",
    "Mapping",
    "ReceiptStatus",
    "_BSelection",
    "_PreparedCrossSection",
    "_SleeveSelection",
    "_base_receipt_summary",
    "_percentile_rank",
    "_prepare_cross_section",
    "_raise_unavailable",
    "_required_columns",
    "_trade_date_text",
    "_truthy",
    "_validate_column_settings",
    "_validate_config",
    "_validate_guard_factors",
    "_validate_portfolio_settings",
    "annotations",
    "cast",
    "dataclass",
    "field",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._daily_watch20_config import (
        _OUTPUT_COLUMNS,
        Any,
        DailyWatch20Config,
        DailyWatch20Receipt,
        DailyWatch20Result,
        DailyWatch20SelectionError,
        FallbackMode,
        GuardFactorSpec,
        Literal,
        Mapping,
        ReceiptStatus,
        _base_receipt_summary,
        _BSelection,
        _percentile_rank,
        _prepare_cross_section,
        _PreparedCrossSection,
        _raise_unavailable,
        _required_columns,
        _SleeveSelection,
        _trade_date_text,
        _truthy,
        _validate_column_settings,
        _validate_config,
        _validate_guard_factors,
        _validate_portfolio_settings,
        annotations,
        cast,
        dataclass,
        field,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._daily_watch20_config")
