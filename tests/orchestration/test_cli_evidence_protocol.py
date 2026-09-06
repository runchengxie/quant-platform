from __future__ import annotations

from strategy_pipeline.cli import build_parser


def test_public_cli_registers_evidence_and_protocol_commands():
    parser = build_parser()
    assert (
        parser.parse_args(["afml-evidence", "--run-dir", "run"]).command
        == "afml-evidence"
    )
    assert (
        parser.parse_args(
            ["research-protocol", "--level", "exploratory", "--init-manifest", "m.json"]
        ).command
        == "research-protocol"
    )
