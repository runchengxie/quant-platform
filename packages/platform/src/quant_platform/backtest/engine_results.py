"""Canonical views of explicit product evidence, without financial reconstruction."""

from __future__ import annotations

import math
import re
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import pandas as pd
from quant_backtest_core.artifacts import load_artifact
from quant_backtest_engine.product import ProductResult, result_to_json

from .contracts import BackendCapabilities, CanonicalBacktestResult, to_json_compatible
from .ledger import UnifiedLedger


def _dtype(value: str):
    """Decode the owner's documented dtype metadata without evaluating code."""
    match = re.fullmatch(r"dtype\('([^']+)'\)", value)
    if match:
        return match.group(1)
    if value == "<StringDtype(na_value=nan)>":
        return pd.StringDtype(na_value=float("nan"))
    match = re.fullmatch(r"<StringDtype\(storage='(python|pyarrow)', na_value=nan\)>", value)
    if match:
        return pd.StringDtype(storage=match.group(1), na_value=float("nan"))
    if value in ("str", "string", "string[python]", "string[pyarrow]"):
        return value
    raise ValueError(f"unsupported owner dtype: {value}")


def _scalar(value: Any):
    if isinstance(value, dict):
        if set(value) != {"nonfinite"} or value["nonfinite"] not in ("nan", "inf", "-inf"):
            raise ValueError("unsupported owner scalar tag")
        return float(value["nonfinite"])
    return value


def _owner_frame(value: dict[str, Any]) -> pd.DataFrame:
    columns = value["columns"]
    data = [[_scalar(v) for v in row] for row in value["data"]]
    frame = pd.DataFrame(data, columns=columns)
    for index, dtype in enumerate(value["dtypes"]):
        kind = _dtype(dtype)
        values = frame.iloc[:, index]
        if kind == "bool":
            values = values.map(
                lambda v: v if isinstance(v, bool) else {"True": True, "False": False}[v]
            )
        frame[columns[index]] = values.astype(kind)
    frame.index = pd.Index(
        [_scalar(v) for v in value["index"]],
        dtype=_dtype(value["index_dtype"]),
        name=value["index_name"],
    )
    frame.columns = pd.Index(
        columns, dtype=_dtype(value["columns_dtype"]), name=value["columns_name"]
    )
    return frame


def _daily_performance(daily: pd.DataFrame, summary: dict[str, Any]) -> pd.DataFrame:
    if daily.empty:
        return pd.DataFrame(columns=["period_end", "net_return"])
    performance = daily.rename(
        columns={
            "trade_date": "period_end",
            "executed_return": "raw_executed_return",
            "executed_nav": "raw_executed_nav",
        }
    ).copy()
    evidence = summary.get("daily_return")
    if evidence is None or len(evidence) != len(daily):
        performance["net_return"] = pd.Series([None] * len(daily), dtype=object)
    else:
        performance["net_return"] = pd.Series(
            [None if v is None else float(v) for v in evidence],
            dtype=object,
        )
    return performance


def _receivable_limitation(daily: pd.DataFrame) -> str | None:
    # These are owner-reported states, not a reconstructed financial calculation.
    # The schema's no-action profile omits both receivable columns.
    for name in ("cash_receivable", "stock_receivable_value"):
        if name not in daily:
            continue
        values = pd.to_numeric(daily[name], errors="coerce")
        if not values.map(math.isfinite).all():
            return "unknown_owner_receivables"
        if values.ne(0).any():
            return "unpaid_owner_receivables"
    return None


