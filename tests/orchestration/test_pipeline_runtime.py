from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from strategy_pipeline.pipeline.runtime import (
    _days_to_steps,
    _resolve_holdout_len,
    config_hash,
    setup_logging,
)


def test_runtime_helpers_normalize_holdout_and_gap_values() -> None:
    assert _resolve_holdout_len(None, 10) == 0
    assert _resolve_holdout_len(0.2, 10) == 2
    assert _resolve_holdout_len(3, 10) == 3
    assert _days_to_steps(10, 2.5) == 4
    assert _days_to_steps(10, None) == 10


def test_config_hash_is_stable_and_logging_can_write_file(tmp_path) -> None:
    config = {"model": {"type": "linear"}, "seed": 7}
    assert config_hash(config) == config_hash({"seed": 7, "model": {"type": "linear"}})

    log_path = tmp_path / "run.log"
    assert setup_logging({"logging": {"level": "INFO", "file": str(log_path)}}) == log_path
    logging.getLogger("runtime-test").info("runtime smoke")
    assert "runtime smoke" in log_path.read_text(encoding="utf-8")

    setup_logging({"logging": {"level": "WARNING"}})
    assert np.isfinite(1.0)
    assert isinstance(pd.Timestamp("2026-01-01"), pd.Timestamp)
