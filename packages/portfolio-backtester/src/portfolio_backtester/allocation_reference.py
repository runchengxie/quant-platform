"""Explicit market-reference artifact consumed by the allocation control plane."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_REFERENCE_COLUMNS = {"symbol", "price", "round_lot", "price_date"}


@dataclass(frozen=True, slots=True)
class AllocationReference:
    frame: pd.DataFrame
    price_date: str
    source: str
    path: Path


def _load_frame(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix in {".json", ".jsonl"}:
        return pd.read_json(path, lines=suffix == ".jsonl")
    raise SystemExit(
        "Allocation reference file must be .parquet, .csv, .json, or .jsonl: " + str(path)
    )


def load_allocation_reference(path: str | Path) -> AllocationReference:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise SystemExit(f"Allocation reference file not found: {resolved}")

    frame = _load_frame(resolved).copy()
    _require_reference_columns(frame)
    _normalize_reference_symbols(frame)
    _normalize_reference_prices(frame)
    price_date = _normalize_reference_dates(frame)
    _normalize_order_book_ids(frame)
    source = _reference_source(frame)
    return AllocationReference(
        frame=frame.reset_index(drop=True),
        price_date=price_date,
        source=source,
        path=resolved,
    )


def _require_reference_columns(frame: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_REFERENCE_COLUMNS.difference(frame.columns))
    if missing:
        raise SystemExit(
            "Allocation reference is missing required column(s): " + ", ".join(missing)
        )


def _normalize_reference_symbols(frame: pd.DataFrame) -> None:
    frame["symbol"] = frame["symbol"].astype(str).str.strip()
    if frame["symbol"].eq("").any():
        raise SystemExit("Allocation reference contains an empty symbol.")
    duplicates = sorted(frame.loc[frame["symbol"].duplicated(keep=False), "symbol"].unique())
    if duplicates:
        raise SystemExit(
            "Allocation reference contains duplicate symbol rows: " + ", ".join(duplicates)
        )


def _normalize_reference_prices(frame: pd.DataFrame) -> None:
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    frame["round_lot"] = pd.to_numeric(frame["round_lot"], errors="coerce")
    if frame["price"].isna().any() or (frame["price"] <= 0).any():
        raise SystemExit("Allocation reference price values must be positive numbers.")
    if frame["round_lot"].isna().any() or (frame["round_lot"] <= 0).any():
        raise SystemExit("Allocation reference round_lot values must be positive numbers.")
    non_integral_lot = (frame["round_lot"] % 1).abs() > 1e-12
    if non_integral_lot.any():
        raise SystemExit("Allocation reference round_lot values must be whole numbers.")
    frame["round_lot"] = frame["round_lot"].astype(int)


def _normalize_reference_dates(frame: pd.DataFrame) -> str:
    price_dates = pd.to_datetime(frame["price_date"], errors="coerce")
    if price_dates.isna().any():
        raise SystemExit("Allocation reference contains an invalid price_date.")
    normalized_dates = price_dates.dt.strftime("%Y-%m-%d")
    unique_dates = sorted(normalized_dates.unique())
    if len(unique_dates) != 1:
        raise SystemExit("Allocation reference must contain a single price_date snapshot.")
    frame["price_date"] = normalized_dates
    return str(unique_dates[0])


def _normalize_order_book_ids(frame: pd.DataFrame) -> None:
    if "order_book_id" not in frame.columns:
        frame["order_book_id"] = frame["symbol"]
    else:
        frame["order_book_id"] = (
            frame["order_book_id"].fillna(frame["symbol"]).astype(str).str.strip()
        )
        frame.loc[frame["order_book_id"].eq(""), "order_book_id"] = frame["symbol"]


def _reference_source(frame: pd.DataFrame) -> str:
    source = "reference_file"
    if "source" in frame.columns:
        sources = sorted(
            {str(value).strip() for value in frame["source"].dropna() if str(value).strip()}
        )
        if len(sources) > 1:
            raise SystemExit("Allocation reference must contain at most one source label.")
        if sources:
            source = sources[0]
    return source


def join_allocation_reference(
    selection: pd.DataFrame,
    reference: AllocationReference,
) -> pd.DataFrame:
    if "symbol" not in selection.columns:
        raise SystemExit("Allocation selection is missing symbol.")

    selected = selection.copy()
    selected["symbol"] = selected["symbol"].astype(str).str.strip()
    reference_columns = reference.frame[
        ["symbol", "order_book_id", "price", "round_lot", "price_date"]
    ].copy()
    joined = selected.merge(
        reference_columns,
        on="symbol",
        how="left",
        sort=False,
        validate="many_to_one",
    )
    missing_mask = joined["price"].isna() | joined["round_lot"].isna()
    if missing_mask.any():
        missing = sorted(joined.loc[missing_mask, "symbol"].astype(str).unique())
        raise SystemExit(
            "Allocation reference is missing selected symbol(s): " + ", ".join(missing)
        )
    return joined
