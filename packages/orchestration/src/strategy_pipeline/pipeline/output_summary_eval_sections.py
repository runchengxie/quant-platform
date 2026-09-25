"""Evaluation, backtest, and out-of-sample summary sections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from portfolio_backtester.execution import describe_execution_model
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_signal_stability_summary,
    _build_turnover_attribution_summary,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_backtest_exposure_summary,
    _build_execution_sim_summary,
    _build_ideal_daily_nav_summary,
    _build_position_postprocess_summary,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _date_list_text,
    _date_text,
    _path_text,
)


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
