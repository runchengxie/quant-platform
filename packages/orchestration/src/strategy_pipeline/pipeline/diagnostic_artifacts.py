from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from .support import save_frame, save_json


def _write_turnover_attribution_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    result = ctx.get("turnover_attribution")
    payload = _diagnostic_payload(
        result,
        frame_fields=("by_window", "by_industry", "by_feature", "by_regime"),
    )
    if payload is None:
        return
    summary, result_frames = payload
    summary_path = run_dir / "turnover_attribution_summary.json"
    save_json(dict(summary), summary_path)
    artifacts["turnover_attribution_summary_path"] = summary_path
    frames = {
        "turnover_attribution_window_path": (
            result_frames["by_window"],
            "turnover_attribution_by_window.csv",
        ),
        "turnover_attribution_industry_path": (
            result_frames["by_industry"],
            "turnover_attribution_by_industry.csv",
        ),
        "turnover_attribution_feature_path": (
            result_frames["by_feature"],
            "turnover_attribution_by_feature.csv",
        ),
        "turnover_attribution_regime_path": (
            result_frames["by_regime"],
            "turnover_attribution_by_regime.csv",
        ),
    }
    _write_nonempty_frames(frames, run_dir=run_dir, artifacts=artifacts)


def _write_signal_stability_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    result = ctx.get("signal_stability")
    payload = _diagnostic_payload(
        result,
        frame_fields=("by_window", "by_symbol", "by_feature"),
    )
    if payload is None:
        return
    summary, result_frames = payload
    summary_path = run_dir / "signal_stability_summary.json"
    save_json(dict(summary), summary_path)
    artifacts["signal_stability_summary_path"] = summary_path
    frames = {
        "signal_stability_window_path": (
            result_frames["by_window"],
            "signal_stability_by_window.csv",
        ),
        "signal_stability_symbol_path": (
            result_frames["by_symbol"],
            "signal_stability_by_symbol.csv",
        ),
        "signal_stability_feature_path": (
            result_frames["by_feature"],
            "signal_stability_by_feature.csv",
        ),
    }
    _write_nonempty_frames(frames, run_dir=run_dir, artifacts=artifacts)


def _write_factor_diagnostics_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    result = ctx.get("factor_diagnostics")
    payload = _diagnostic_payload(
        result,
        frame_fields=(
            "by_factor",
            "by_factor_date",
            "style_exposure",
            "size_bucket",
            "industry",
            "residual_ic",
            "correlation",
            "drift",
        ),
    )
    if payload is None:
        return
    summary, result_frames = payload
    summary_path = run_dir / "factor_diagnostics_summary.json"
    save_json(dict(summary), summary_path)
    artifacts["factor_diagnostics_summary_path"] = summary_path
    frames = {
        "factor_diagnostics_by_factor_path": (
            result_frames["by_factor"],
            "factor_diagnostics_by_factor.csv",
        ),
        "factor_diagnostics_by_factor_date_path": (
            result_frames["by_factor_date"],
            "factor_diagnostics_by_factor_date.csv",
        ),
        "factor_diagnostics_style_exposure_path": (
            result_frames["style_exposure"],
            "factor_diagnostics_style_exposure.csv",
        ),
        "factor_diagnostics_size_bucket_path": (
            result_frames["size_bucket"],
            "factor_diagnostics_size_bucket.csv",
        ),
        "factor_diagnostics_industry_path": (
            result_frames["industry"],
            "factor_diagnostics_industry.csv",
        ),
        "factor_diagnostics_residual_ic_path": (
            result_frames["residual_ic"],
            "factor_diagnostics_residual_ic.csv",
        ),
        "factor_diagnostics_correlation_path": (
            result_frames["correlation"],
            "factor_diagnostics_correlation.csv",
        ),
        "factor_diagnostics_drift_path": (
            result_frames["drift"],
            "factor_diagnostics_drift.csv",
        ),
    }
    _write_nonempty_frames(frames, run_dir=run_dir, artifacts=artifacts)


def _diagnostic_payload(
    result: Any,
    *,
    frame_fields: Sequence[str],
) -> tuple[Mapping[str, Any], dict[str, pd.DataFrame]] | None:
    summary = getattr(result, "summary", None)
    if not isinstance(summary, Mapping):
        return None

    frames: dict[str, pd.DataFrame] = {}
    for field in frame_fields:
        frame = getattr(result, field, None)
        if not isinstance(frame, pd.DataFrame):
            return None
        frames[field] = frame
    return summary, frames


def _write_nonempty_frames(
    frames: Mapping[str, tuple[Any, str]],
    *,
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    for key, (frame, filename) in frames.items():
        if frame.empty:
            continue
        path = run_dir / filename
        save_frame(frame, path)
        artifacts[key] = path
