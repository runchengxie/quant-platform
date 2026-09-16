"""Output path resolution for alpha research command line tools.

Research reports are durable run artifacts and should live outside a Git
checkout. An explicit CLI path always wins. The environment variables provide
stable owner-specific roots for local and deployed runs.
"""

from __future__ import annotations

import os
from pathlib import Path


def output_root() -> Path:
    """Return the alpha research output root without creating it."""

    for name in ("ALPHA_RESEARCH_OUTPUT_ROOT", "QUANT_PLATFORM_OUTPUT_ROOT"):
        configured = os.getenv(name)
        if configured:
            return Path(configured).expanduser().resolve()

    data_root = os.getenv("DATA_PLATFORM_ROOT")
    if data_root:
        return (Path(data_root).expanduser() / "quant-platform" / "research").resolve()

    xdg_state = os.getenv("XDG_STATE_HOME")
    state_root = Path(xdg_state).expanduser() if xdg_state else Path.home() / ".local" / "state"
    return (state_root / "quant-platform" / "research").resolve()


def default_output_path(relative_path: str | Path) -> Path:
    """Return a path under the configured alpha research output root."""

    relative = Path(relative_path)
    if relative.is_absolute():
        raise ValueError("default output path must be relative")
    return output_root() / relative


def resolve_output_path(
    path_text: str | Path | None,
    *,
    default_relative: str | Path,
) -> Path:
    """Resolve an explicit output path or an owner-rooted default.

    Relative paths supplied by a caller remain relative to the current working
    directory for compatibility. Only omitted CLI values use the external
    owner root.
    """

    if path_text is None or not str(path_text).strip():
        return default_output_path(default_relative)
    candidate = Path(path_text).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (Path.cwd() / candidate).resolve()


__all__ = ["default_output_path", "output_root", "resolve_output_path"]
