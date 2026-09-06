from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from portfolio_backtester.execution import describe_execution_model
from portfolio_backtester.execution_sim import describe_execution_sim_config


def _build_backtest_exposure_summary(
    *,
    style_path: Any,
    industry_path: Any,
    active_summary_path: Any,
    style_summary: Mapping[str, Any] | None,
    industry_summary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    style_meta = style_summary if isinstance(style_summary, Mapping) else {}
    industry_meta = industry_summary if isinstance(industry_summary, Mapping) else {}
    latest_rebalance_date = style_meta.get("latest_rebalance_date")
    if latest_rebalance_date is None:
        latest_rebalance_date = industry_meta.get("latest_rebalance_date")
    latest_entry_date = style_meta.get("latest_entry_date")
    if latest_entry_date is None:
        latest_entry_date = industry_meta.get("latest_entry_date")
    return {
        "style_file": str(style_path) if style_path else None,
        "industry_file": str(industry_path) if industry_path else None,
        "active_summary_file": str(active_summary_path) if active_summary_path else None,
        "latest_rebalance_date": latest_rebalance_date,
        "latest_entry_date": latest_entry_date,
        "style_factors": style_meta.get("factors", {}),
        "latest_style": style_meta.get("latest", {}),
        "industry_column": industry_meta.get("industry_column"),
        "latest_industry": industry_meta.get("latest", {}),
    }


def _build_execution_sim_summary(
    *,
    summary: Mapping[str, Any] | None,
    config: Any,
    orders_path: Any,
    fills_path: Any,
    executed_summary: Mapping[str, Any] | None,
    executed_daily_path: Any,
) -> dict[str, Any]:
    if isinstance(summary, Mapping):
        out = dict(summary)
    else:
        out = {
            "enabled": bool(getattr(config, "enabled", False)),
            "status": "not_run" if getattr(config, "enabled", False) else "disabled",
            "config": describe_execution_sim_config(config),
        }
    out["orders_file"] = str(orders_path) if orders_path else None
    out["fills_file"] = str(fills_path) if fills_path else None
    executed: dict[str, Any]
    if isinstance(executed_summary, Mapping):
        executed = dict(executed_summary)
    else:
        executed = {
            "enabled": bool(getattr(config, "enabled", False)),
            "status": "not_run" if getattr(config, "enabled", False) else "disabled",
        }
    executed["daily_file"] = str(executed_daily_path) if executed_daily_path else None
    out["executed"] = executed
    return out


def _build_ideal_daily_nav_summary(
    *,
    summary: Mapping[str, Any] | None,
    daily_path: Any,
    orders_path: Any,
    fills_path: Any,
) -> dict[str, Any]:
    out = dict(summary) if isinstance(summary, Mapping) else {"status": "not_run"}
    out["daily_file"] = str(daily_path) if daily_path else None
    out["orders_file"] = str(orders_path) if orders_path else None
    out["fills_file"] = str(fills_path) if fills_path else None
    return out


def _path_text(value: Any) -> str | None:
    return str(value) if value else None


def _build_position_postprocess_summary(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    raw = ctx.get("position_postprocess")
    summary = dict(raw) if isinstance(raw, Mapping) else {"enabled": False}
    summary["pre_repair_exposure"] = {
        "style_file": _path_text(art.get("position_postprocess_pre_repair_style_path")),
        "industry_file": _path_text(art.get("position_postprocess_pre_repair_industry_path")),
        "active_summary_file": _path_text(
            art.get("position_postprocess_pre_repair_active_summary_path")
        ),
    }
    summary["post_repair_exposure"] = {
        "style_file": _path_text(art["backtest_style_exposure_path"]),
        "industry_file": _path_text(art["backtest_industry_exposure_path"]),
        "active_summary_file": _path_text(art["backtest_active_exposure_summary_path"]),
    }
    summary["breaches_file"] = _path_text(art.get("position_postprocess_breaches_path"))
    return summary


def _date_text(value: Any) -> str | None:
    return value.strftime("%Y%m%d") if value else None


def _date_list_text(values: Any) -> list[str]:
    return [pd.to_datetime(date).strftime("%Y%m%d") for date in values]


def _date_bounds_text(values: Any) -> dict[str, str | None]:
    dates = pd.to_datetime(list(values), errors="coerce")
    dates = dates[~dates.isna()]
    if len(dates) == 0:
        return {"start": None, "end": None}
    return {
        "start": dates.min().strftime("%Y%m%d"),
        "end": dates.max().strftime("%Y%m%d"),
    }


def _json_scalar(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, np.generic):
        return value.item()
    return value


def _frame_records(frame: Any) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    rows: list[dict[str, Any]] = []
    for row in frame.to_dict("records"):
        rows.append({str(key): _json_scalar(value) for key, value in row.items()})
    return rows


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


def _build_eval_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
    quantile_mean: pd.Series,
) -> dict[str, Any]:
    return {
        "ic": ctx["ic_stats"],
        "pearson_ic": ctx["pearson_ic_stats"],
        "train_ic": ctx["train_ic_stats"] if ctx["REPORT_TRAIN_IC"] else None,
        "train_ic_raw": ctx["train_ic_raw_stats"] if ctx["train_ic_raw_stats"] else None,
        "train_pearson_ic": ctx["train_pearson_ic_stats"] if ctx["REPORT_TRAIN_IC"] else None,
        "cv_ic": ctx["cv_stats"],
        "cv_ic_raw": ctx["cv_stats_raw"],
        "signal_direction": ctx["SIGNAL_DIRECTION"],
        "signal_direction_mode": ctx["SIGNAL_DIRECTION_MODE"],
        "error_metrics": ctx["error_metrics"],
        "hit_rate": ctx["hit_rate_stats"],
        "topk_positive_ratio": ctx["topk_positive_stats"],
        "bucket_ic": ctx["bucket_ic_records"],
        "bucket_ic_file": _path_text(art["bucket_ic_path"]),
        "rolling_ic": {
            "windows_months": ctx["ROLLING_WINDOWS_MONTHS"],
            "obs_per_year": ctx["rolling_ic_obs_per_year"],
            "latest": ctx["rolling_ic_latest"],
            "series_files": art["rolling_ic_files"],
        },
        "quantile_mean": quantile_mean.to_dict() if not quantile_mean.empty else {},
        "long_short": float(quantile_mean.iloc[-1] - quantile_mean.iloc[0])
        if not quantile_mean.empty
        else None,
        "turnover_mean": float(ctx["turnover_series"].mean())
        if not ctx["turnover_series"].empty
        else None,
        "turnover_count": int(ctx["turnover_series"].shape[0]),
        "buffer_exit": ctx["EVAL_BUFFER_EXIT"],
        "buffer_entry": ctx["EVAL_BUFFER_ENTRY"],
        "sample_on_rebalance_dates": ctx["SAMPLE_ON_REBALANCE_DATES"],
        "rebalance_frequency": ctx["REBALANCE_FREQUENCY"],
        "rebalance_dates": _date_list_text(ctx["eval_rebalance_dates"]),
        "save_signal_artifact": ctx["SAVE_SIGNAL_ARTIFACT"],
        "save_scored_artifact": ctx["SAVE_SCORED_ARTIFACT"],
        "scored_file": _path_text(art["eval_scored_path"]),
        "scored_pred_col": "pred",
        "scored_signal_col": "signal_eval",
        "scored_signal_backtest_col": "signal_backtest",
        "pred_nunique": ctx["pred_nunique"],
        "constant_prediction": ctx["constant_prediction"],
        "feature_importance_file": _path_text(art["feature_importance_path"]),
        "feature_importance_source": ctx["importance_source"],
        "feature_importance_nonzero": ctx["feature_importance_nonzero"],
        "zero_feature_importance": ctx["zero_feature_importance"],
        "permutation_test": ctx["perm_stats"],
    }


def _build_backtest_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    benchmark_returns_file = None
    if ctx.get("benchmark_returns_file_path") is not None:
        benchmark_returns_file = str(ctx["benchmark_returns_file_path"])

    strategy = ctx.get("strategy_spec")
    return {
        "enabled": ctx["BACKTEST_ENABLED"],
        "exit_mode": ctx["BACKTEST_EXIT_MODE"],
        "exit_horizon_days": ctx["BACKTEST_EXIT_HORIZON_DAYS"],
        "exit_price_policy": ctx["BACKTEST_EXIT_PRICE_POLICY"],
        "exit_fallback_policy": ctx["BACKTEST_EXIT_FALLBACK_POLICY"],
        "buffer_exit": ctx["BACKTEST_BUFFER_EXIT"],
        "buffer_entry": ctx["BACKTEST_BUFFER_ENTRY"],
        "mode": "long_only" if ctx["BACKTEST_LONG_ONLY"] else "long_short",
        "weighting": ctx["BACKTEST_WEIGHTING"],
        "group_col": ctx["BACKTEST_GROUP_COL"],
        "max_names_per_group": ctx["BACKTEST_MAX_NAMES_PER_GROUP"],
        "selection_tiebreak_col": ctx.get("BACKTEST_SELECTION_TIEBREAK_COL"),
        "selection_score_bucket_size": ctx.get("BACKTEST_SELECTION_SCORE_BUCKET_SIZE"),
        "selection_score_margin": ctx.get("BACKTEST_SELECTION_SCORE_MARGIN"),
        "selection_score_margin_rank_limit": ctx.get("BACKTEST_SELECTION_SCORE_MARGIN_RANK_LIMIT"),
        "top_k": ctx["BACKTEST_TOP_K"],
        "short_k": ctx["BACKTEST_SHORT_K"],
        "rebalance_frequency": ctx["BACKTEST_REBALANCE_FREQUENCY"],
        "rebalance_dates": _date_list_text(ctx["backtest_rebalance_dates"]),
        "shift_days": ctx["LABEL_SHIFT_DAYS"],
        "trading_days_per_year": ctx["BACKTEST_TRADING_DAYS_PER_YEAR"],
        "tradable_col": ctx["BACKTEST_TRADABLE_COL"],
        "signal_direction": ctx["BACKTEST_SIGNAL_DIRECTION"],
        "benchmark_symbol": ctx["benchmark_symbol"],
        "benchmark_returns_file": benchmark_returns_file,
        "pricing_file": _path_text(art["pricing_path"]),
        "transaction_cost_bps": ctx["BACKTEST_COST_BPS_REPORT"],
        "execution_source": ctx["BACKTEST_EXECUTION_SOURCE"],
        "strategy": strategy.to_dict() if hasattr(strategy, "to_dict") else None,
        "execution": describe_execution_model(ctx["execution_model"]),
        "position_postprocess": _build_position_postprocess_summary(ctx=ctx, art=art),
        "ideal_daily_nav": _build_ideal_daily_nav_summary(
            summary=ctx.get("ideal_daily_nav_summary"),
            daily_path=art["ideal_daily_nav_daily_path"],
            orders_path=art["ideal_daily_nav_orders_path"],
            fills_path=art["ideal_daily_nav_fills_path"],
        ),
        "execution_sim": _build_execution_sim_summary(
            summary=ctx.get("execution_sim_summary"),
            config=ctx["execution_sim_config"],
            orders_path=art["execution_sim_orders_path"],
            fills_path=art["execution_sim_fills_path"],
            executed_summary=ctx.get("execution_sim_executed_summary"),
            executed_daily_path=art["execution_sim_executed_daily_path"],
        ),
        "stats": ctx["bt_stats"],
        "benchmark": ctx["bt_benchmark_stats"],
        "active": ctx["bt_active_stats"],
        "layer_comparison_file": _path_text(art["backtest_layer_comparison_path"]),
        "report_file": _path_text(art["backtest_report_path"]),
        "tearsheet_file": _path_text(art["backtest_tearsheet_path"]),
        "benchmark_compare": {
            "summary_file": _path_text(art["backtest_benchmark_compare_summary_path"]),
            "benchmarks": art["backtest_benchmark_compare_entries"],
        },
        "exposure": _build_backtest_exposure_summary(
            style_path=art["backtest_style_exposure_path"],
            industry_path=art["backtest_industry_exposure_path"],
            active_summary_path=art["backtest_active_exposure_summary_path"],
            style_summary=ctx.get("bt_style_exposure_summary"),
            industry_summary=ctx.get("bt_industry_exposure_summary"),
        ),
        "rolling_sharpe": {
            "windows_months": ctx["ROLLING_WINDOWS_MONTHS"],
            "latest": ctx["rolling_sharpe_latest"],
            "series_files": art["rolling_sharpe_files"],
        },
    }


def _build_oos_backtest_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "stats": ctx["bt_stats_oos"],
        "benchmark": ctx["bt_benchmark_stats_oos"],
        "active": ctx["bt_active_stats_oos"],
        "report_file": _path_text(art["backtest_report_oos_path"]),
        "tearsheet_file": _path_text(art["backtest_tearsheet_oos_path"]),
        "benchmark_compare": {
            "summary_file": _path_text(art["backtest_benchmark_compare_summary_oos_path"]),
            "benchmarks": art["backtest_benchmark_compare_oos_entries"],
        },
        "exposure": _build_backtest_exposure_summary(
            style_path=art["backtest_style_exposure_oos_path"],
            industry_path=art["backtest_industry_exposure_oos_path"],
            active_summary_path=art["backtest_active_exposure_summary_oos_path"],
            style_summary=ctx.get("bt_style_exposure_summary_oos"),
            industry_summary=ctx.get("bt_industry_exposure_summary_oos"),
        ),
        "rolling_sharpe": {
            "windows_months": ctx["ROLLING_WINDOWS_MONTHS"],
            "latest": ctx["rolling_sharpe_latest_oos"],
            "series_files": art["rolling_sharpe_oos_files"],
        },
    }


