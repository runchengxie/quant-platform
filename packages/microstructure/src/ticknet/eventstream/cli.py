"""Command line interface for eventstream training."""

from __future__ import annotations

import argparse

import yaml

from ticknet.eventstream.model import DAY_SUPERVISION_MODES
from ticknet.eventstream.training import train
from ticknet.eventstream.training_config import EventstreamConfig


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="YAML 配置文件")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--source-revision")
    parser.add_argument(
        "--day-supervision-mode",
        choices=sorted(DAY_SUPERVISION_MODES),
    )
    parser.add_argument("--day-loss-weight", type=float)
    parser.add_argument("--checkpoint-dir")
    parser.add_argument("--checkpoint-name")
    parser.add_argument("--expected-parameter-count", type=int)
    parser.add_argument(
        "--evaluate-test",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    args = parser.parse_args(argv)
    with open(args.config, encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    if not isinstance(raw, dict):
        raise ValueError("事件流配置应为 YAML 对象")
    overrides = {
        "seed": args.seed,
        "epochs": args.epochs,
        "source_revision": args.source_revision,
        "evaluate_test": args.evaluate_test,
        "day_supervision_mode": args.day_supervision_mode,
        "day_loss_weight": args.day_loss_weight,
        "checkpoint_dir": args.checkpoint_dir,
        "checkpoint_name": args.checkpoint_name,
    }
    for name, value in overrides.items():
        if value is not None:
            raw[name] = value
    config = EventstreamConfig.from_mapping(dict(raw))
    train(config, expected_parameter_count=args.expected_parameter_count)
