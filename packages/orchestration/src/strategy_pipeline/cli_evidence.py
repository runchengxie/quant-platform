"""CLI handlers for generic AFML evidence generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def add_afml_evidence_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--target-sharpe", type=float, default=1.0)
    parser.add_argument("--evaluation-years", type=float, default=2.0)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--random-state", type=int, default=0)
    parser.add_argument("--hrp-returns")
    parser.add_argument(
        "--manifest",
        help="Optional protocol manifest to merge with generated evidence.",
    )
    parser.add_argument("--manifest-output", help="Merged manifest output path.")


def handle_afml_evidence(args: argparse.Namespace) -> int:
    from alpha_research.research_protocols import load_protocol_manifest
    from portfolio_backtester.afml_evidence import (
        generate_run_afml_evidence,
        merge_evidence_fragment,
    )

    fragment = generate_run_afml_evidence(
        args.run_dir,
        target_sharpe=args.target_sharpe,
        evaluation_years=args.evaluation_years,
        bootstrap_samples=args.bootstrap_samples,
        random_state=args.random_state,
        hrp_returns_path=args.hrp_returns,
    )
    if args.manifest:
        manifest = load_protocol_manifest(args.manifest)
        merged = merge_evidence_fragment(manifest, fragment)
        target = Path(args.manifest_output or args.manifest)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix.lower() == ".json":
            target.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2, default=str) + "\n"
            )
        else:
            target.write_text(
                yaml.safe_dump(merged, allow_unicode=True, sort_keys=False)
            )
        fragment["merged_manifest"] = str(target)
    print(json.dumps(fragment, ensure_ascii=False, indent=2, default=str))
    return 0


def register_afml_evidence_commands(subparsers) -> None:
    parser = subparsers.add_parser(
        "afml-evidence",
        help="Generate sizing, strategy-risk, and optional HRP evidence",
    )
    add_afml_evidence_args(parser)
    parser.set_defaults(func=handle_afml_evidence)


__all__ = [
    "add_afml_evidence_args",
    "handle_afml_evidence",
    "register_afml_evidence_commands",
]
