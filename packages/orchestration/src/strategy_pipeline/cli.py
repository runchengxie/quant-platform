"""Generic public control-plane command line interface."""

from __future__ import annotations

import argparse
import json

from .control_plane.targets import export_targets


def build_parser() -> argparse.ArgumentParser:
    from .cli_evidence import register_afml_evidence_commands
    from .cli_protocol import register_protocol_commands

    parser = argparse.ArgumentParser(prog="strategy-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    register_afml_evidence_commands(commands)
    register_protocol_commands(commands)
    for name in ("inspect", "publish", "handoff"):
        command = commands.add_parser(name)
        command.add_argument("--run-id", required=True)
    export = commands.add_parser("export-targets")
    export.add_argument(
        "--holdings", required=True, help="Owner-produced holdings JSON path."
    )
    export.add_argument(
        "--out", required=True, help="Canonical targets JSON output path."
    )
    export.add_argument("--lineage-out", help="Optional lineage sidecar output path.")
    export.add_argument("--source", default="strategy-pipeline")
    cashflow = commands.add_parser("cashflow-publish-shadow")
    cashflow.add_argument("--selection", required=True)
    cashflow.add_argument("--readiness", required=True)
    cashflow.add_argument("--output-root", required=True)
    cashflow.add_argument("--allow-reconstructed-pit", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    if args.command == "export-targets":
        lineage = export_targets(
            args.holdings,
            args.out,
            lineage_path=args.lineage_out,
            source=args.source,
        )
        print(json.dumps({"targets": args.out, "lineage": str(lineage)}))
        return 0
    if args.command == "cashflow-publish-shadow":
        from .cashflow_publication import publish_cashflow_shadow

        publication = publish_cashflow_shadow(
            args.selection,
            readiness_path=args.readiness,
            output_root=args.output_root,
            allow_reconstructed_pit=args.allow_reconstructed_pit,
        )
        print(
            json.dumps(
                {
                    "targets": str(publication.targets_path),
                    "receipt": str(publication.receipt_path),
                }
            )
        )
        return 0
    print(json.dumps({"command": args.command, "run_id": args.run_id}))
    return 0
