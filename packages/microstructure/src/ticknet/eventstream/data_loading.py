"""Eventstream training and evaluation data loaders."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ticknet.eventstream.config import day_is_packed
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.eventstream.materialized import (
    MaterializedWindowDataset,
    assert_materialized_compatible,
    load_materialized_manifest,
)
from ticknet.eventstream.training_config import EventstreamConfig

type EventstreamSample = tuple[torch.Tensor, ...]


def list_packed_days(start: int, end: int, root: Path) -> list[int]:
    days: list[int] = []
    for f in sorted(root.glob("index_*.npz")):
        d = int(f.stem.split("_")[1])
        if start <= d <= end and day_is_packed(d, root):
            days.append(d)
    return days


def _resolve_days(config: EventstreamConfig, root: Path) -> list[int]:
    if config.days:
        return list(config.days)
    return list_packed_days(config.train_start, config.train_end, root)


def _window_dataset_kwargs(config: EventstreamConfig) -> dict[str, bool]:
    return {
        "use_lob_prefix": config.use_lob_prefix,
        "use_session_anchors": config.use_session_anchors,
    }


def make_dataloaders(
    config: EventstreamConfig,
    *,
    device: torch.device,
) -> tuple[
    DataLoader[EventstreamSample],
    DataLoader[EventstreamSample] | None,
    DataLoader[EventstreamSample] | None,
]:
    if config.materialized_root:
        root = Path(config.materialized_root)
        manifest = load_materialized_manifest(root)
        assert_materialized_compatible(manifest, config)
        train_ds = MaterializedWindowDataset(
            root,
            "train",
            target_overlay_root=(
                Path(config.target_overlay_root) if config.target_overlay_root else None
            ),
        )
        val_ds = MaterializedWindowDataset(root, "validation")
        test_ds = MaterializedWindowDataset(root, "oos") if config.evaluate_test else None
        train_loader = DataLoader[EventstreamSample](
            train_ds,
            batch_size=config.batch_size,
            shuffle=True,
            drop_last=True,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
            persistent_workers=config.num_workers > 0,
        )
        val_loader = DataLoader[EventstreamSample](
            val_ds,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
        )
        test_loader = (
            DataLoader[EventstreamSample](
                test_ds,
                batch_size=config.batch_size,
                shuffle=False,
                num_workers=config.num_workers,
                pin_memory=device.type == "cuda",
            )
            if test_ds is not None
            else None
        )
        return train_loader, val_loader, test_loader

    root = Path(config.pack_root)
    label_path = Path(config.label_path) if config.label_path else None
    train_ds = L2WindowDataset(
        _resolve_days(config, root),
        seq_len=config.seq_len,
        min_events=config.min_events,
        samples_per_day=config.samples_per_day,
        root=root,
        label_path=label_path,
        seed=config.seed,
        **_window_dataset_kwargs(config),
    )
    train_loader = DataLoader[EventstreamSample](
        train_ds,
        batch_size=config.batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=config.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=config.num_workers > 0,
    )
    val_loader = test_loader = None
    if config.val_start:
        val_days = list_packed_days(config.val_start, config.val_end, root)
        val_ds = L2WindowDataset(
            val_days,
            seq_len=config.seq_len,
            min_events=config.min_events,
            root=root,
            label_path=label_path,
            eval_mode=True,
            eval_tickers=config.eval_tickers,
            **_window_dataset_kwargs(config),
        )
        val_loader = DataLoader[EventstreamSample](
            val_ds,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
        )
    if config.test_start and config.evaluate_test:
        test_days = list_packed_days(config.test_start, config.test_end, root)
        test_ds = L2WindowDataset(
            test_days,
            seq_len=config.seq_len,
            min_events=config.min_events,
            root=root,
            label_path=label_path,
            eval_mode=True,
            eval_tickers=0,
            **_window_dataset_kwargs(config),
        )
        test_loader = DataLoader[EventstreamSample](
            test_ds,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
        )
    return train_loader, val_loader, test_loader


def make_monitor_dataloaders(
    config: EventstreamConfig,
    *,
    device: torch.device,
) -> tuple[DataLoader[EventstreamSample] | None, DataLoader[EventstreamSample] | None]:
    """用同一批确定性收盘窗口加载只监控标签，不参与 checkpoint 选择。"""
    if config.materialized_root:
        root = Path(config.materialized_root)
        validation = DataLoader[EventstreamSample](
            MaterializedWindowDataset(root, "monitor_validation"),
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
        )
        oos = (
            DataLoader[EventstreamSample](
                MaterializedWindowDataset(root, "monitor_oos"),
                batch_size=config.batch_size,
                shuffle=False,
                num_workers=config.num_workers,
                pin_memory=device.type == "cuda",
            )
            if config.evaluate_test
            else None
        )
        return validation, oos
    if not config.monitor_label_path:
        return None, None
    root = Path(config.pack_root)
    label_path = Path(config.monitor_label_path)

    def build(start: int, end: int, eval_tickers: int) -> DataLoader[EventstreamSample] | None:
        if not start:
            return None
        dataset = L2WindowDataset(
            list_packed_days(start, end, root),
            seq_len=config.seq_len,
            min_events=config.min_events,
            root=root,
            label_path=label_path,
            eval_mode=True,
            eval_tickers=eval_tickers,
            **_window_dataset_kwargs(config),
        )
        return DataLoader[EventstreamSample](
            dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=device.type == "cuda",
        )

    return (
        build(config.val_start, config.val_end, config.eval_tickers),
        build(config.test_start, config.test_end, 0),
    )
