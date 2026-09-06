"""Generic run-output persistence orchestration.

The public layer owns ordering and lifecycle. Research-specific summary,
evidence, and metadata writers are injected by the application owner.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import yaml

from .output_artifacts import write_run_artifacts
from .support import save_json

OutputCallback = Callable[..., Any]
InputLockBuilder = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def write_run_metadata(
    *,
    context: Mapping[str, Any],
    summary: Mapping[str, Any],
    input_lock_builder: InputLockBuilder | None = None,
) -> None:
    """Persist generic run files and an optional owner-provided input lock."""
    run_dir = Path(context["run_dir"])
    save_json(summary, run_dir / "summary.json")
    if input_lock_builder is not None:
        save_json(input_lock_builder(context), run_dir / "inputs.lock.json")
    with (run_dir / "config.used.yml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(context["config"], handle, sort_keys=False)

    if context.get("LIVE_ENABLED"):
        live = summary.get("live")
        live_summary = live if isinstance(live, Mapping) else {}
        latest_payload = {
            "pointer_type": "mutable_latest",
            "run_dir": str(run_dir),
            "run_name": context["run_name"],
            "timestamp": context["run_stamp"],
            "config_hash": context["run_hash"],
            "summary_file": str(run_dir / "summary.json"),
            "as_of": live_summary.get("as_of"),
            "positions_file": live_summary.get("positions_file"),
            "current_file": live_summary.get("current_file"),
            "diff_file": live_summary.get("diff_file"),
        }
        save_json(latest_payload, run_dir.parent / "latest.json")


def persist_run_outputs(
    *,
    context: Mapping[str, Any],
    summary_builder: OutputCallback,
    metadata_writer: OutputCallback,
    evidence_builder: OutputCallback | None = None,
) -> dict[str, Any]:
    """Write artifacts and invoke owner-provided output callbacks in order."""
    if not context.get("SAVE_ARTIFACTS", False):
        return {}

    artifacts = write_run_artifacts(context=context)
    if evidence_builder is not None:
        evidence_builder(context=context, artifacts=artifacts)
    summary = summary_builder(context=context, artifacts=artifacts)
    metadata_writer(context=context, summary=summary)
    return artifacts
