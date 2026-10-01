# Command-line adapter helpers

Language: English · [简体中文](cli-helpers.zh-CN.md)

`strategy_pipeline.cli_helpers` provides small, strategy-neutral helpers shared by command adapters. The module formats byte counts and percentage bars, converts optional values, and appends flags, repeated arguments, boolean switches, and pass-through arguments.

These helpers do not read configuration, access data, or implement strategy logic. Each command remains responsible for its own configuration and business arguments.

## Formatting and conversion

- `format_bytes(value)` formats using binary 1,024-based units from `B` through `PB`, with two decimal places.
- `render_pct_bar(pct, width=20)` renders a fixed-width bar. The filled width is clamped to zero through `width`; the displayed percentage remains the supplied value.
- `coerce_float(value)` returns `float(value)` when conversion succeeds and `None` for `TypeError` or `ValueError`.

## Build argument lists

- `append_arg(argv, flag, value, formatter=str)` skips `None` and the empty string; otherwise it appends the flag and formatted value.
- `append_repeat_args(argv, flag, values)` appends one flag/value pair for each entry.
- `append_bool_switch(argv, value, true_flag=..., false_flag=None)` appends the true flag for `True`; for `False`, it appends the false flag only when one is provided. `None` adds nothing.
- `append_passthrough(argv, values)` appends the supplied items and removes one leading `--` separator when present.

The module exports these helpers through `__all__`. Focused behavior tests are in `tests/orchestration/test_cli_helpers.py`.
