"""Export a generic holdings payload as execution targets.

The exporter deliberately accepts an owner-produced JSON payload.  It does not
load strategy configuration, research code, provider data, or broker clients.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _execution_symbol(value: object, market: object | None) -> tuple[str, str]:
    symbol = str(value).strip().upper()
    if not symbol:
        raise ValueError("target symbol must be non-empty")
    suffix_map = {
        ".SH": "CN",
        ".SZ": "CN",
        ".BJ": "CN",
        ".XSHG": "CN",
        ".XSHE": "CN",
    }
    for suffix, normalized_market in suffix_map.items():
        if symbol.endswith(suffix):
            return symbol[: -len(suffix)], normalized_market
    normalized_market = str(market or "").strip().upper()
    if not normalized_market:
        raise ValueError(f"market is required for symbol {symbol}")
    return symbol, normalized_market


def _load_holdings(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        payload = {"holdings": payload}
    if not isinstance(payload, dict):
        raise TypeError("holdings payload must be an object or an array")
    rows = payload.get("holdings")
    if not isinstance(rows, list) or not rows:
        raise ValueError("holdings payload must contain a non-empty holdings array")
    return payload


def _target_rows(payload: dict[str, Any]) -> tuple[list[dict[str, object]], str]:
    rows = payload["holdings"]
    default_market = payload.get("market")
    result: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    total = 0.0
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("every holding must be an object")
        if str(row.get("side", "long")).lower() != "long":
            raise ValueError("export-targets only supports long-only holdings")
        try:
            weight = float(row["weight"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("every holding requires a numeric weight") from exc
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("target weights must be finite and non-negative")
        symbol, market = _execution_symbol(
            row.get("symbol"), row.get("market", default_market)
        )
        key = (symbol, market)
        if key in seen:
            raise ValueError(f"duplicate execution target for {symbol}.{market}")
        seen.add(key)
        total += weight
        result.append({"symbol": symbol, "market": market, "target_weight": weight})
    if total <= 0 or total > 1.0 + 1e-8:
        raise ValueError("target weights must sum to a value in (0, 1]")
    markets = ",".join(sorted({market for _, market in seen}))
    return result, markets


def export_targets(
    holdings_path: str | Path,
    output_path: str | Path,
    *,
    lineage_path: str | Path | None = None,
    source: str = "strategy-pipeline",
) -> Path:
    """Write canonical targets JSON and return the lineage sidecar path."""

    holdings_file = Path(holdings_path)
    targets_file = Path(output_path)
    payload = _load_holdings(holdings_file)
    targets, markets = _target_rows(payload)
    total = sum(float(target["target_weight"]) for target in targets)
    gross_exposure = 0.99 if markets == "CN" else 1.0
    result = {
        "asof": payload.get("as_of"),
        "source": source,
        "target_gross_exposure": gross_exposure,
        "targets": targets,
    }
    targets_file.parent.mkdir(parents=True, exist_ok=True)
    targets_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    sidecar = (
        Path(lineage_path)
        if lineage_path
        else targets_file.with_suffix(".json.lineage.json")
    )
    content_sha256 = hashlib.sha256(targets_file.read_bytes()).hexdigest()
    run_id = str(payload.get("run_id", holdings_file.stem))
    configuration = {"source": source, "holdings_path": str(holdings_file)}
    lineage = {
        "run_id": run_id,
        "source": source,
        "holdings_file": str(holdings_file),
        "target_count": len(targets),
        "markets": markets,
        "weight_sum": total,
        "content_sha256": content_sha256,
        "artifact_envelope": {
            "schema_version": "research.artifact-envelope.v2",
            "artifact_id": f"targets:{run_id}",
            "artifact_type": "targets.json",
            "run_id": run_id,
            "created_at": datetime.now(UTC).isoformat(),
            "producer": {
                "repository": "strategy-pipeline",
                "version": "0.1.0",
                "commit": "unknown",
                "backend": "export_targets",
            },
            "configuration_sha256": hashlib.sha256(
                json.dumps(
                    configuration, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "content_sha256": content_sha256,
            "lineage": [
                {
                    "artifact_id": "owner.holdings.json",
                    "sha256": hashlib.sha256(holdings_file.read_bytes()).hexdigest(),
                }
            ],
        },
    }
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(
        json.dumps(lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return sidecar
