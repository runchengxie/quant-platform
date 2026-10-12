"""Command-line interface for materialized eventstream datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from ticknet.eventstream.fingerprint import git_sha
from ticknet.eventstream.materialized import (
    MANIFEST_NAME,
    PARTITIONS,
    _atomic_json,
    build_materialized_dataset,
    verify_materialized_dataset,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="物化并核对事件流固定训练窗口")
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="从正式 pack 生成按月物化训练集")
    build.add_argument("--config", type=Path, required=True)
    build.add_argument("--storage-manifest", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--source-revision", default="")

    verify = commands.add_parser("verify", help="逐文件核对物化训练集")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--output", type=Path)
    verify.add_argument(
        "--partition",
        action="append",
        choices=PARTITIONS,
        dest="partitions",
        help="只核对指定分区，可重复使用。默认核对全部分区",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    arguments = _parser().parse_args(argv)
    if arguments.command == "build":
        from ticknet.eventstream.train import EventstreamConfig

        with arguments.config.expanduser().resolve().open(encoding="utf-8") as file:
            raw = yaml.safe_load(file)
        if not isinstance(raw, dict):
            raise ValueError("事件流配置应为 YAML 对象")
        config = EventstreamConfig.from_mapping(raw)
        report = build_materialized_dataset(
            config,
            storage_manifest_path=arguments.storage_manifest.expanduser().resolve(),
            output_root=arguments.output.expanduser().resolve(),
            source_revision=arguments.source_revision or git_sha(Path.cwd()),
        )
    else:
        report = verify_materialized_dataset(
            arguments.root.expanduser().resolve(),
            partitions=tuple(arguments.partitions or PARTITIONS),
        )
        if arguments.output is not None:
            _atomic_json(arguments.output.expanduser().resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))


__all__ = ["MANIFEST_NAME", "_parser", "main"]
