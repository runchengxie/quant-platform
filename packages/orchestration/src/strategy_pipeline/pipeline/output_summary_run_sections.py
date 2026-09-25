"""Run configuration, input data, and model summary sections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from strategy_pipeline.pipeline.output_summary_formatting import (
    _date_bounds_text,
    _path_text,
)


def _build_run_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": ctx["run_name"],
        "timestamp": ctx["run_stamp"],
        "config_hash": ctx["run_hash"],
        "config_path": _path_text(ctx["config_path"]),
        "config_source": ctx["config_source"],
        "model_type": ctx["MODEL_TYPE"],
        "sample_weight_mode": ctx["SAMPLE_WEIGHT_MODE"],
        "sample_weight_params": ctx["SAMPLE_WEIGHT_PARAMS"],
        "train_window": {
            "mode": ctx["TRAIN_WINDOW_MODE"],
            "size": ctx["TRAIN_WINDOW_SIZE"],
            "unit": ctx["TRAIN_WINDOW_UNIT"],
        },
        "output_dir": str(ctx["run_dir"]),
        "log_file": _path_text(ctx["active_log_file"]),
    }


def _build_data_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "market": ctx["MARKET"],
        "provider": ctx["provider"],
        "start_date": ctx["START_DATE"],
        "end_date": ctx["END_DATE"],
        "price_col": ctx["PRICE_COL"],
        "price_col_diagnostics": ctx["price_col_diagnostics"],
        "symbols": len(ctx["symbols"]),
        "rows": len(ctx["df_full"]),
        "rows_model": len(ctx["df_model_all"]),
        "rows_model_in_sample": len(ctx["df_model"]),
        "rows_model_oos": len(ctx["df_model_oos"]) if ctx["FINAL_OOS_ENABLED"] else 0,
        "min_symbols_per_date": ctx["MIN_SYMBOLS_PER_DATE"],
        "dropped_dates": int(ctx["dropped_date_counts"].shape[0]),
    }


def _build_dataset_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    dataset = ctx["dataset"]
    section = {
        "schema": dataset.schema.to_dict() if dataset is not None else None,
        "rows": len(dataset.frame) if dataset is not None else 0,
        "file": _path_text(art["dataset_path"]),
        "index": [dataset.schema.date_col, dataset.schema.instrument_col]
        if dataset is not None
        else None,
    }
    lifecycle = ctx.get("dataset_lifecycle")
    if isinstance(lifecycle, Mapping):
        section["lifecycle"] = dict(lifecycle)
        section["learn_rows"] = lifecycle.get("learn_rows")
        section["infer_rows"] = lifecycle.get("infer_rows")
        section["processors"] = lifecycle.get("processors", [])
    return section


def _build_signal_artifact_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    summary = art.get("signals_summary")
    if isinstance(summary, Mapping):
        return {
            "canonical": dict(summary),
            "persistence": "written",
            "legacy_eval_scored_file": _path_text(art["eval_scored_path"]),
        }
    artifacts_enabled = bool(ctx.get("SAVE_ARTIFACTS"))
    signal_enabled = bool(ctx.get("SAVE_SIGNAL_ARTIFACT"))
    return {
        "canonical": {
            "schema_version": 1,
            "file": None,
            "metadata_file": None,
            "rows": 0,
            "score_columns": [],
        },
        "persistence": "disabled"
        if not artifacts_enabled or not signal_enabled
        else "not_available",
        "legacy_eval_scored_file": _path_text(art["eval_scored_path"]),
    }


def _build_model_detail_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    importance_df = ctx.get("importance_df")
    top_features: list[dict[str, Any]] = []
    if isinstance(importance_df, pd.DataFrame) and not importance_df.empty:
        for _, row in importance_df.head(20).iterrows():
            top_features.append(
                {
                    "feature": str(row["feature"]),
                    "importance": float(row["importance"]),
                }
            )
    return {
        "model_type": ctx["MODEL_TYPE"],
        "params": dict(ctx["MODEL_PARAMS"]),
        "model_version": f"{ctx['MODEL_TYPE']}:{ctx['run_hash']}",
        "feature_set_id": ctx.get("feature_set_id") or ctx["run_hash"],
        "feature_importance_source": ctx["importance_source"],
        "top_features": top_features,
        "constant_prediction": ctx["constant_prediction"],
        "zero_feature_importance": ctx["zero_feature_importance"],
        "train_ic": ctx["train_ic_stats"] if ctx["REPORT_TRAIN_IC"] else None,
        "cv_ic": ctx["cv_stats"],
        "test_ic": ctx["ic_stats"],
        "degradation_reasons": [
            reason
            for reason, enabled in (
                ("constant_prediction", bool(ctx["constant_prediction"])),
                ("zero_feature_importance", bool(ctx["zero_feature_importance"])),
            )
            if enabled
        ],
    }


def _build_universe_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mode": ctx["universe_mode_effective"],
        "by_date_file": _path_text(ctx["by_date_file"]),
        "require_by_date": ctx["REQUIRE_BY_DATE"],
        "drop_suspended": ctx["DROP_SUSPENDED"],
        "drop_limit_up": ctx["DROP_LIMIT_UP"],
        "drop_limit_down": ctx["DROP_LIMIT_DOWN"],
        "suspended_policy": ctx["SUSPENDED_POLICY"],
    }


def _build_label_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "horizon_days": ctx["LABEL_HORIZON_DAYS"],
        "horizon_days_effective": ctx["label_horizon_effective"],
        "horizon_mode": ctx["LABEL_HORIZON_MODE"],
        "rebalance_frequency": ctx["LABEL_REBALANCE_FREQUENCY"],
        "shift_days": ctx["LABEL_SHIFT_DAYS"],
        "winsorize_pct": ctx["WINSORIZE_PCT"],
        "train_target_transform": ctx["TRAIN_TARGET_TRANSFORM"],
        "train_target_group_cols": ctx["TRAIN_TARGET_GROUP_COLS"],
    }


def _build_split_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    rebalance_gap_days = None
    if (
        ctx["SAMPLE_ON_REBALANCE_DATES"]
        and ctx["rebalance_gap_days"] is not None
        and np.isfinite(ctx["rebalance_gap_days"])
    ):
        rebalance_gap_days = float(ctx["rebalance_gap_days"])

    return {
        "train_dates": len(ctx["train_dates"]),
        "train_dates_raw": len(ctx["train_dates_full"]),
        "test_dates": len(ctx["test_dates"]),
        "train_window_dates": _date_bounds_text(ctx["train_dates"]),
        "test_window_dates": _date_bounds_text(ctx["test_dates"]),
        "purge_days": ctx["purge_days"],
        "embargo_days": ctx["embargo_days"],
        "purge_steps": ctx["PURGE_STEPS"],
        "embargo_steps": ctx["EMBARGO_STEPS"],
        "cv_purge_mode": ctx.get("CV_PURGE_MODE", "gap"),
        "train_window": {
            "mode": ctx["TRAIN_WINDOW_MODE"],
            "size": ctx["TRAIN_WINDOW_SIZE"],
            "unit": ctx["TRAIN_WINDOW_UNIT"],
            "applied": bool(
                ctx["TRAIN_WINDOW_MODE"] == "rolling"
                and len(ctx["train_dates"]) < len(ctx["train_dates_full"])
            ),
        },
        "rebalance_gap_days": rebalance_gap_days,
    }
