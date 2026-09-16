"""Project path helpers."""

from __future__ import annotations

import os
from pathlib import Path

_OUTPUT_ROOT_ENV = "QUANT_PLATFORM_OUTPUT_ROOT"
_DATA_ROOT_ENV = "DATA_PLATFORM_ROOT"
_QEXEC_OUTPUTS_ENV = "QEXEC_OUTPUTS_DIR"


def get_project_root() -> Path:
    """Return repository root."""

    try:
        return Path(__file__).resolve().parents[2]
    except NameError:
        return Path.cwd()


def outputs_dir() -> Path:
    """Return the active outputs directory.

    ``QEXEC_OUTPUTS_DIR`` is the most specific override. Otherwise
    ``QUANT_PLATFORM_OUTPUT_ROOT`` identifies this platform's output root and
    ``DATA_PLATFORM_ROOT`` provides a stable shared-data parent for deployments.
    The final fallback is the user's XDG state directory, so importing or
    running the package never creates an ``outputs`` directory in the checkout.
    """

    override = os.getenv(_QEXEC_OUTPUTS_ENV)
    if override:
        return Path(override).expanduser().resolve()
    owner_root = os.getenv(_OUTPUT_ROOT_ENV)
    if owner_root:
        return Path(owner_root).expanduser().resolve()
    data_root = os.getenv(_DATA_ROOT_ENV)
    if data_root:
        return (Path(data_root).expanduser() / "quant-platform" / "execution").resolve()
    xdg_state = os.getenv("XDG_STATE_HOME")
    state_root = Path(xdg_state).expanduser() if xdg_state else Path.home() / ".local" / "state"
    return (state_root / "quant-platform" / "execution").resolve()


PROJECT_ROOT = get_project_root()
OUTPUTS_DIR = outputs_dir()
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ["OUTPUTS_DIR", "PROJECT_ROOT", "get_project_root", "outputs_dir"]
