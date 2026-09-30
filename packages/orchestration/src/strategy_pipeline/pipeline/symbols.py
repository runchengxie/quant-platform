"""Symbol handling for strategy pipeline input and output frames."""

from __future__ import annotations

import pandas as pd

from portfolio_backtester._symbol_utils import _ensure_symbol_columns

PROVIDER_SYMBOL_PRIORITY = ("ts_code", "stock_ticker", "order_book_id", "symbol")


def normalize_market(market: str | None, *, default: str | None = "a_share") -> str | None:
    fallback = None if default is None else str(default).strip().lower() or None
    value = str(market).strip().lower() if market is not None else None
    return value or fallback


def normalize_symbol_standard_name(name: object) -> str:
    text = str(name or "").strip()
    return "symbol" if text in {"symbol", "ts_code", "stock_ticker", "order_book_id"} else text


def normalize_symbol_for_market(value: object, *, market: str | None) -> str:
    text = str(value or "").strip()
    if not text or str(market or "").strip().lower() != "a_share":
        return text
    upper = text.upper()
    for suffix, exchange in ((".XSHG", ".SH"), (".XSHE", ".SZ"), (".SH", ".SH"), (".SZ", ".SZ")):
        if upper.endswith(suffix):
            return f"{upper[: -len(suffix)].zfill(6)}{exchange}"
    if upper.isdigit():
        code = upper.zfill(6)
        if code.startswith(("5", "6", "9")):
            return f"{code}.SH"
        if code.startswith(("0", "2", "3")):
            return f"{code}.SZ"
    return upper


def normalize_historical_hk_symbol(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    upper = text.upper()
    for suffix in (".XHKG", ".HK"):
        if upper.endswith(suffix):
            upper = upper[: -len(suffix)]
            break
    return f"{upper.zfill(5)}.HK" if upper.isdigit() else text


def ensure_symbol_columns(frame: pd.DataFrame, *, context: str) -> pd.DataFrame:
    return _ensure_symbol_columns(frame, context=context, priority=PROVIDER_SYMBOL_PRIORITY)
