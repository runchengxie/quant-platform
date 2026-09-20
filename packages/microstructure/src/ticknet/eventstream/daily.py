"""Pure NumPy aggregation of packed L2 events into a daily state."""

from __future__ import annotations

import numpy as np


DAILY_STATE_KEYS = (
    "order_count",
    "trade_count",
    "snapshot_count",
    "total_event_count",
    "event_duration_hours",
    "event_rate_per_hour",
    "trade_amount",
    "signed_trade_amount",
    "signed_trade_ratio",
    "realized_variance",
    "upside_semivariance",
    "downside_semivariance",
    "snapshot_return",
    "snapshot_return_observations",
    "price_impact_per_turnover",
    "price_impact_observations",
    "spread_bps_mean",
    "spread_bps_observations",
    "depth_mean",
    "depth_observations",
    "l1_imbalance_mean",
    "l1_imbalance_observations",
    "early_signed_trade_amount",
    "late_signed_trade_amount",
    "early_snapshot_return",
    "late_snapshot_return",
    "last_snapshot_to_final_return",
    "recovery_observations",
)


def _finite_or_zero(value: float) -> float:
    value = float(value)
    return value if np.isfinite(value) else 0.0


def _safe_mean(values: np.ndarray) -> tuple[float, float]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 0.0, 0.0
    return _finite_or_zero(np.mean(finite)), float(finite.size)


def _global_timestamps(order: np.ndarray, trade: np.ndarray, snap: np.ndarray) -> np.ndarray:
    parts = [values["time_ms"].astype(np.int64, copy=False) for values in (order, trade, snap) if len(values)]
    if not parts:
        return np.empty(0, dtype=np.int64)
    return np.concatenate(parts)


def _ordered_snapshots(snap: np.ndarray) -> np.ndarray:
    if len(snap) < 2:
        return snap
    return snap[np.argsort(snap["time_ms"], kind="stable")]


def _snapshot_returns(snap: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ordered = _ordered_snapshots(snap)
    if len(ordered) < 2:
        return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.int64)
    prices = ordered["last"].astype(np.float64)
    valid = (prices[:-1] > 0) & (prices[1:] > 0)
    returns = prices[1:] / prices[:-1] - 1.0
    return returns[valid], ordered["time_ms"][1:][valid].astype(np.int64)


def _path_return(prices: np.ndarray) -> float:
    valid = prices[np.isfinite(prices) & (prices > 0)]
    if len(valid) < 2:
        return 0.0
    return _finite_or_zero(valid[-1] / valid[0] - 1.0)


def _split_snapshot_returns(snap: np.ndarray, split: float) -> tuple[float, float]:
    ordered = _ordered_snapshots(snap)
    if not len(ordered):
        return 0.0, 0.0
    times = ordered["time_ms"].astype(np.float64)
    prices = ordered["last"].astype(np.float64)
    early = prices[times <= split]
    late = prices[times > split]
    if len(early) and len(late):
        late = np.concatenate(([early[-1]], late))
    return _path_return(early), _path_return(late)


def _final_observed_price(order: np.ndarray, trade: np.ndarray, snap: np.ndarray) -> tuple[float, float]:
    candidates: list[tuple[int, float]] = []
    for values, field in ((order, "price"), (trade, "price"), (snap, "last")):
        for time_ms, price in zip(values["time_ms"], values[field], strict=False):
            if float(price) > 0:
                candidates.append((int(time_ms), float(price)))
    if not candidates:
        return 0.0, 0.0
    time_ms, price = max(candidates, key=lambda item: item[0])
    return price, float(time_ms)


