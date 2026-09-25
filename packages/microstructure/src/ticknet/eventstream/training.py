"""Eventstream model training orchestration."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader

from ticknet.eventstream.checkpoints import (
    _atomic_json,
    _atomic_torch_save,
    _checkpoint_matches_experiment,
    _checkpoint_paths,
    _environment,
    _experiment_signature,
    _json_safe,
    _load_checkpoint,
    _warm_start_from_checkpoint,
)
from ticknet.eventstream.data_loading import (
    _resolve_days,
    make_dataloaders,
    make_monitor_dataloaders,
)
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.eventstream.evaluation import evaluate_rank_ic
from ticknet.eventstream.fingerprint import dataset_fingerprint, file_sha256
from ticknet.eventstream.materialized import (
    MaterializedWindowDataset,
    assert_materialized_compatible,
    load_materialized_manifest,
)
from ticknet.eventstream.model import build_eventstream_model, compute_loss
from ticknet.eventstream.training_config import EventstreamConfig
from ticknet.train import resolve_device, set_seed


def train(
    config: EventstreamConfig,
    *,
    expected_parameter_count: int | None = None,
) -> dict[str, Any]:
    """训练事件流基础模型并在验证/测试区间上评估 day 头 Rank IC。"""
    started_at = time.perf_counter()
    config.validate()
    set_seed(config.seed)
    device = resolve_device(config.device)
    train_loader, val_loader, test_loader = make_dataloaders(config, device=device)
    monitor_val_loader, monitor_test_loader = make_monitor_dataloaders(config, device=device)

    root = Path(config.pack_root)
    fingerprint, monitor_label_fingerprint = _dataset_fingerprints(config, root)
    signature = _experiment_signature(config, fingerprint, monitor_label_fingerprint)
    train_dataset = train_loader.dataset
    target_overlay_fingerprint = _target_overlay_fingerprint(train_dataset)
    if target_overlay_fingerprint is not None:
        signature["target_overlay_fingerprint"] = target_overlay_fingerprint

    model = build_eventstream_model(
        config.model,
        use_vq=config.use_vq,
        vq_codebook_size=config.vq_codebook_size,
        vq_dim=config.vq_dim,
    ).to(device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    _validate_parameter_count(parameter_count, expected_parameter_count)
    _stem, last_path, best_path, history_path, result_path = _checkpoint_paths(config)
    _warm_start_if_requested(config, model, device, last_path)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.lr, weight_decay=config.weight_decay, betas=(0.9, 0.95)
    )
    use_amp = config.amp and device.type == "cuda"
    scaler = torch.amp.GradScaler(device.type, enabled=use_amp)

    start_epoch = 0
    best_selection_value = -math.inf
    epochs_without_improvement = 0
    history: list[dict[str, Any]] = []
    if config.resume and last_path.exists():
        (
            start_epoch,
            best_selection_value,
            epochs_without_improvement,
            history,
        ) = _restore_training_state(
            last_path,
            device=device,
            model=model,
            optimizer=optimizer,
            scaler=scaler,
            signature=signature,
        )
        print(f"从第 {start_epoch} 个 epoch 后继续训练：{last_path}")

    can_continue = epochs_without_improvement < config.patience
    if not can_continue:
        print("checkpoint 已达到 early stopping 条件，跳过后续训练。")
    epoch_range = range(start_epoch, config.epochs) if can_continue else range(0)

    for epoch in epoch_range:
        epoch_started_at = time.perf_counter()
        epoch_loss = _train_epoch(model, train_loader, optimizer, scaler, device, config, use_amp)

        validation = evaluate_rank_ic(
            model, val_loader, device, min_symbols_per_day=config.min_symbols_per_day
        )
        monitor_validation = evaluate_rank_ic(
            model,
            monitor_val_loader,
            device,
            min_symbols_per_day=config.min_symbols_per_day,
        )
        raw_selection = validation[config.selection_metric]
        selection_value = float(raw_selection) if raw_selection is not None else math.nan
        comparable = selection_value if math.isfinite(selection_value) else -math.inf
        improved = epoch == 0 or comparable > best_selection_value
        if improved:
            best_selection_value = comparable
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        record = {
            "epoch": epoch + 1,
            "train_loss": epoch_loss,
            "epoch_seconds": time.perf_counter() - epoch_started_at,
            **{f"val_{key}": value for key, value in validation.items()},
        }
        if monitor_val_loader is not None:
            record.update(
                {
                    f"val_{config.monitor_name}_{key}": value
                    for key, value in monitor_validation.items()
                }
            )
        history.append(record)
        state = {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scaler": scaler.state_dict(),
            "epoch": epoch + 1,
            "best_selection_value": best_selection_value,
            "epochs_without_improvement": epochs_without_improvement,
            "experiment": signature,
            "history": history,
        }
        if improved:
            _atomic_torch_save(best_path, state)
        _atomic_torch_save(last_path, state)
        _atomic_json(history_path, _json_safe(history))
        print(
            f"epoch {epoch + 1:03d}｜训练损失 {record['train_loss']:.4f}｜"
            f"验证 Rank IC {float(validation['daily_rank_ic_mean']):.4f}"
        )
        if epochs_without_improvement >= config.patience:
            print(f"验证指标连续 {config.patience} 个 epoch 未提升，停止训练。")
            break

    best = _load_checkpoint(best_path, device)
    model.load_state_dict(best["model"])
    val_metrics = evaluate_rank_ic(
        model, val_loader, device, min_symbols_per_day=config.min_symbols_per_day
    )
    test_metrics = _evaluate_optional_loader(
        model, test_loader, device, config.min_symbols_per_day, config.evaluate_test
    )
    monitor_val_metrics = evaluate_rank_ic(
        model,
        monitor_val_loader,
        device,
        min_symbols_per_day=config.min_symbols_per_day,
    )
    monitor_test_metrics = _evaluate_optional_loader(
        model, monitor_test_loader, device, config.min_symbols_per_day, config.evaluate_test
    )
    dataset_types = (L2WindowDataset, MaterializedWindowDataset)
    val_count = _checked_dataset_size(val_loader, dataset_types, "验证")
    test_count = _checked_dataset_size(test_loader, dataset_types, "测试")
    result = {
        "mode": "eventstream_train",
        "config": config.to_dict(),
        "parameter_count": parameter_count,
        "samples": {
            "train": _checked_dataset_size(train_loader, dataset_types, "训练"),
            "val": val_count,
            "test": test_count,
        },
        "environment": _environment(device),
        "duration_seconds": time.perf_counter() - started_at,
        "dataset_fingerprint": fingerprint,
        "target_overlay_fingerprint": target_overlay_fingerprint,
        "monitor_label_fingerprint": monitor_label_fingerprint,
        "best_epoch": int(best["epoch"]),
        "best_selection_value": float(best["best_selection_value"]),
        "val": val_metrics,
        "test": test_metrics,
        "test_status": "evaluated" if config.evaluate_test else "not_evaluated",
        "monitor": (
            None
            if monitor_val_loader is None
            else {
                "name": config.monitor_name,
                "label_path": config.monitor_label_path,
                "val": monitor_val_metrics,
                "test": monitor_test_metrics,
            }
        ),
        "result_file": str(result_path),
    }
    safe_result = _json_safe(result)
    _atomic_json(result_path, safe_result)
    print(json.dumps(safe_result, ensure_ascii=False, indent=2))
    return safe_result


def _target_overlay_fingerprint(dataset: Any) -> str | None:
    if not isinstance(dataset, (L2WindowDataset, MaterializedWindowDataset)):
        raise TypeError("训练数据集类型无效")
    if isinstance(dataset, MaterializedWindowDataset):
        return dataset.target_overlay_fingerprint
    return None


def _validate_parameter_count(parameter_count: int, expected_parameter_count: int | None) -> None:
    if expected_parameter_count is not None and parameter_count != expected_parameter_count:
        raise ValueError(f"事件流参数量不匹配：{parameter_count} != {expected_parameter_count}")


def _warm_start_if_requested(
    config: EventstreamConfig,
    model: torch.nn.Module,
    device: torch.device,
    last_path: Path,
) -> None:
    if config.init_checkpoint and not (config.resume and last_path.exists()):
        _warm_start_from_checkpoint(
            model, Path(config.init_checkpoint), device, use_vq=config.use_vq
        )


def _dataset_fingerprints(config: EventstreamConfig, root: Path) -> tuple[str, str | None]:
    if config.materialized_root:
        manifest = load_materialized_manifest(Path(config.materialized_root))
        assert_materialized_compatible(manifest, config)
        return str(manifest["dataset_fingerprint"]), None
    fingerprint = dataset_fingerprint(
        _resolve_days(config, root),
        root=root,
        label_path=Path(config.label_path) if config.label_path else None,
    )
    monitor_fingerprint = (
        file_sha256(config.monitor_label_path) if config.monitor_label_path else None
    )
    return fingerprint, monitor_fingerprint


def _train_epoch(
    model: torch.nn.Module,
    train_loader: DataLoader[tuple[torch.Tensor, ...]],
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    device: torch.device,
    config: EventstreamConfig,
    use_amp: bool,
) -> float:
    model.train()
    total_loss = 0.0
    sample_count = 0
    optimizer.zero_grad(set_to_none=True)
    for batch_index, batch in enumerate(train_loader):
        x, sid, oid, tgt_sid, tgt_oid, tgt_reg, tgt_day, day_valid, valid, _ = (
            tensor.to(device, non_blocking=True) for tensor in batch
        )
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            output = model(x, sid, oid)
            loss, _metrics = compute_loss(
                output,
                tgt_sid,
                tgt_oid,
                tgt_reg,
                tgt_day,
                day_valid,
                valid,
                day_supervision_mode=config.day_supervision_mode,
                day_loss_weight=config.day_loss_weight,
                vq_loss_weight=config.vq_loss_weight,
            )
        scaled_loss = loss / config.gradient_accumulation_steps
        scaler.scale(scaled_loss).backward()
        should_step = (batch_index + 1) % config.gradient_accumulation_steps == 0 or (
            batch_index + 1 == len(train_loader)
        )
        if should_step:
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
        total_loss += loss.item() * x.shape[0]
        sample_count += x.shape[0]
    if sample_count == 0:
        raise ValueError("训练数据集为空")
    return float(total_loss / sample_count)


def _restore_training_state(
    path: Path,
    *,
    device: torch.device,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    signature: dict[str, Any],
) -> tuple[int, float, int, list[dict[str, Any]]]:
    checkpoint = _load_checkpoint(path, device)
    if not _checkpoint_matches_experiment(checkpoint, signature):
        raise ValueError(f"{path} 的实验配置与本次运行不同")
    model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    if "scaler" in checkpoint:
        scaler.load_state_dict(checkpoint["scaler"])
    return (
        int(checkpoint["epoch"]),
        float(checkpoint["best_selection_value"]),
        int(checkpoint["epochs_without_improvement"]),
        list(checkpoint.get("history", [])),
    )


def _evaluate_optional_loader(
    model: torch.nn.Module,
    loader: DataLoader[Any] | None,
    device: torch.device,
    min_symbols_per_day: int,
    enabled: bool,
) -> dict[str, Any] | None:
    if not enabled:
        return None
    if loader is None:
        raise ValueError("已启用评估的 DataLoader 缺失")
    return evaluate_rank_ic(model, loader, device, min_symbols_per_day=min_symbols_per_day)


def _checked_dataset_size(loader, dataset_types, label: str) -> int:
    if loader is None:
        return 0
    if not isinstance(loader.dataset, dataset_types):
        raise TypeError(f"{label}数据集类型无效")
    return len(loader.dataset)
