"""Small synthetic assurance artifacts with explicit, independently testable truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

SCENARIO_SCHEMA = "quant.assurance-scenario.v1"
SCENARIO_NAMES = (
    "null_signal",
    "industry_confound",
    "delayed_revision",
    "partial_fill",
    "sequence_gap",
)


@dataclass(frozen=True)
class ScenarioBundle:
    name: str
    seed: int
    frames: dict[str, pd.DataFrame]
    truth: dict[str, object]


def build_scenario(name: str, *, seed: int = 0) -> ScenarioBundle:
    if name not in SCENARIO_NAMES or type(seed) is not int or seed < 0:
        raise ValueError("known scenario and non-negative integer seed required")
    rng = np.random.default_rng(seed)
    truth: dict[str, object]
    if name in {"null_signal", "industry_confound"}:
        scale = int(rng.integers(1, 1000))
        frame = pd.DataFrame(
            {
                "trade_date": ["2024-01-02"] * 4,
                "symbol": ["SYN_A", "SYN_B", "SYN_C", "SYN_D"],
                "industry": [0, 0, 1, 1],
                "prediction": np.array([-1, 1, -1, 1], dtype=float) * scale,
                "return": np.array([-1, -1, 1, 1], dtype=float) / 64,
            }
        )
        if name == "industry_confound":
            frame["prediction"] = frame["industry"].astype(float) * scale
        truth = (
            {"covariance": 0.0}
            if name == "null_signal"
            else {"return_source": "industry_only", "neutralized_prediction_variance": 0.0}
        )
        frames = {"signals": frame}
    elif name == "delayed_revision":
        frames = {
            "revisions": pd.DataFrame(
                {
                    "symbol": ["SYN_A", "SYN_A"],
                    "event_at": ["2024-01-01T00:00:00+00:00"] * 2,
                    "available_at": ["2024-01-02T12:00:00+00:00", "2024-01-04T12:00:00+00:00"],
                    "revision": [1, 2],
                    "value": [10.0, 99.0],
                }
            )
        }
        truth = {"before_publication_rows": 0, "initial_value": 10.0, "corrected_value": 99.0}
    elif name == "partial_fill":
        frames = {
            "fills": pd.DataFrame(
                {
                    "trade_date": ["2024-01-02"],
                    "instrument_id": ["SYN_A"],
                    "side": ["buy"],
                    "filled_notional": [660.0],
                    "average_fill_price": [11.0],
                }
            ),
            "marks": pd.DataFrame(
                {
                    "trade_date": ["2024-01-02"],
                    "instrument_id": ["SYN_A"],
                    "price": [12.0],
                }
            ),
        }
        truth = {
            "requested_quantity": 100.0,
            "filled_quantity": 60.0,
            "decision_price": 10.0,
            "unfilled_price": 12.0,
            "fees": 5.0,
            "shortfall_cash": 145.0,
            "initial_capital": 1000.0,
            "cash_end_before_fees": 340.0,
            "market_value_end": 720.0,
        }
    else:
        frames = {
            "events": pd.DataFrame(
                {
                    "time_ms": [100, 100],
                    "kind": ["order", "cancel"],
                    "order_id": ["SYN_A", "SYN_A"],
                    "channel": ["1", "1"],
                    "sequence": [1, 3],
                    "source_index": [0, 1],
                }
            )
        }
        truth = {"missing_sequences": [2], "complete": False}
    return ScenarioBundle(name, seed, frames, truth)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_scenario(bundle: ScenarioBundle, destination: Path) -> Path:
    """Create a new artifact directory; manifest is written after all inputs."""
    if bundle.name not in SCENARIO_NAMES or type(bundle.seed) is not int or bundle.seed < 0:
        raise ValueError("invalid scenario identity")
    inventory = []
    contents: dict[str, bytes] = {}
    for key, frame in sorted(bundle.frames.items()):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or frame.columns.has_duplicates:
            raise ValueError("invalid frame identity or duplicate columns")
        dtypes = {str(col): str(dtype) for col, dtype in frame.dtypes.items()}
        if not dtypes or not all(
            dtype in {"object", "str", "float64", "int64", "bool"} for dtype in dtypes.values()
        ):
            raise ValueError("unsupported scenario column type")
        data = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
        relative = f"{key}.csv"
        contents[relative] = data
        inventory.append(
            {
                "name": key,
                "path": relative,
                "sha256": _digest(data),
                "rows": len(frame),
                "dtypes": dtypes,
            }
        )
    if not inventory:
        raise ValueError("scenario must have input frames")
    manifest = {
        "schema_version": SCENARIO_SCHEMA,
        "name": bundle.name,
        "seed": bundle.seed,
        "truth": bundle.truth,
        "inventory": inventory,
    }
    encoded = json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False).encode("utf-8")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for relative, data in contents.items():
        (destination / relative).write_bytes(data)
    path = destination / "manifest.json"
    path.write_bytes(encoded + b"\n")
    return path


def read_scenario(manifest: Path) -> ScenarioBundle:
    manifest = Path(manifest).resolve()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != SCENARIO_SCHEMA
        or payload.get("name") not in SCENARIO_NAMES
        or type(payload.get("seed")) is not int
        or payload["seed"] < 0
        or not isinstance(payload.get("truth"), dict)
        or not isinstance(payload.get("inventory"), list)
        or not payload["inventory"]
    ):
        raise ValueError("invalid scenario manifest")
    frames: dict[str, pd.DataFrame] = {}
    paths: set[Path] = set()
    for item in payload["inventory"]:
        if not isinstance(item, dict):
            raise ValueError("invalid inventory entry")
        key, relative, dtypes = item.get("name"), item.get("path"), item.get("dtypes")
        if (
            not isinstance(key, str)
            or not re.fullmatch(r"[a-z][a-z0-9_]*", key)
            or not isinstance(relative, str)
            or relative != f"{key}.csv"
            or key in frames
            or not isinstance(dtypes, dict)
            or not dtypes
            or not all(
                isinstance(col, str) and dtype in {"object", "str", "float64", "int64", "bool"}
                for col, dtype in dtypes.items()
            )
        ):
            raise ValueError("invalid or duplicate inventory identity")
        source = (manifest.parent / relative).resolve()
        if not source.is_relative_to(manifest.parent) or source in paths:
            raise ValueError("scenario path escapes root or repeats")
        paths.add(source)
        if _digest(source.read_bytes()) != item.get("sha256"):
            raise ValueError("scenario input hash mismatch")
        frame = pd.read_csv(source, dtype=dtypes)
        if set(frame.columns) != set(dtypes) or len(frame) != item.get("rows"):
            raise ValueError("scenario frame shape differs from manifest")
        frames[key] = frame
    return ScenarioBundle(payload["name"], payload["seed"], frames, payload["truth"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", choices=SCENARIO_NAMES)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(write_scenario(build_scenario(args.name, seed=args.seed), args.output))


if __name__ == "__main__":
    main()