def _daily_result(result: ProductResult, raw: dict[str, Any] | None) -> CanonicalBacktestResult:
    from quant_platform._portfolio.backends.native import _attach_fill_ids, _attach_order_ids

    wire = cast(dict[str, Any], result_to_json(result))
    tables = {t["name"]: t for t in wire["tables"]}
    summary = wire["summary"]
    if raw is not None:
        if raw.get("schema") != "daily-owner-result.v1":
            raise ValueError("unexpected daily owner result schema")
        owner_tables = {
            key: _owner_frame(value) if value is not None else None
            for key, value in raw["owner_tables"].items()
        }
        if set(raw["owner_unified_ledger"]) != set(UnifiedLedger.__dataclass_fields__):
            raise ValueError("incomplete owner unified ledger schema")
        owner_ledger = UnifiedLedger(
            **{key: _owner_frame(value) for key, value in raw["owner_unified_ledger"].items()}
        )
        daily = owner_tables["daily"]
        daily = daily if daily is not None else pd.DataFrame()
        orders, fills = owner_tables["orders"], owner_tables["fills"]
        if orders is None or fills is None:
            raise ValueError("daily owner reports/fills schema is missing")
    else:
        daily = pd.DataFrame(tables["daily"]["rows"])
        orders = pd.DataFrame(tables["reports"]["rows"])
        fills = pd.DataFrame(tables["fills"]["rows"])
    orders = _attach_order_ids(orders)
    fills = _attach_fill_ids(fills, orders)
    ledger = None
    daily_ledger = pd.DataFrame()
    positions = pd.DataFrame()
    limitation = _receivable_limitation(daily)
    if raw is not None and raw["owner_tables"]["daily"] is not None and limitation is None:
        ledger = replace(owner_ledger, orders=orders, fills=fills)
        daily_ledger = ledger.daily_cash.merge(ledger.daily_positions, on="trade_date").merge(
            ledger.daily_nav, on="trade_date"
        )
        positions = ledger.targets.rename(columns={"target_weight": "weight"})
    complete = ledger is not None and summary.get("valuation_complete") is True
    canonical = CanonicalBacktestResult(
        backend_name=result.provider.backend_id,
        performance=_daily_performance(daily, summary),
        positions=positions,
        capabilities=BackendCapabilities(
            order_lifecycle=True, partial_fills=True, daily_ledger=ledger is not None
        ),
        orders=orders,
        fills=fills,
        daily_ledger=daily_ledger,
        unified_ledger=ledger,
        summary=summary,
        metadata={
            "execution_aware": complete,
            "product_result": wire,
            "raw_return_scope": "historical owner marks; not supported interval evidence",
            "full_owner_artifact_verified": raw is not None,
            "canonical_ledger_limitation": limitation,
            "decision_count": len(raw["decision_clocks"]) if raw is not None else None,
            "owner_result": raw,
        },
    )
    canonical.validate()
    return canonical


def to_canonical_result(
    result: ProductResult,
    *,
    artifact_root: Path | None = None,
) -> CanonicalBacktestResult:
    """Translate evidence; optionally verify the complete relative owner artifact.

    Product DTOs intentionally do not carry a trusted filesystem root. Omitting
    ``artifact_root`` keeps unavailable owner tables unavailable. No cwd lookup,
    network fetch, financial replay or backend fallback occurs.
    """
    if not isinstance(result, ProductResult):
        raise TypeError("result must be a ProductResult")
    if result.status != "completed":
        raise ValueError("only completed product results can be canonicalized")
    raw = None
    if artifact_root is not None:
        if result.raw_result is None:
            raise ValueError("product has no raw owner artifact")
        if result.raw_result.sha256 != result.normalization.source_sha256:
            raise ValueError("normalization and raw artifact digests disagree")
        raw = load_artifact(result.raw_result, artifact_root)
        if not isinstance(raw, dict) or result.normalization.source_schema != raw.get(
            "schema", raw.get("schema_version")
        ):
            raise ValueError("normalization source schema differs from owner artifact")
    if result.provider.backend_id == "python.daily":
        return _daily_result(result, raw)
    if result.provider.backend_id == "rust.nautilus.sessions" and raw is not None:
        from .engine_sessions import _canonical_result

        canonical = _canonical_result(
            raw, result.provider.artifact_sha256 or "", result.provider.source_revision
        )
        return replace(
            canonical,
            summary=to_json_compatible(result_to_json(result)["summary"]),
            metadata={
                **canonical.metadata,
                "product_result": result_to_json(result),
                "execution_aware": False,
            },
        )
    # Other adapters retain their neutral evidence; unknown ledgers are not invented.
    canonical = CanonicalBacktestResult(
        backend_name=result.provider.backend_id,
        performance=pd.DataFrame(columns=["period_end"]),
        positions=pd.DataFrame(),
        capabilities=BackendCapabilities(),
        summary=cast(dict[str, Any], result_to_json(result)["summary"]),
        metadata={"execution_aware": False, "product_result": result_to_json(result)},
    )
    canonical.validate()
    return canonical
