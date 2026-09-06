from __future__ import annotations

import json
from pathlib import Path

import yaml

from strategy_pipeline.pipeline.output import write_run_metadata


def test_write_run_metadata_persists_generic_run_files(tmp_path: Path) -> None:
    run_dir = tmp_path / "artifacts" / "runs" / "demo"
    context = {
        "run_dir": run_dir,
        "config": {"market": "synthetic", "model": {"name": "fixture"}},
        "LIVE_ENABLED": True,
        "run_name": "demo",
        "run_stamp": "20260904_120000",
        "run_hash": "deadbeef",
    }
    summary = {
        "live": {
            "as_of": "20260904",
            "positions_file": "positions.csv",
            "current_file": "current.csv",
            "diff_file": "diff.csv",
        }
    }

    write_run_metadata(
        context=context,
        summary=summary,
        input_lock_builder=lambda _: {"inputs": {"panel": "fixture"}},
    )

    assert json.loads((run_dir / "summary.json").read_text()) == summary
    assert json.loads((run_dir / "inputs.lock.json").read_text()) == {
        "inputs": {"panel": "fixture"}
    }
    assert yaml.safe_load((run_dir / "config.used.yml").read_text()) == context["config"]
    assert json.loads((run_dir.parent / "latest.json").read_text()) == {
        "pointer_type": "mutable_latest",
        "run_dir": str(run_dir),
        "run_name": "demo",
        "timestamp": "20260904_120000",
        "config_hash": "deadbeef",
        "summary_file": str(run_dir / "summary.json"),
        "as_of": "20260904",
        "positions_file": "positions.csv",
        "current_file": "current.csv",
        "diff_file": "diff.csv",
    }
