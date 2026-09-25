"""Checkpoint persistence and experiment compatibility checks."""

from __future__ import annotations

import json
import math
import os
import platform
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ticknet.eventstream.model import DAY_SUPERVISION_WEIGHT_VERSION
from ticknet.eventstream.training_config import EventstreamConfig


def _atomic_torch_save(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(content, temporary)
    os.replace(temporary, path)


def _atomic_json(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2, allow_nan=False)
    os.replace(temporary, path)


def _load_checkpoint(path: Path, device: torch.device) -> dict[str, Any]:
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


def _warm_start_from_checkpoint(
    model: torch.nn.Module,
    path: Path,
    device: torch.device,
    *,
    use_vq: bool,
) -> None:
    """从异构 checkpoint 热启动（strict=False）。

    典型场景：已训练的连续通路模型（无 VQ 权重）作为启用 VQ 的
    新实验初始化。要求主干权重完全对齐；缺失键必须全部属于 VQ
    模块（use_vq=True 时），否则视为架构不匹配直接报错。
    """
    checkpoint = _load_checkpoint(path, device)
    result = model.load_state_dict(checkpoint["model"], strict=False)
    unexpected = list(result.unexpected_keys)
    if unexpected:
        raise ValueError(f"{path} 存在无法对齐的权重键：{unexpected[:8]}")
    missing = list(result.missing_keys)
    allowed_prefixes = ("vq_encoder", "vector_quantizer", "vq_proj") if use_vq else ()
    bad = [k for k in missing if not k.startswith(allowed_prefixes)]
    if bad:
        raise ValueError(f"{path} 缺失非 VQ 主干权重：{bad[:8]}")
    print(
        f"热启动自 {path}：加载主干 {len(checkpoint['model']) - len(missing)} 项，"
        f"随机初始化 {len(missing)} 项（{sorted({k.split('.')[0] for k in missing})}）"
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _environment(device: torch.device) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "device": str(device),
        "cuda": torch.version.cuda,
    }


def _experiment_signature(
    config: EventstreamConfig,
    fingerprint: str,
    monitor_label_fingerprint: str | None = None,
) -> dict[str, Any]:
    signature = config.to_dict()
    for name in (
        "epochs",
        "resume",
        "device",
        "num_workers",
        "amp",
        "gradient_accumulation_steps",
        "evaluate_test",
    ):
        signature.pop(name)
    if not config.monitor_label_path and not config.materialized_root:
        signature.pop("monitor_label_path")
        signature.pop("monitor_name")
    if not config.target_overlay_root:
        signature.pop("target_overlay_root")
    if not config.materialized_source_revision:
        signature.pop("materialized_source_revision")
    signature["dataset_fingerprint"] = fingerprint
    signature["day_supervision_weight_version"] = DAY_SUPERVISION_WEIGHT_VERSION
    if monitor_label_fingerprint is not None:
        signature["monitor_label_fingerprint"] = monitor_label_fingerprint
    return signature


def _checkpoint_matches_experiment(checkpoint: dict[str, Any], expected: dict[str, Any]) -> bool:
    experiment = checkpoint.get("experiment")
    if not isinstance(experiment, dict):
        return False
    normalized = dict(experiment)
    normalized.setdefault("day_loss_weight", 1.0)
    normalized.setdefault("day_supervision_mode", "all")
    normalized.setdefault("day_supervision_weight_version", DAY_SUPERVISION_WEIGHT_VERSION)
    normalized.setdefault("use_lob_prefix", False)
    normalized.setdefault("use_session_anchors", False)
    normalized.setdefault("use_vq", False)
    normalized.setdefault("vq_codebook_size", 1024)
    normalized.setdefault("vq_dim", 64)
    normalized.setdefault("vq_loss_weight", 0.25)
    expected_normalized = dict(expected)
    expected_normalized.setdefault("day_loss_weight", 1.0)
    expected_normalized.setdefault("day_supervision_mode", "all")
    expected_normalized.setdefault("day_supervision_weight_version", DAY_SUPERVISION_WEIGHT_VERSION)
    expected_normalized.setdefault("use_lob_prefix", False)
    expected_normalized.setdefault("use_session_anchors", False)
    expected_normalized.setdefault("use_vq", False)
    expected_normalized.setdefault("vq_codebook_size", 1024)
    expected_normalized.setdefault("vq_dim", 64)
    expected_normalized.setdefault("vq_loss_weight", 0.25)
    return normalized == expected_normalized


def _checkpoint_paths(config: EventstreamConfig) -> tuple[str, Path, Path, Path, Path]:
    root = Path(config.checkpoint_dir)
    stem = f"{config.checkpoint_name}.seed{config.seed}"
    return (
        stem,
        root / f"{stem}.last.pt",
        root / f"{stem}.best.pt",
        root / f"train_history.{stem}.json",
        root / f"result.{stem}.json",
    )
