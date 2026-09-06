from strategy_pipeline.cli_helpers import (
    append_arg,
    append_bool_switch,
    append_passthrough,
    append_repeat_args,
    coerce_float,
    format_bytes,
    render_pct_bar,
)


def test_cli_value_formatters():
    assert format_bytes(1024) == "1.00 KB"
    assert render_pct_bar(50, width=4) == "[##--] 50.00%"
    assert coerce_float("1.5") == 1.5
    assert coerce_float("bad") is None


def test_cli_argument_helpers():
    argv: list[str] = []
    append_arg(argv, "--name", "demo")
    append_arg(argv, "--empty", "")
    append_repeat_args(argv, "--tag", ["a", "b"])
    append_bool_switch(argv, True, true_flag="--enabled", false_flag="--disabled")
    append_bool_switch(argv, False, true_flag="--enabled", false_flag="--disabled")
    append_passthrough(argv, ["--", "--extra", "value"])
    assert argv == [
        "--name",
        "demo",
        "--tag",
        "a",
        "--tag",
        "b",
        "--enabled",
        "--disabled",
        "--extra",
        "value",
    ]
