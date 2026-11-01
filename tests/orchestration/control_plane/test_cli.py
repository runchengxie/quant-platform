import json
from pathlib import Path

import pytest

from strategy_pipeline.cli import build_parser, main


def test_public_cli_exposes_only_generic_commands():
    parser = build_parser()

    inspect_args = parser.parse_args(["inspect", "--run-id", "run-1"])
    publish_args = parser.parse_args(["publish", "--run-id", "run-1"])

    assert inspect_args.command == "inspect"
    assert inspect_args.run_id == "run-1"
    assert publish_args.command == "publish"
    assert publish_args.run_id == "run-1"


def test_public_cli_parses_generic_target_export():
    parser = build_parser()

    args = parser.parse_args(
        [
            "export-targets",
            "--holdings",
            "holdings.json",
            "--out",
            "targets.json",
        ]
    )

    assert args.command == "export-targets"
    assert args.holdings == "holdings.json"
    assert args.out == "targets.json"


def test_public_cli_parses_cashflow_shadow_publication():
    parser = build_parser()

    args = parser.parse_args(
        [
            "cashflow-publish-shadow",
            "--selection",
            "selection.json",
            "--readiness",
            "readiness.json",
            "--output-root",
            "published",
        ]
    )

    assert args.command == "cashflow-publish-shadow"
    assert args.selection == "selection.json"


@pytest.mark.parametrize("command", ["inspect", "publish", "handoff"])
def test_unimplemented_commands_fail_closed(command, capsys):
    result = main([command, "--run-id", "run-1"])

    captured = capsys.readouterr()
    assert result != 0
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error["status"] == "not_implemented"
    assert error["command"] == command
    assert error["run_id"] == "run-1"
    assert error["message"]


def test_target_export_still_writes_artifacts_and_returns_success(tmp_path, capsys):
    holdings = tmp_path / "holdings.json"
    holdings.write_text(
        json.dumps({"holdings": [{"symbol": "SYNTH", "market": "US", "weight": 0.5}]})
    )
    targets = tmp_path / "targets.json"

    result = main(["export-targets", "--holdings", str(holdings), "--out", str(targets)])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    output = json.loads(captured.out)
    assert output["targets"] == str(targets)
    assert json.loads(targets.read_text())["targets"] == [
        {"symbol": "SYNTH", "market": "US", "target_weight": 0.5}
    ]
    assert Path(output["lineage"]).is_file()
