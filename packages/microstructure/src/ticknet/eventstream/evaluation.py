"""Evaluation metrics for eventstream training."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from numpy.typing import NDArray
from torch.utils.data import DataLoader

from ticknet.eventstream.data_loading import EventstreamSample
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.eventstream.materialized import MaterializedWindowDataset

type FloatArray = NDArray[np.float32] | NDArray[np.float64]
type IntArray = NDArray[np.int64]


def _empty_metrics() -> dict[str, Any]:
    return {
        "daily_rank_ic_mean": math.nan,
        "daily_rank_ic_std": math.nan,
        "ic_ir": math.nan,
        "daily_spread_mean": math.nan,
        "n_days": 0,
        "n_samples": 0,
    }


def _spearman(a: FloatArray, b: FloatArray) -> float:
    if a.size < 2 or np.std(a) == 0 or np.std(b) == 0:
        return math.nan

    def ranks(values: FloatArray) -> FloatArray:
        order = np.argsort(values, kind="mergesort")
        out = np.empty(values.size)
        out[order] = np.arange(values.size)
        return out

    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


@torch.no_grad()
def evaluate_rank_ic(
    model: nn.Module,
    dataloader: DataLoader[EventstreamSample] | None,
    device: torch.device,
    *,
    min_symbols_per_day: int,
) -> dict[str, Any]:
    """day 头在最后一个有效位置（收盘全量上下文）的逐日 Spearman Rank IC。"""
    if dataloader is None:
        return _empty_metrics()
    dataset = dataloader.dataset
    if not isinstance(dataset, (L2WindowDataset, MaterializedWindowDataset)):
        raise TypeError("事件流评估需要原始或物化窗口数据集")
    if len(dataset) == 0:
        return _empty_metrics()
    preds: list[FloatArray] = []
    labs: list[FloatArray] = []
    day_ids: list[IntArray] = []
    model.eval()
    use_amp = torch.cuda.is_available()
    for batch in dataloader:
        x, sid, oid, _, _, _, tgt_day, day_valid, valid, day = (
            b.to(device, non_blocking=True) for b in batch
        )
        with torch.autocast(device.type, dtype=torch.float16, enabled=use_amp):
            out = model(x, sid, oid)
        last = valid.sum(-1).clamp(min=1).long() - 1
        score = out["day"].float().gather(1, last[:, None]).squeeze(1)
        keep = day_valid > 0
        preds.append(score[keep].cpu().numpy())
        labs.append(tgt_day[keep].cpu().numpy())
        day_ids.append(day[keep].cpu().numpy())
    model.train()
    if not preds:
        return {
            **dict.fromkeys(
                ("daily_rank_ic_mean", "daily_rank_ic_std", "ic_ir", "daily_spread_mean"), math.nan
            ),
            "n_days": 0,
            "n_samples": 0,
        }
    pred = np.concatenate(preds)
    lab = np.concatenate(labs)
    day = np.concatenate(day_ids)

    grouped: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for p, val, d in zip(pred, lab, day, strict=True):
        grouped[int(d)].append((float(p), float(val)))
    daily_ics: list[float] = []
    spreads: list[float] = []
    for rows in grouped.values():
        if len(rows) < min_symbols_per_day:
            continue
        ps = np.asarray([r[0] for r in rows])
        ls = np.asarray([r[1] for r in rows])
        ic = _spearman(ps, ls)
        if math.isfinite(ic):
            daily_ics.append(ic)
        order = np.argsort(ps, kind="mergesort")
        tail = max(1, int(np.floor(len(ps) * 0.1)))
        spreads.append(float(ls[order[-tail:]].mean() - ls[order[:tail]].mean()))
    mean = float(np.mean(daily_ics)) if daily_ics else math.nan
    std = float(np.std(daily_ics, ddof=1)) if len(daily_ics) > 1 else math.nan
    return {
        "daily_rank_ic_mean": mean,
        "daily_rank_ic_std": std,
        "ic_ir": float(mean / std) if math.isfinite(std) and std > 0 else math.nan,
        "daily_spread_mean": float(np.mean(spreads)) if spreads else math.nan,
        "n_days": len(daily_ics),
        "n_samples": len(pred),
    }
