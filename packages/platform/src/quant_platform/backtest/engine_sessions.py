"""Map independent engine wire evidence to platform analysis tables.

The engine-owned SDK handles executable verification, subprocesses and protocol
validation. This module only converts its validated result, without simulating
orders, planning quantities or claiming a complete execution-aware ledger.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from pathlib import Path

import pandas as pd

try:
    from quant_backtest_engine import EngineClient as WireEngineClient
    from quant_backtest_engine import EngineProtocolError as EngineProtocolError
except ModuleNotFoundError as error:
    if error.name != "quant_backtest_engine":
        raise
    raise ImportError(
        "Install quant-platform[engine] to use the independent engine adapter"
    ) from error

from .contracts import BackendCapabilities, CanonicalBacktestResult


class EngineClient:
    """Compatibility client returning platform tables from validated session JSON."""

    def __init__(
        self,
        executable: Path,
        sha256: str,
        *,
        timeout: float = 30,
        source_revision: str | None = None,
    ) -> None:
        selected = WireEngineClient(
            executable, sha256, timeout=timeout, source_revision=source_revision
        )
        self.executable = selected.executable
        self.sha256 = selected.sha256
        self.timeout = selected.timeout
        self.source_revision = selected.source_revision

    def _client(self) -> WireEngineClient:
        return WireEngineClient(
            self.executable, self.sha256, timeout=self.timeout, source_revision=self.source_revision
        )

    def size(self, request: dict) -> dict:
        return self._client().size(request)

    def run_sessions(self, request: dict) -> CanonicalBacktestResult:
        result = self._client().run_sessions(request)
        return _canonical_result(result, self.sha256, self.source_revision)


def _canonical_result(
    result: dict, executable_sha256: str, source_revision: str | None
) -> CanonicalBacktestResult:
    daily_rows = [
        {
            **row,
            "trade_date": row["session_date"],
            **{
                key: float(Decimal(row[key]))
                for key in ("cash", "positions_value", "nav", "commission")
            },
        }
        for row in result["daily_ledger"]
    ]
    nav_by_date = {row["session_date"]: Decimal(row["nav"]) for row in result["daily_ledger"]}
    with localcontext() as context:
        context.prec = 64
        position_rows = [
            {
                **row,
                "rebalance_date": row["session_date"],
                "weight": float(Decimal(row["market_value"]) / nav_by_date[row["session_date"]])
                if nav_by_date[row["session_date"]]
                else 0.0,
            }
            for row in result["daily_positions"]
        ]
    rejections = {row["order_id"]: row for row in result["rejections"]}
    canonical = CanonicalBacktestResult(
        backend_name="independent_engine_sessions",
        performance=pd.DataFrame(
            [{"period_end": r["trade_date"], "nav": r["nav"]} for r in daily_rows]
        ),
        positions=pd.DataFrame(position_rows),
        capabilities=BackendCapabilities(
            order_lifecycle=True,
            partial_fills=True,
            daily_ledger=True,
            market_rules=tuple(
                c
                for c in result["capabilities"]
                if c != "configured_t_plus_one" or result["enforce_t1"]
            ),
        ),
        orders=pd.DataFrame(
            [
                {**row, "order_id": row["id"], "rejection": rejections.get(row["id"])}
                for row in result["orders"]
            ]
        ),
        fills=pd.DataFrame(
            [{**row, "fill_id": f"engine-fill-{i}"} for i, row in enumerate(result["fills"])]
        ),
        daily_ledger=pd.DataFrame(daily_rows),
        summary={key: result[key] for key in ("final_cash", "final_nav", "total_commission")},
        metadata={
            "engine_result": result,
            "executable_sha256": executable_sha256,
            "source_revision": source_revision,
            "execution_aware": False,
        },
    )
    canonical.validate()
    return canonical
