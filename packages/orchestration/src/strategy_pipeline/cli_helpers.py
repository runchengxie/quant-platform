"""Small, strategy-neutral helpers for command-line adapters."""

from __future__ import annotations


def format_bytes(value: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def render_pct_bar(pct: float, width: int = 20) -> str:
    if pct <= 0:
        filled = 0
    elif pct >= 100:
        filled = width
    else:
        filled = round(width * pct / 100)
    return f"[{'#' * filled}{'-' * (width - filled)}] {pct:.2f}%"


def coerce_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def append_arg(argv: list[str], flag: str, value, *, formatter=str) -> None:
    if value is None or (isinstance(value, str) and value == ""):
        return
    argv.extend([flag, formatter(value)])


def append_repeat_args(argv: list[str], flag: str, values) -> None:
    if not values:
        return
    for entry in values:
        argv.extend([flag, str(entry)])


def append_bool_switch(
    argv: list[str],
    value: bool | None,
    *,
    true_flag: str,
    false_flag: str | None = None,
) -> None:
    if value is True:
        argv.append(true_flag)
    elif value is False and false_flag is not None:
        argv.append(false_flag)


def append_passthrough(argv: list[str], values) -> None:
    if values:
        items = list(values)
        if items and items[0] == "--":
            items = items[1:]
        argv.extend(items)


__all__ = [
    "append_arg",
    "append_bool_switch",
    "append_passthrough",
    "append_repeat_args",
    "coerce_float",
    "format_bytes",
    "render_pct_bar",
]
