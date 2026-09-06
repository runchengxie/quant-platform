"""CLI handlers for generic research protocol manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast


def add_protocol_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--level", choices=("exploratory", "candidate", "release"), required=True
    )
    parser.add_argument("--manifest", help="JSON or YAML evidence manifest.")
    parser.add_argument(
        "--init-manifest", help="Write a manifest template instead of evaluating one."
    )
    parser.add_argument("--output", default="research_protocol_report.json")
    parser.add_argument("--strict", action=argparse.BooleanOptionalAction, default=True)


def handle_protocol(args: argparse.Namespace) -> int:
    from alpha_research.research_protocols import (
        ProtocolLevel,
        evaluate_protocol_manifest,
        example_manifest,
        load_protocol_manifest,
        write_protocol_report,
    )

    level = cast(ProtocolLevel, str(args.level))
    if args.init_manifest:
        target = Path(args.init_manifest)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = example_manifest(level)
        if target.suffix.lower() == ".json":
            target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        else:
            import yaml

            target.write_text(
                yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
            )
        return 0
    if not args.manifest:
        raise SystemExit("--manifest is required unless --init-manifest is used")
    manifest_path = Path(args.manifest).expanduser().resolve()
    report = evaluate_protocol_manifest(
        load_protocol_manifest(manifest_path),
        level=level,
        base_dir=manifest_path.parent,
    )
    write_protocol_report(report, args.output)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 1 if args.strict and report.status != "pass" else 0


def register_protocol_commands(subparsers) -> None:
    parser = subparsers.add_parser(
        "research-protocol", help="Initialize or evaluate research evidence protocols"
    )
    add_protocol_args(parser)
    parser.set_defaults(func=handle_protocol)


__all__ = ["add_protocol_args", "handle_protocol", "register_protocol_commands"]
