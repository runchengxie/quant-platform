"""Recoverable bar execution with conservative delayed financial snapshots.

Uses the existing minute matcher and ledger. No queue model or network cancel
latency is added. Quotes remain external and undelivered reports prohibit new
orders, regardless of policy behavior. Corporate actions and valuation events
are outside this initial session API.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pandas as pd

from quant_platform._portfolio.minute_execution import _MinuteSimulation

from .impact import LinearImpact

_FIELDS = [
    "cash",
    "holdings",
    "bought",
    "marks",
    "orders",
    "fills",
    "daily",
    "costs",
    "mark_days",
    "mark_times",
    "mark_source_times",
    "mark_basis",
    "adjusted_ex_dates",
    "holdings_ledger",
    "clipped_vwap_bars",
    "current_day",
    "day_has_events",
    "current_time",
    "policy_snapshots",
]


def _wire(value):
    if isinstance(value, pd.Timestamp):
        return {
            "type": "timestamp",
            "value": value.isoformat(),
            "zone": str(value.tz) if value.tz else None,
        }
    if isinstance(value, date):
        return {"type": "date", "value": value.isoformat()}
    if isinstance(value, pd.DataFrame):
        return {"type": "frame", "value": _wire(value.to_dict("list"))}
    if isinstance(value, dict):
        return {"type": "dict", "value": [[_wire(k), _wire(v)] for k, v in value.items()]}
    if isinstance(value, (set, tuple)):
        return {
            "type": "set" if isinstance(value, set) else "tuple",
            "value": [_wire(v) for v in sorted(value) if isinstance(value, set)]
            if isinstance(value, set)
            else [_wire(v) for v in value],
        }
    if isinstance(value, list):
        return [_wire(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return {"type": "nonfinite", "value": repr(value)}
    return value


def _unwire(value):
    if isinstance(value, list):
        return [_unwire(v) for v in value]
    if not isinstance(value, dict):
        return value
    kind, data = value["type"], value["value"]
    if kind == "dict":
        return {_unwire(k): _unwire(v) for k, v in data}
    if kind == "timestamp":
        return (
            pd.Timestamp(data).tz_convert(value["zone"])
            if value.get("zone")
            else pd.Timestamp(data)
        )
    if kind == "date":
        return date.fromisoformat(data)
    if kind == "frame":
        return pd.DataFrame(_unwire(data))
    if kind == "nonfinite":
        if data not in {"nan", "inf", "-inf"}:
            raise ValueError("invalid nonfinite encoding")
        return float(data)
    if kind in {"set", "tuple"}:
        return set(_unwire(data)) if kind == "set" else tuple(_unwire(data))
    raise ValueError("unknown checkpoint type")


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def _binding(targets, bars, config, policy):
    return _digest(
        {
            "targets": targets.to_json(date_format="iso", date_unit="ns"),
            "bars": bars.to_json(date_format="iso", date_unit="ns"),
            "config": asdict(config),
            "policy_type": type(policy).__module__ + "." + type(policy).__qualname__,
            "policy_source": hashlib.sha256(
                Path(inspect.getfile(type(policy))).read_bytes()
            ).hexdigest(),
            "source": {
                str(Path(p).name): hashlib.sha256(Path(p).read_bytes()).hexdigest()
                for p in (
                    __file__,
                    inspect.getfile(_MinuteSimulation),
                    inspect.getfile(LinearImpact),
                )
            },
        }
    )


class MinuteSession:
    """Policy must implement checkpoint(); caller restores its own policy type.

    Checkpoints contain financial state and bind exact inputs, configuration and
    loaded source. Digests detect accidental modification, not malicious authors.
    Deliveries are a causal prefix. Economic fills and T+1 remain owner behavior.
    """

    def __init__(self, targets, bars, config, *, policy, report_delay_seconds=0, impact=None):
        if impact is not None and type(impact) is not LinearImpact:
            raise ValueError("recoverable session requires exact LinearImpact type")
        if not math.isfinite(report_delay_seconds) or report_delay_seconds < 0:
            raise ValueError("finite nonnegative report delay required")
        self.targets, self.bars, self.config = targets.copy(), bars.copy(), config
        self.policy = policy
        self.delay = report_delay_seconds
        self.binding = _binding(targets, bars, config, policy)
        self.cursor, self.finished = 0, False
        self.queue = []
        self.simulation = _MinuteSimulation(self.targets, self.bars, config, (), ())
        self.simulation.decision_policy = self._decide
        self.simulation.impact_model = impact
        self.simulation.times = sorted(set(self.simulation.times) | set(self.simulation.decisions))
        self.delivered: dict[str, Any] = {
            "cash": config.initial_cash,
            "holdings": {},
            "pending_orders": (),
        }
        self.trace = []

    def _decide(self, state, proposed):
        pending = self.delivered["pending_orders"]
        if self.queue:
            pending = (
                *pending,
                {"status": "undelivered_financial_report", "remaining_quantity": 0},
            )
        holdings = self.delivered["holdings"]
        nav = self.delivered["cash"] + sum(q * state.marks[s] for s, q in holdings.items())
        visible = replace(
            state,
            cash=self.delivered["cash"],
            nav=nav,
            holdings=MappingProxyType(dict(holdings)),
            pending_orders=tuple(MappingProxyType(dict(order)) for order in pending),
        )
        weights = self.policy(visible, proposed)
        self.trace.append(
            {
                "time": state.time.isoformat(),
                "visible_cash": visible.cash,
                "visible_holdings": dict(visible.holdings),
                "undelivered_reports": len(self.queue),
                "action": "wait_reports" if self.queue else "policy",
            }
        )
        return None if self.queue else weights

    def _snapshot(self):
        sim = self.simulation
        return {
            "cash": sim.cash,
            "holdings": dict(sim.holdings),
            "pending_orders": tuple(
                {**o, "remaining_quantity": o["quantity"] - o["filled_quantity"]}
                for o in sim.pending
                if o["status"] == "pending"
            ),
        }

    def _deliver(self, time):
        while self.queue and self.queue[0][0] <= time:
            _, self.delivered = self.queue.pop(0)

    def step(self):
        if self.finished:
            raise ValueError("session already finished")
        sim = self.simulation
        if self.cursor == len(sim.times):
            return False
        time = sim.times[self.cursor]
        before = self._snapshot()
        sim.advance_account(time)
        self._deliver(time)
        if not self.delay:
            self.delivered = self._snapshot()
        if time in sim.grouped or time in sim.snapshots:
            sim.day_has_events = True
        if time in sim.decisions:
            sim.decide(time)
        if time in sim.snapshots:
            if self.queue:
                sim.policy_snapshots[time] = None
            sim.rebalance(time)
        if time in sim.grouped:
            sim.process_bars(time)
        after = self._snapshot()
        if before != after:
            self.queue.append((time + pd.Timedelta(seconds=self.delay), after))
        self._deliver(time)
        self.cursor += 1
        return True

    def run(self):
        while self.step():
            pass
        result = self.simulation.finish()
        self.finished = True
        result.summary.update(
            account_delivery="causal_prefix_delayed_snapshots",
            report_delay_seconds=self.delay,
            cancellation="synchronous_exchange_delayed_acknowledgement",
            financial_reports_pending=len(self.queue),
        )
        return result

    def checkpoint(self):
        if self.finished:
            raise ValueError("cannot checkpoint a finished session")
        sim = self.simulation
        state = {key: getattr(sim, key) for key in _FIELDS if hasattr(sim, key)}
        value = {
            "schema": "minute-session.v1",
            "binding": self.binding,
            "cursor": self.cursor,
            "delay": self.delay,
            "policy": json.loads(json.dumps(self.policy.checkpoint(), allow_nan=False)),
            "impact": sim.impact_model.checkpoint() if sim.impact_model else None,
            "state": _wire(state),
            "delivery": _wire([self.delivered, self.queue, self.trace]),
        }
        return {**value, "digest": _digest(value)}

    @classmethod
    def restore(cls, targets, bars, config, checkpoint, *, policy):
        value = dict(checkpoint)
        digest = value.pop("digest", None)
        if value.get("schema") != "minute-session.v1" or digest != _digest(value):
            raise ValueError("checkpoint integrity mismatch")
        result = cls(
            targets,
            bars,
            config,
            policy=policy,
            report_delay_seconds=value["delay"],
            impact=LinearImpact.restore(value["impact"]) if value["impact"] else None,
        )
        if (
            result.binding != value["binding"]
            or json.loads(json.dumps(policy.checkpoint(), allow_nan=False)) != value["policy"]
        ):
            raise ValueError("checkpoint source/input/policy binding mismatch")
        if type(value["cursor"]) is not int or not 0 <= value["cursor"] <= len(
            result.simulation.times
        ):
            raise ValueError("invalid checkpoint cursor")
        for key, item in _unwire(value["state"]).items():
            if key not in _FIELDS:
                raise ValueError("invalid checkpoint field")
            setattr(result.simulation, key, item)
        result.simulation.pending = [
            o for o in result.simulation.orders if o["status"] == "pending"
        ]
        result.delivered, result.queue, result.trace = _unwire(value["delivery"])
        result.cursor = value["cursor"]
        return result