def _build_oos_positions_section(art: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "by_rebalance_file": _path_text(art["positions_by_rebalance_oos_path"]),
        "current_file": _path_text(art["positions_current_oos_path"]),
        "diff_file": _path_text(art["positions_diff_oos_path"]),
    }


def _build_final_oos_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
    quantile_mean_oos: pd.Series,
) -> dict[str, Any]:
    has_oos_eval = ctx["final_oos_eval"] is not None

    return {
        "enabled": ctx["FINAL_OOS_ENABLED"],
        "size": ctx["FINAL_OOS_SIZE_RAW"],
        "dates": int(ctx["final_oos_len"]) if ctx["FINAL_OOS_ENABLED"] else 0,
        "start": _date_text(ctx["final_oos_start"]),
        "end": _date_text(ctx["final_oos_end"]),
        "ic": ctx["ic_stats_oos"] if has_oos_eval else None,
        "pearson_ic": ctx["pearson_ic_stats_oos"] if has_oos_eval else None,
        "error_metrics": ctx["error_metrics_oos"] if has_oos_eval else None,
        "hit_rate": ctx["hit_rate_stats_oos"] if has_oos_eval else None,
        "topk_positive_ratio": ctx["topk_positive_stats_oos"] if has_oos_eval else None,
        "bucket_ic": ctx["bucket_ic_records_oos"] if has_oos_eval else None,
        "bucket_ic_file": _path_text(art["bucket_ic_oos_path"]),
        "rolling_ic": {
            "windows_months": ctx["ROLLING_WINDOWS_MONTHS"],
            "obs_per_year": ctx["rolling_ic_oos_obs_per_year"],
            "latest": ctx["rolling_ic_latest_oos"],
            "series_files": art["rolling_ic_oos_files"],
        }
        if has_oos_eval
        else None,
        "quantile_mean": quantile_mean_oos.to_dict()
        if has_oos_eval and not quantile_mean_oos.empty
        else {},
        "long_short": float(quantile_mean_oos.iloc[-1] - quantile_mean_oos.iloc[0])
        if has_oos_eval and not quantile_mean_oos.empty
        else None,
        "turnover_mean": float(ctx["turnover_series_oos"].mean())
        if has_oos_eval and not ctx["turnover_series_oos"].empty
        else None,
        "turnover_count": int(ctx["turnover_series_oos"].shape[0]) if has_oos_eval else 0,
        "backtest": _build_oos_backtest_section(ctx=ctx, art=art) if has_oos_eval else None,
        "positions": _build_oos_positions_section(art) if has_oos_eval else None,
        "turnover_attribution": _build_turnover_attribution_summary(art=art),
        "signal_stability": _build_signal_stability_summary(art=art),
    }


