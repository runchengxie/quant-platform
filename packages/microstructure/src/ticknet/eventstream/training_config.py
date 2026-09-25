"""Configuration for eventstream model training."""

from __future__ import annotations

from typing import Any

from ticknet.eventstream.config import PACK_ROOT
from ticknet.eventstream.model import CONFIGS, DAY_SUPERVISION_MODES


class EventstreamConfig:
    """一次事件流预训练实验的配置。"""

    __slots__ = (
        "amp",
        "batch_size",
        "checkpoint_dir",
        "checkpoint_name",
        "day_loss_weight",
        "day_supervision_mode",
        "days",
        "device",
        "epochs",
        "eval_tickers",
        "evaluate_test",
        "gradient_accumulation_steps",
        "init_checkpoint",
        "label_path",
        "lr",
        "materialized_root",
        "materialized_source_revision",
        "min_events",
        "min_symbols_per_day",
        "model",
        "monitor_label_path",
        "monitor_name",
        "num_workers",
        "pack_root",
        "patience",
        "resume",
        "samples_per_day",
        "seed",
        "selection_metric",
        "seq_len",
        "source_revision",
        "target_overlay_root",
        "test_end",
        "test_start",
        "train_end",
        "train_start",
        "use_lob_prefix",
        "use_session_anchors",
        "use_vq",
        "val_end",
        "val_start",
        "vq_codebook_size",
        "vq_dim",
        "vq_loss_weight",
        "weight_decay",
    )

    def __init__(
        self,
        *,
        pack_root: str = str(PACK_ROOT),
        label_path: str = "",
        monitor_label_path: str = "",
        monitor_name: str = "",
        train_start: int = 0,
        train_end: int = 0,
        val_start: int = 0,
        val_end: int = 0,
        test_start: int = 0,
        test_end: int = 0,
        days: tuple[int, ...] = (),
        model: str = "probe25m",
        seq_len: int = 512,
        min_events: int = 256,
        samples_per_day: int = 2000,
        eval_tickers: int = 200,
        evaluate_test: bool = True,
        day_supervision_mode: str = "all",
        day_loss_weight: float = 1.0,
        use_lob_prefix: bool = False,
        use_session_anchors: bool = False,
        init_checkpoint: str = "",
        use_vq: bool = False,
        vq_codebook_size: int = 1024,
        vq_dim: int = 64,
        vq_loss_weight: float = 0.25,
        epochs: int = 20,
        batch_size: int = 8,
        lr: float = 3e-4,
        materialized_root: str = "",
        materialized_source_revision: str = "",
        target_overlay_root: str = "",
        weight_decay: float = 0.1,
        patience: int = 4,
        seed: int = 0,
        num_workers: int = 0,
        device: str = "cpu",
        amp: bool = True,
        gradient_accumulation_steps: int = 1,
        resume: bool = True,
        checkpoint_dir: str = "./checkpoints-eventstream",
        checkpoint_name: str = "eventstream",
        selection_metric: str = "daily_rank_ic_mean",
        source_revision: str = "",
        min_symbols_per_day: int = 20,
    ):
        self.pack_root = pack_root
        self.label_path = label_path
        self.monitor_label_path = monitor_label_path
        self.monitor_name = monitor_name
        self.train_start = train_start
        self.train_end = train_end
        self.val_start = val_start
        self.val_end = val_end
        self.test_start = test_start
        self.test_end = test_end
        self.days = days
        self.model = model
        self.seq_len = seq_len
        self.min_events = min_events
        self.samples_per_day = samples_per_day
        self.eval_tickers = eval_tickers
        self.evaluate_test = evaluate_test
        self.day_supervision_mode = day_supervision_mode
        self.day_loss_weight = float(day_loss_weight)
        self.use_lob_prefix = bool(use_lob_prefix)
        self.use_session_anchors = bool(use_session_anchors)
        self.init_checkpoint = str(init_checkpoint)
        self.use_vq = bool(use_vq)
        self.vq_codebook_size = int(vq_codebook_size)
        self.vq_dim = int(vq_dim)
        self.vq_loss_weight = float(vq_loss_weight)
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.materialized_root = materialized_root
        self.materialized_source_revision = materialized_source_revision
        self.target_overlay_root = target_overlay_root
        self.weight_decay = weight_decay
        self.patience = patience
        self.seed = seed
        self.num_workers = num_workers
        self.device = device
        self.amp = amp
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.resume = resume
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_name = checkpoint_name
        self.selection_metric = selection_metric
        self.source_revision = source_revision
        self.min_symbols_per_day = min_symbols_per_day

    def validate(self) -> None:
        self._validate_model_and_training()
        self._validate_event_features()
        self._validate_input_contract()

    def _validate_model_and_training(self) -> None:
        if self.model not in CONFIGS:
            raise ValueError(f"model 应为 {sorted(CONFIGS)} 之一")
        if self.seq_len < 2 or self.min_events < 1 or self.samples_per_day < 1:
            raise ValueError("seq_len、min_events 和 samples_per_day 应为正整数")
        if self.epochs < 1 or self.batch_size < 1 or self.patience < 1:
            raise ValueError("epochs、batch_size 和 patience 应为正整数")
        if self.lr <= 0 or self.weight_decay < 0:
            raise ValueError("lr 应为正数，weight_decay 不能为负数")
        if self.num_workers < 0:
            raise ValueError("num_workers 不能为负数")
        if self.gradient_accumulation_steps < 1:
            raise ValueError("gradient_accumulation_steps 应为正整数")
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("device 应为 cpu 或 cuda")
        if self.day_supervision_mode not in DAY_SUPERVISION_MODES:
            raise ValueError(f"day_supervision_mode 应为 {sorted(DAY_SUPERVISION_MODES)} 之一")
        if self.day_loss_weight < 0:
            raise ValueError("day_loss_weight 不能为负数")

    def _validate_event_features(self) -> None:
        if self.use_session_anchors and not self.use_lob_prefix:
            raise ValueError("use_session_anchors 需要同时启用 use_lob_prefix")
        if self.vq_codebook_size < 2:
            raise ValueError("vq_codebook_size 至少为 2")
        if self.vq_dim < 2:
            raise ValueError("vq_dim 至少为 2")
        if self.vq_loss_weight < 0:
            raise ValueError("vq_loss_weight 不能为负数")
        if self.min_symbols_per_day < 2:
            raise ValueError("min_symbols_per_day 至少为 2")

    def _validate_input_contract(self) -> None:
        if self.monitor_label_path and not self.monitor_name:
            raise ValueError("提供 monitor_label_path 时必须提供 monitor_name")
        if self.target_overlay_root and not self.materialized_root:
            raise ValueError("target_overlay_root 只能与 materialized_root 一起使用")
        if self.materialized_source_revision and not self.materialized_root:
            raise ValueError("materialized_source_revision 只能与 materialized_root 一起使用")
        if self.monitor_name and (
            not self.monitor_name.isascii() or not self.monitor_name.replace("_", "").isalnum()
        ):
            raise ValueError("monitor_name 只能包含 ASCII 字母、数字和下划线")
        if (
            not self.materialized_root
            and not self.days
            and not (0 < self.train_start < self.train_end)
        ):
            raise ValueError("需要显式 days 或有效的 train_start/train_end 区间")
        if self.source_revision and (
            not self.source_revision.isascii() or len(self.source_revision) < 7
        ):
            raise ValueError("source_revision 应为至少 7 位 ASCII 标识")

    def to_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__slots__}

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> EventstreamConfig:
        unknown = set(raw) - set(cls.__slots__)
        if unknown:
            raise ValueError(f"配置包含未知字段：{sorted(unknown)}")
        data = dict(raw)
        if isinstance(data.get("days"), list):
            data["days"] = tuple(data["days"])
        return cls(**data)
