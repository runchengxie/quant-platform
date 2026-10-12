"""按交易日把 L2 三条原始流打包成无损整数镜像。

每天产出（dtype 契约见 ``config.py``）：
    orders_{day}.bin  按 (ticker, time_ms, OrderID) 排序
    trades_{day}.bin  按 (ticker, time_ms, DealID) 排序
    snaps_{day}.bin   按 (ticker, time_ms) 排序
    index_{day}.npz   每股票三流偏移/长度 + prev_close

ID 关联在打包时就地解析（现在便宜，之后贵）：
    - 撤单订单（OrderType -1/-11）按 (ticker, OrderID) 回链原始订单，得
      cancel_age_ms / cancel_orig_vol
    - 成交按 BuyID/SellID 回链订单到达时间，得 buy/sell_age_ms
不可解析的关联（例如盘前订单）记 AGE_UNKNOWN_MS = -1。

快照输入是月度整文件（``snapshot_{yyyymm}.parquet``），打包时按 TradingDay
过滤出当日行，无需先做逐日重分片。

用法：
    python -m ticknet.eventstream.pack --start 20210104 --end 20210108
    python -m ticknet.eventstream.pack --days 20210104 --universe universe_top.json
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import numpy as np
import polars as pl
from numpy.typing import NDArray

from ticknet.eventstream.config import (
    AGE_UNKNOWN_MS,
    MARKET_END_MS,
    N_LEVELS,
    ORDER_DTYPE,
    PACK_ROOT,
    RAW_L2_ROOT,
    SESSION_START_MS,
    SNAP_DTYPE,
    TRADE_DTYPE,
    day_input_files,
    day_is_packed,
    day_pack_paths,
)

CANCEL_TYPES = (-1, -11)
UniverseSpec = list[str] | dict[int, list[str]]


def _validate_symbols(raw: object, *, context: str) -> list[str]:
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{context} 应为非空股票字符串列表")
    symbols: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise ValueError(f"{context} 应为非空股票字符串列表")
        symbols.append(item)
    if len(set(symbols)) != len(symbols):
        raise ValueError(f"{context} 不能包含重复股票")
    return symbols


def _load_universe(path: Path | None) -> UniverseSpec | None:
    if path is None or not Path(path).exists():
        return None
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return _validate_symbols(raw, context="universe")
    if isinstance(raw, Mapping) and "universes" in raw:
        raw = raw["universes"]
    if not isinstance(raw, Mapping) or not raw:
        raise ValueError("universe 应为股票列表或按交易日映射")
    universes: dict[int, list[str]] = {}
    for day, symbols in raw.items():
        try:
            parsed_day = int(day)
        except (TypeError, ValueError) as error:
            raise ValueError(f"universe 交易日无效：{day!r}") from error
        universes[parsed_day] = _validate_symbols(symbols, context=f"universe[{day}]")
    return universes


def _universe_for_day(universe: UniverseSpec | None, day: int) -> list[str] | None:
    if universe is None or isinstance(universe, list):
        return universe
    return universe.get(int(day))


def _load_prev_close(day: int, tickers: list[str], raw_root: Path) -> NDArray[Any]:
    """basic/close_data.parquet 宽表里 day 之前的最近一个收盘价（元）。"""
    import pyarrow.parquet as pq

    table = pq.read_table(raw_root / "basic" / "close_data.parquet")
    dates = np.asarray(table.column("value").to_pylist(), dtype=np.int64)
    prior_rows = np.nonzero(dates < day)[0]
    out = np.zeros(len(tickers), dtype=np.float64)
    if prior_rows.size == 0:
        return out
    for i, ticker in enumerate(tickers):
        if ticker not in table.column_names:
            continue
        column = table.column(ticker)
        for row in reversed(prior_rows):
            value = column[int(row)].as_py()
            if value is None:
                continue
            close = float(value)
            if np.isfinite(close) and close > 0.0:
                out[i] = close
                break
    return out


def _f32(col: str) -> pl.Expr:
    return pl.col(col).cast(pl.Float32, strict=False).fill_null(0.0)


def _ticker_groups(frame: pl.DataFrame) -> dict[str, tuple[int, int]]:
    """对已按 ticker 排序的帧返回每个 ticker 的连续 (offset, length)。

    用 Rust 端 group_by count（秒级），避免对亿级 Python 字符串做 np.unique。
    """
    counts = frame.group_by("ticker", maintain_order=True).len()
    names = counts["ticker"].cast(pl.Utf8).to_list()
    lens = counts["len"].to_numpy().astype(np.int64)
    offs = np.concatenate([[0], np.cumsum(lens)[:-1]])
    return {t: (int(o), int(c)) for t, o, c in zip(names, offs, lens, strict=True)}


def _load_day_frames(
    day: int,
    paths: Mapping[str, Path],
    universe: list[str] | None,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    time_ok = (pl.col("time_ms") >= SESSION_START_MS) & (pl.col("time_ms") < MARKET_END_MS)
    uni_filter = pl.col("ticker").is_in(universe) if universe is not None else pl.lit(True)
    orders = (
        pl.scan_parquet(paths["order"])
        .filter(time_ok & uni_filter)
        .with_columns(pl.col("ticker").cast(pl.Categorical), pl.col("OrderType").cast(pl.Int16))
        .collect()
    )
    is_cancel = pl.col("OrderType").is_in(CANCEL_TYPES)
    adds = orders.filter(~is_cancel).select(
        "ticker",
        "OrderID",
        pl.col("time_ms").alias("orig_time"),
        pl.col("Volume").alias("orig_vol"),
    )
    orders = (
        orders.join(adds, on=["ticker", "OrderID"], how="left")
        .with_columns(
            pl.when(is_cancel & pl.col("orig_time").is_not_null())
            .then(pl.col("time_ms") - pl.col("orig_time"))
            .when(is_cancel)
            .then(pl.lit(AGE_UNKNOWN_MS))
            .otherwise(0)
            .cast(pl.Int32)
            .alias("cancel_age_ms"),
            pl.when(is_cancel)
            .then(pl.col("orig_vol").fill_null(0))
            .otherwise(0)
            .cast(pl.Int32)
            .alias("cancel_orig_vol"),
        )
        .sort(["ticker", "time_ms", "OrderID"])
    )

    trades = (
        pl.scan_parquet(paths["trades"])
        .filter(time_ok & uni_filter)
        .with_columns(pl.col("ticker").cast(pl.Categorical))
        .collect()
    )
    arrivals = adds.select("ticker", "OrderID", "orig_time")
    trades = (
        trades.join(
            arrivals.rename({"OrderID": "BuyID", "orig_time": "buy_time"}),
            on=["ticker", "BuyID"],
            how="left",
        )
        .join(
            arrivals.rename({"OrderID": "SellID", "orig_time": "sell_time"}),
            on=["ticker", "SellID"],
            how="left",
        )
        .with_columns(
            (pl.col("time_ms") - pl.col("buy_time"))
            .fill_null(AGE_UNKNOWN_MS)
            .cast(pl.Int32)
            .alias("buy_age_ms"),
            (pl.col("time_ms") - pl.col("sell_time"))
            .fill_null(AGE_UNKNOWN_MS)
            .cast(pl.Int32)
            .alias("sell_age_ms"),
        )
        .sort(["ticker", "time_ms", "DealID"])
    )
    del adds, arrivals
    gc.collect()

    snaps = (
        pl.scan_parquet(paths["snap"])
        .filter((pl.col("TradingDay") == int(day)) & time_ok & uni_filter)
        .with_columns(pl.col("ticker").cast(pl.Categorical))
        .sort(["ticker", "time_ms"])
        .with_columns(
            pl.col("Volume").diff().over("ticker").fill_null(pl.col("Volume")).alias("d_volume"),
            pl.col("Turnover")
            .diff()
            .over("ticker")
            .fill_null(pl.col("Turnover"))
            .alias("d_turnover"),
            pl.col("DealNum").diff().over("ticker").fill_null(pl.col("DealNum")).alias("d_dealnum"),
        )
        .collect()
    )
    return orders, trades, snaps


def _float_column(frame: pl.DataFrame, name: str, dtype: Any) -> NDArray[Any]:
    return frame[name].cast(pl.Float64).fill_null(0.0).to_numpy().astype(dtype)


def _cent_column(frame: pl.DataFrame, name: str) -> NDArray[np.int32]:
    """Convert source prices in yuan to integer fen, preserving quote precision."""
    return np.round(frame[name].cast(pl.Float64).fill_null(0.0) * 100.0).astype(np.int32)


def _order_array(frame: pl.DataFrame) -> NDArray[np.void]:
    result = cast(NDArray[np.void], np.empty(len(frame), dtype=ORDER_DTYPE))
    for target, source, dtype in (
        ("time_ms", "time_ms", np.int32),
        ("volume", "Volume", np.int32),
        ("order_type", "OrderType", np.int16),
        ("cancel_age_ms", "cancel_age_ms", np.int32),
        ("cancel_orig_vol", "cancel_orig_vol", np.int32),
    ):
        result[target] = _float_column(frame, source, dtype)
    result["price"] = _cent_column(frame, "Price")
    result["last_price"] = _cent_column(frame, "LastPrice")
    return result


def _trade_array(frame: pl.DataFrame) -> NDArray[np.void]:
    result = cast(NDArray[np.void], np.empty(len(frame), dtype=TRADE_DTYPE))
    for target, source, dtype in (
        ("time_ms", "time_ms", np.int32),
        ("volume", "Volume", np.int32),
        ("side", "Side", np.int8),
        ("bsflag", "bsflag", np.int8),
        ("buy_age_ms", "buy_age_ms", np.int32),
        ("sell_age_ms", "sell_age_ms", np.int32),
    ):
        result[target] = _float_column(frame, source, dtype)
    result["price"] = _cent_column(frame, "Price")
    return result


def _snapshot_array(frame: pl.DataFrame) -> NDArray[np.void]:
    result = cast(NDArray[np.void], np.empty(len(frame), dtype=SNAP_DTYPE))
    for target, source, dtype in (
        ("time_ms", "time_ms", np.int32),
        ("d_volume", "d_volume", np.int32),
        ("d_turnover", "d_turnover", np.int64),
        ("d_dealnum", "d_dealnum", np.int32),
        ("total_bidvol", "TotalBidVolume", np.float32),
        ("total_askvol", "TotalAskVolume", np.float32),
    ):
        result[target] = _float_column(frame, source, dtype)
    result["last"] = _cent_column(frame, "Price")
    result["wbid"] = _cent_column(frame, "WeightBidPrice")
    result["wask"] = _cent_column(frame, "WeightAskPrice")
    for level in range(N_LEVELS):
        result["bid_px"][:, level] = _cent_column(frame, f"BidPrice{level + 1}")
        result["ask_px"][:, level] = _cent_column(frame, f"AskPrice{level + 1}")
        result["bid_vol"][:, level] = _float_column(frame, f"BidVolume{level + 1}", np.int32)
        result["ask_vol"][:, level] = _float_column(frame, f"AskVolume{level + 1}", np.int32)
        result["bid_cnt"][:, level] = np.clip(
            _float_column(frame, f"BidOrder{level + 1}", np.int64), 0, 65535
        ).astype(np.uint16)
        result["ask_cnt"][:, level] = np.clip(
            _float_column(frame, f"AskOrder{level + 1}", np.int64), 0, 65535
        ).astype(np.uint16)
    return result


def pack_day(
    day: int,
    *,
    raw_root: Path = RAW_L2_ROOT,
    pack_root: Path = PACK_ROOT,
    universe: list[str] | None = None,
    overwrite: bool = False,
) -> None:
    if day_is_packed(day, pack_root) and not overwrite:
        print(f"[{day}] already packed, skip", flush=True)
        return
    t0 = time.time()
    paths = day_input_files(day, raw_root)
    for _name, path in paths.items():
        if not path.exists():
            print(f"[{day}] missing {path}, skip day", flush=True)
            return

    if universe is not None and not universe:
        raise ValueError(f"{day} 的 universe 不能为空")
    orders, trades, snaps = _load_day_frames(day, paths, universe)
    order_arr = _order_array(orders)
    order_groups = _ticker_groups(orders)
    del orders
    gc.collect()

    trade_arr = _trade_array(trades)
    trade_groups = _ticker_groups(trades)
    del trades
    gc.collect()

    snap_arr = _snapshot_array(snaps)
    snap_groups = _ticker_groups(snaps)
    del snaps
    gc.collect()

    # ---------------- 每股票索引 ----------------
    tickers = sorted(set(order_groups) | set(trade_groups) | set(snap_groups))
    tk_to_i = {t: i for i, t in enumerate(tickers)}
    n = len(tickers)

    def offsets(groups: dict[str, tuple[int, int]]) -> tuple[NDArray[Any], NDArray[Any]]:
        off = np.zeros(n, dtype=np.int64)
        length = np.zeros(n, dtype=np.int64)
        for ticker, (start, count) in groups.items():
            i = tk_to_i[ticker]
            off[i], length[i] = start, count
        return off, length

    o_off, o_len = offsets(order_groups)
    t_off, t_len = offsets(trade_groups)
    s_off, s_len = offsets(snap_groups)
    prev_close = _load_prev_close(day, tickers, raw_root)

    pack_root.mkdir(parents=True, exist_ok=True)
    paths = day_pack_paths(day, pack_root)
    order_arr.tofile(paths["order"])
    trade_arr.tofile(paths["trade"])
    snap_arr.tofile(paths["snap"])
    np.savez_compressed(
        paths["index"],
        tickers=np.array(tickers),
        o_off=o_off,
        o_len=o_len,
        t_off=t_off,
        t_len=t_len,
        s_off=s_off,
        s_len=s_len,
        prev_close=prev_close,
    )
    total_mb = sum(paths[k].stat().st_size for k in ("order", "trade", "snap")) / 1e6
    print(
        f"[{day}] tickers={n} orders={len(order_arr) / 1e6:.1f}M "
        f"trades={len(trade_arr) / 1e6:.1f}M snaps={len(snap_arr) / 1e6:.1f}M "
        f"size={total_mb:.0f}MB {time.time() - t0:.0f}s",
        flush=True,
    )


def trading_days(start: int, end: int, raw_root: Path = RAW_L2_ROOT) -> list[int]:
    days: set[int] = set()
    for sub in (raw_root / "order").iterdir():
        if not sub.is_dir():
            continue
        for f in sub.glob("order_*.parquet"):
            d = int(f.stem.split("_")[1].replace("-", ""))
            if start <= d <= end:
                days.add(d)
    return sorted(days)


def _isolated_day_command(arguments: argparse.Namespace, day: int) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "ticknet.eventstream.pack",
        "--days",
        str(int(day)),
        "--raw-root",
        str(arguments.raw_root),
        "--pack-root",
        str(arguments.pack_root),
        "--no-isolate-days",
    ]
    if arguments.universe:
        command.extend(["--universe", str(arguments.universe)])
    if arguments.overwrite:
        command.append("--overwrite")
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=99999999)
    parser.add_argument("--days", type=int, nargs="*", default=None)
    parser.add_argument("--universe", default="", help="可选 JSON 股票列表文件，限制打包范围")
    parser.add_argument("--raw-root", type=Path, default=RAW_L2_ROOT)
    parser.add_argument("--pack-root", type=Path, default=PACK_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--isolate-days",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="多日任务默认每个交易日使用独立子进程，避免内存跨日累积",
    )
    args = parser.parse_args()

    days = args.days or trading_days(args.start, args.end, args.raw_root)
    if args.isolate_days and len(days) > 1:
        print(f"packing {len(days)} days with isolated workers", flush=True)
        for day in days:
            subprocess.run(_isolated_day_command(args, day), check=True)
        return

    universe = _load_universe(Path(args.universe)) if args.universe else None
    universe_description = (
        "ALL"
        if universe is None
        else f"static-{len(universe)}"
        if isinstance(universe, list)
        else f"daily-{len(universe)}"
    )
    print(f"packing {len(days)} days universe={universe_description}")
    for day in days:
        day_universe = _universe_for_day(universe, day)
        if universe is not None and day_universe is None:
            print(f"[{day}] universe missing, skip day", flush=True)
            continue
        pack_day(
            day,
            raw_root=args.raw_root,
            pack_root=args.pack_root,
            universe=day_universe,
            overwrite=args.overwrite,
        )


if __name__ == "__main__":
    main()