def _build_recency_diagnostics_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "windows": ctx["RECENCY_WINDOWS"],
        "guidance": {
            "6m": "current_effectiveness",
            "1m": "watch_signal",
            "1w": "monitoring_only",
        },
        "test": {
            "file": _path_text(art["recency_diagnostics_path"]),
            "rows": _frame_records(ctx.get("recency_diagnostics")),
        },
        "final_oos": {
            "file": _path_text(art["recency_diagnostics_oos_path"]),
            "rows": _frame_records(ctx.get("recency_diagnostics_oos")),
        },
    }


def _build_turnover_attribution_summary(*, art: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "summary_file": _path_text(art["turnover_attribution_summary_path"]),
        "by_window_file": _path_text(art["turnover_attribution_window_path"]),
        "by_industry_file": _path_text(art["turnover_attribution_industry_path"]),
        "by_feature_file": _path_text(art["turnover_attribution_feature_path"]),
        "by_regime_file": _path_text(art["turnover_attribution_regime_path"]),
    }


def _build_signal_stability_summary(*, art: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "summary_file": _path_text(art["signal_stability_summary_path"]),
        "by_window_file": _path_text(art["signal_stability_window_path"]),
        "by_symbol_file": _path_text(art["signal_stability_symbol_path"]),
        "by_feature_file": _path_text(art["signal_stability_feature_path"]),
    }


