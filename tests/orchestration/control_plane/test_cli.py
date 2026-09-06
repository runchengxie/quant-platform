from strategy_pipeline.cli import build_parser


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
