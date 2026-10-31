"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Collection",
    "Counter",
    "DailyWatch20Config",
    "DailyWatch20Receipt",
    "DailyWatch20Result",
    "FallbackMode",
    "Mapping",
    "ReceiptStatus",
    "Sequence",
    "_BSelection",
    "_PreparedCrossSection",
    "_SleeveSelection",
    "_add_previous_candidates",
    "_base_receipt_summary",
    "_build_success_receipt",
    "_build_watchlist",
    "_candidate_score_snapshot",
    "_industry_map",
    "_prepare_cross_section",
    "_raise_unavailable",
    "_ranked_symbols",
    "_select_b",
    "_select_ranked_with_cap",
    "_select_sleeves",
    "_try_add_with_cap",
    "_validate_config",
    "_validate_selected_watchlist",
    "annotations",
    "select_daily_watch20",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._daily_watch20_select import (
        Collection,
        Counter,
        DailyWatch20Config,
        DailyWatch20Receipt,
        DailyWatch20Result,
        FallbackMode,
        Mapping,
        ReceiptStatus,
        Sequence,
        _add_previous_candidates,
        _base_receipt_summary,
        _BSelection,
        _build_success_receipt,
        _build_watchlist,
        _candidate_score_snapshot,
        _industry_map,
        _prepare_cross_section,
        _PreparedCrossSection,
        _raise_unavailable,
        _ranked_symbols,
        _select_b,
        _select_ranked_with_cap,
        _select_sleeves,
        _SleeveSelection,
        _try_add_with_cap,
        _validate_config,
        _validate_selected_watchlist,
        annotations,
        select_daily_watch20,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._daily_watch20_select")