def aggregate_day(
    order: np.ndarray,
    trade: np.ndarray,
    snap: np.ndarray,
    prev_close_cent: float,
) -> dict[str, float]:
    """Aggregate one packed trading day into a finite named state vector."""
    state = {key: 0.0 for key in DAILY_STATE_KEYS}
    state["order_count"] = float(len(order))
    state["trade_count"] = float(len(trade))
    state["snapshot_count"] = float(len(snap))
    state["total_event_count"] = state["order_count"] + state["trade_count"] + state["snapshot_count"]

    timestamps = _global_timestamps(order, trade, snap)
    if len(timestamps):
        duration_ms = int(timestamps.max()) - int(timestamps.min())
        state["event_duration_hours"] = _finite_or_zero(duration_ms / 3_600_000.0)
        if duration_ms > 0:
            state["event_rate_per_hour"] = _finite_or_zero(
                state["total_event_count"] / state["event_duration_hours"]
            )
        split = float(np.median(timestamps))
    else:
        split = 0.0

    if len(trade):
        volumes = np.maximum(trade["volume"].astype(np.float64), 0.0)
        signed_side = np.sign(trade["side"].astype(np.float64))
        state["trade_amount"] = _finite_or_zero(volumes.sum())
        state["signed_trade_amount"] = _finite_or_zero((volumes * signed_side).sum())
        if state["trade_amount"] > 0:
            state["signed_trade_ratio"] = _finite_or_zero(
                state["signed_trade_amount"] / state["trade_amount"]
            )
        trade_times = trade["time_ms"].astype(np.float64)
        signed_amount = volumes * signed_side
        state["early_signed_trade_amount"] = _finite_or_zero(signed_amount[trade_times <= split].sum())
        state["late_signed_trade_amount"] = _finite_or_zero(signed_amount[trade_times > split].sum())

    returns, _return_times = _snapshot_returns(snap)
    if len(returns):
        state["realized_variance"] = _finite_or_zero(np.square(returns).sum())
        state["upside_semivariance"] = _finite_or_zero(np.square(returns[returns > 0]).sum())
        state["downside_semivariance"] = _finite_or_zero(np.square(returns[returns < 0]).sum())
        state["price_impact_observations"] = float(len(returns))
        turnover = np.maximum(_ordered_snapshots(snap)["d_turnover"].astype(np.float64), 0.0).sum()
        if turnover > 0:
            state["price_impact_per_turnover"] = _finite_or_zero(np.abs(returns).sum() / turnover)

    ordered_snap = _ordered_snapshots(snap)
    if len(ordered_snap):
        prices = ordered_snap["last"].astype(np.float64)
        valid_prices = prices[prices > 0]
        if len(valid_prices) and np.isfinite(prev_close_cent) and prev_close_cent > 0:
            state["snapshot_return"] = _finite_or_zero(valid_prices[-1] / prev_close_cent - 1.0)
            state["snapshot_return_observations"] = 1.0

        bid = ordered_snap["bid_px"][:, 0].astype(np.float64)
        ask = ordered_snap["ask_px"][:, 0].astype(np.float64)
        mid = (bid + ask) / 2.0
        spread = np.divide((ask - bid) * 10_000.0, mid, out=np.full_like(mid, np.nan), where=mid > 0)
        state["spread_bps_mean"], state["spread_bps_observations"] = _safe_mean(spread)

        bid_depth = np.maximum(ordered_snap["total_bidvol"].astype(np.float64), 0.0)
        ask_depth = np.maximum(ordered_snap["total_askvol"].astype(np.float64), 0.0)
        depth, depth_count = _safe_mean(bid_depth + ask_depth)
        state["depth_mean"] = depth
        state["depth_observations"] = depth_count
        imbalance = np.divide(
            bid_depth - ask_depth,
            bid_depth + ask_depth,
            out=np.full_like(bid_depth, np.nan),
            where=(bid_depth + ask_depth) > 0,
        )
        state["l1_imbalance_mean"], state["l1_imbalance_observations"] = _safe_mean(imbalance)
        state["early_snapshot_return"], state["late_snapshot_return"] = _split_snapshot_returns(snap, split)

        final_price, _final_time = _final_observed_price(order, trade, snap)
        last_price = valid_prices[-1] if len(valid_prices) else 0.0
        if last_price > 0 and final_price > 0:
            state["last_snapshot_to_final_return"] = _finite_or_zero(final_price / last_price - 1.0)
            state["recovery_observations"] = 1.0

    return {key: _finite_or_zero(state[key]) for key in DAILY_STATE_KEYS}