def _build_factor_diagnostics_summary(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    result = ctx.get("factor_diagnostics")
    result_summary = getattr(result, "summary", None)
    out = dict(result_summary) if isinstance(result_summary, Mapping) else {}
    out.update(
        {
            "summary_file": _path_text(art["factor_diagnostics_summary_path"]),
            "by_factor_file": _path_text(art["factor_diagnostics_by_factor_path"]),
            "by_factor_date_file": _path_text(art["factor_diagnostics_by_factor_date_path"]),
            "style_exposure_file": _path_text(art["factor_diagnostics_style_exposure_path"]),
            "size_bucket_file": _path_text(art["factor_diagnostics_size_bucket_path"]),
            "industry_file": _path_text(art["factor_diagnostics_industry_path"]),
            "residual_ic_file": _path_text(art["factor_diagnostics_residual_ic_path"]),
            "correlation_file": _path_text(art["factor_diagnostics_correlation_path"]),
            "drift_file": _path_text(art["factor_diagnostics_drift_path"]),
        }
    )
    return out


def _build_positions_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    strategy = ctx.get("strategy_spec")
    section = {
        "by_rebalance_file": _path_text(art["positions_by_rebalance_path"]),
        "current_file": _path_text(art["positions_current_path"]),
        "diff_file": _path_text(art["positions_diff_path"]),
        "shift_days": ctx["LABEL_SHIFT_DAYS"],
        "buffer_exit": ctx["BACKTEST_BUFFER_EXIT"],
        "buffer_entry": ctx["BACKTEST_BUFFER_ENTRY"],
        "window_fields": {
            "signal_asof": "signal_asof",
            "entry_date": "entry_date",
            "next_entry_date": "next_entry_date",
            "holding_window": "holding_window",
        },
    }
    if hasattr(strategy, "to_dict"):
        section["strategy"] = {
            **strategy.to_dict(),
            "signals_file": _path_text(art["signals_path"]),
            "positions_file": _path_text(art["positions_by_rebalance_path"]),
        }
    return section


def _build_live_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    live_enabled = ctx["LIVE_ENABLED"]
    return {
        "enabled": live_enabled,
        "as_of": _date_text(ctx["live_as_of"]) if live_enabled else None,
        "signal_asof": _date_text(ctx["live_signal_asof"])
        if live_enabled and ctx.get("live_signal_asof") is not None
        else None,
        "entry_date": _date_text(ctx["live_entry_date"])
        if live_enabled and ctx.get("live_entry_date") is not None
        else None,
        "execution_calendar": ctx.get("live_execution_calendar") if live_enabled else None,
        "execution_open": ctx.get("live_execution_open") if live_enabled else None,
        "execution_status": ctx.get("live_execution_status") if live_enabled else None,
        "train_mode": ctx["LIVE_TRAIN_MODE"] if live_enabled else None,
        "positions_file": _path_text(art["live_positions_file"]),
        "current_file": _path_text(art["live_current_file"]),
        "diff_file": _path_text(art["positions_diff_live_path"]),
        "position_postprocess": ctx.get(
            "live_position_postprocess",
            {"enabled": False},
        ),
    }


def _build_quality_section(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(ctx.get("quality_summary"), Mapping):
        return ctx["quality_summary"]
    return {"preflight": None}


def _build_promotion_sidecar_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    summary = ctx.get("promotion_sidecar_summary")
    if isinstance(summary, Mapping):
        out = dict(summary)
    else:
        out = {"enabled": False, "status": "disabled"}
    out["events_file"] = _path_text(art["promotion_sidecar_events_path"])
    out["orders_file"] = _path_text(art["promotion_sidecar_orders_path"])
    out["fills_file"] = _path_text(art["promotion_sidecar_fills_path"])
    out["positions_file"] = _path_text(art["promotion_sidecar_positions_path"])
    out["cash_file"] = _path_text(art["promotion_sidecar_cash_path"])
    out["violations_file"] = _path_text(art["promotion_sidecar_violations_path"])
    return out


def _build_fundamentals_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    overlay_enabled = ctx["FUNDAMENTALS_PROVIDER_OVERLAY_ENABLED"]
    return {
        "enabled": ctx["FUNDAMENTALS_ENABLED"],
        "source": ctx["FUNDAMENTALS_SOURCE"] if ctx["FUNDAMENTALS_ENABLED"] else None,
        "provider": ctx["FUNDAMENTALS_PROVIDER"] if ctx["FUNDAMENTALS_ENABLED"] else None,
        "file": _path_text(ctx["FUNDAMENTALS_FILE"]),
        "cache_dir": _path_text(ctx["fund_cache_dir"]),
        "features": ctx["FUNDAMENTALS_FEATURES"],
        "log_market_cap": ctx["FUNDAMENTALS_LOG_MCAP"],
        "market_cap_col": ctx["FUNDAMENTALS_MCAP_COL"],
        "provider_overlay": {
            "enabled": overlay_enabled,
            "source": ctx["FUNDAMENTALS_PROVIDER_OVERLAY_SOURCE"] if overlay_enabled else None,
            "provider": ctx["FUNDAMENTALS_PROVIDER_OVERLAY_PROVIDER"] if overlay_enabled else None,
            "cache_dir": _path_text(ctx["provider_overlay_cache_dir"]),
            "features": ctx["FUNDAMENTALS_PROVIDER_OVERLAY_FEATURES"],
        },
    }


def _build_industry_section(ctx: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "enabled": ctx["INDUSTRY_ENABLED"],
        "source": ctx["INDUSTRY_SOURCE"] if ctx["INDUSTRY_ENABLED"] else None,
        "file": _path_text(ctx["INDUSTRY_FILE"]),
        "keep_columns": ctx["INDUSTRY_KEEP_COLUMNS"],
        "resolved_columns": ctx["passthrough_cols"],
        "ffill": ctx["INDUSTRY_FFILL"],
        "ffill_limit": ctx["INDUSTRY_FFILL_LIMIT"],
    }


def _build_walk_forward_section(
    *,
    ctx: Mapping[str, Any],
    art: Mapping[str, Any],
) -> dict[str, Any]:
    stability_df = ctx["walk_forward_feature_stability_df"]
    return {
        "enabled": ctx["WF_ENABLED"],
        "n_windows": ctx["WF_N_WINDOWS"],
        "actual_windows": len(ctx["walk_forward_results"]),
        "test_size": ctx["WF_TEST_SIZE"],
        "step_size": ctx["WF_STEP_SIZE"],
        "anchor_end": ctx["WF_ANCHOR_END"],
        "feature_top_k": ctx["WF_FEATURE_TOP_K"],
        "feature_importance_windows": int(ctx["walk_forward_importance_df"]["window"].nunique())
        if not ctx["walk_forward_importance_df"].empty
        else 0,
        "feature_importance_file": _path_text(art["walk_forward_importance_path"]),
        "feature_stability_file": _path_text(art["walk_forward_feature_stability_path"]),
        "stable_top_features": stability_df["feature"]
        .head(ctx["WF_FEATURE_TOP_K"])
        .astype(str)
        .tolist()
        if not stability_df.empty
        else [],
        "results": ctx["walk_forward_results"],
    }


def build_run_summary_sections(
    *,
    context: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> dict[str, Any]:
    ctx = context
    art = artifacts
    return {
        "run": _build_run_section(ctx),
        "data": _build_data_section(ctx),
        "dataset": _build_dataset_section(ctx=ctx, art=art),
        "signals": _build_signal_artifact_section(ctx=ctx, art=art),
        "model_detail": _build_model_detail_section(ctx),
        "universe": _build_universe_section(ctx),
        "label": _build_label_section(ctx),
        "split": _build_split_section(ctx),
        "eval": _build_eval_section(
            ctx=ctx,
            art=art,
            quantile_mean=ctx["quantile_mean"],
        ),
        "backtest": _build_backtest_section(ctx=ctx, art=art),
        "final_oos": _build_final_oos_section(
            ctx=ctx,
            art=art,
            quantile_mean_oos=ctx["quantile_mean_oos"],
        ),
        "recency_diagnostics": _build_recency_diagnostics_section(ctx=ctx, art=art),
        "factor_diagnostics": _build_factor_diagnostics_summary(ctx=ctx, art=art),
        "positions": _build_positions_section(ctx=ctx, art=art),
        "live": _build_live_section(ctx=ctx, art=art),
        "promotion_sidecar": _build_promotion_sidecar_section(ctx=ctx, art=art),
        "quality": _build_quality_section(ctx),
        "fundamentals": _build_fundamentals_section(ctx),
        "industry": _build_industry_section(ctx),
        "walk_forward": _build_walk_forward_section(ctx=ctx, art=art),
    }
