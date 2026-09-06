from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd
from alpha_research.signal_artifact import CANONICAL_SIGNAL_FILE, write_signal_artifact
from portfolio_backtester.backtest_contracts import (
    assert_backtest_periods_frame,
    assert_backtest_return_frame,
    build_backtest_periods_frame,
    build_backtest_return_frame,
)
from portfolio_backtester.position_outputs import write_position_outputs
from portfolio_backtester.position_postprocess_outputs import (
    write_position_postprocess_outputs,
)
from portfolio_backtester.reporting import (
    build_backtest_layer_comparison_frame,
    build_backtest_report,
    build_benchmark_compare_entry,
    build_benchmark_compare_summary_frame,
    slugify_report_name,
)
from portfolio_backtester.tearsheet import write_backtest_tearsheet

from .diagnostic_artifacts import (
    _write_factor_diagnostics_artifacts,
    _write_signal_stability_artifacts,
    _write_turnover_attribution_artifacts,
)
from .support import save_frame, save_parquet, save_series

_write_position_outputs = write_position_outputs


def write_run_artifacts(*, context: Mapping[str, Any]) -> dict[str, Any]:
    ctx = context
    run_dir = ctx["run_dir"]
    artifacts = _initial_artifacts()

    _write_dataset_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_feature_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_eval_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_final_oos_eval_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_dropped_date_artifacts(ctx=ctx, run_dir=run_dir)
    _write_backtest_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_backtest_oos_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_position_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_turnover_attribution_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_signal_stability_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_factor_diagnostics_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_promotion_sidecar_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_auxiliary_artifacts(ctx=ctx, run_dir=run_dir)

    return artifacts


def _initial_artifacts() -> dict[str, Any]:
    return {
        "rolling_ic_files": {},
        "rolling_sharpe_files": {},
        "rolling_ic_oos_files": {},
        "rolling_sharpe_oos_files": {},
        "recency_diagnostics_path": None,
        "recency_diagnostics_oos_path": None,
        "bucket_ic_path": None,
        "bucket_ic_oos_path": None,
        "walk_forward_importance_path": None,
        "walk_forward_feature_stability_path": None,
        "dataset_path": None,
        "pricing_path": None,
        "signals_path": None,
        "signals_meta_path": None,
        "signals_summary": None,
        "eval_scored_path": None,
        "feature_importance_path": None,
        "positions_by_rebalance_path": None,
        "positions_current_path": None,
        "positions_by_rebalance_oos_path": None,
        "positions_current_oos_path": None,
        "positions_by_rebalance_live_path": None,
        "positions_current_live_path": None,
        "positions_diff_path": None,
        "positions_diff_oos_path": None,
        "positions_diff_live_path": None,
        "backtest_style_exposure_path": None,
        "backtest_industry_exposure_path": None,
        "backtest_active_exposure_summary_path": None,
        "ideal_daily_nav_daily_path": None,
        "ideal_daily_nav_orders_path": None,
        "ideal_daily_nav_fills_path": None,
        "execution_sim_orders_path": None,
        "execution_sim_fills_path": None,
        "execution_sim_executed_daily_path": None,
        "promotion_sidecar_events_path": None,
        "promotion_sidecar_orders_path": None,
        "promotion_sidecar_fills_path": None,
        "promotion_sidecar_positions_path": None,
        "promotion_sidecar_cash_path": None,
        "promotion_sidecar_violations_path": None,
        "backtest_layer_comparison_path": None,
        "backtest_report_path": None,
        "backtest_tearsheet_path": None,
        "backtest_benchmark_compare_summary_path": None,
        "backtest_benchmark_compare_entries": [],
        "backtest_style_exposure_oos_path": None,
        "backtest_industry_exposure_oos_path": None,
        "backtest_active_exposure_summary_oos_path": None,
        "backtest_report_oos_path": None,
        "backtest_tearsheet_oos_path": None,
        "backtest_benchmark_compare_summary_oos_path": None,
        "backtest_benchmark_compare_oos_entries": [],
        "turnover_attribution_summary_path": None,
        "turnover_attribution_window_path": None,
        "turnover_attribution_industry_path": None,
        "turnover_attribution_feature_path": None,
        "turnover_attribution_regime_path": None,
        "signal_stability_summary_path": None,
        "signal_stability_window_path": None,
        "signal_stability_symbol_path": None,
        "signal_stability_feature_path": None,
        "factor_diagnostics_summary_path": None,
        "factor_diagnostics_by_factor_path": None,
        "factor_diagnostics_by_factor_date_path": None,
        "factor_diagnostics_style_exposure_path": None,
        "factor_diagnostics_size_bucket_path": None,
        "factor_diagnostics_industry_path": None,
        "factor_diagnostics_residual_ic_path": None,
        "factor_diagnostics_correlation_path": None,
        "factor_diagnostics_drift_path": None,
        "live_positions_file": None,
        "live_current_file": None,
    }


def _write_dataset_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if ctx["SAVE_DATASET"]:
        artifacts["dataset_path"] = run_dir / "dataset.parquet"
        save_parquet(ctx["dataset"].as_multiindex(), artifacts["dataset_path"])
    if ctx.get("SAVE_PRICING_ARTIFACT", False):
        pricing = ctx.get("backtest_pricing_df")
        if pricing is not None and not pricing.empty:
            artifacts["pricing_path"] = run_dir / "backtest_pricing.parquet"
            save_parquet(pricing, artifacts["pricing_path"])
    if (
        ctx["SAVE_SIGNAL_ARTIFACT"]
        and ctx["eval_scored_data"] is not None
        and not ctx["eval_scored_data"].empty
    ):
        artifacts["signals_path"] = run_dir / CANONICAL_SIGNAL_FILE
        model_version = f"{ctx['MODEL_TYPE']}:{ctx['run_hash']}"
        feature_set_id = ctx.get("feature_set_id") or ctx["run_hash"]
        _, signal_summary = write_signal_artifact(
            ctx["eval_scored_data"],
            artifacts["signals_path"],
            metadata={
                "run_name": ctx["run_name"],
                "run_hash": ctx["run_hash"],
                "model_type": ctx["MODEL_TYPE"],
                "features": ctx["features"],
            },
            model_version=model_version,
            feature_set_id=feature_set_id,
            signal_direction=ctx.get("SIGNAL_DIRECTION"),
            eligible_for_backtest=bool(ctx["BACKTEST_ENABLED"]),
            eligible_for_live=bool(ctx["LIVE_ENABLED"]),
        )
        artifacts["signals_meta_path"] = artifacts["signals_path"].with_name("signals.meta.json")
        artifacts["signals_summary"] = signal_summary
    if (
        ctx["SAVE_SCORED_ARTIFACT"]
        and ctx["eval_scored_data"] is not None
        and not ctx["eval_scored_data"].empty
    ):
        artifacts["eval_scored_path"] = run_dir / "eval_scored.parquet"
        save_parquet(ctx["eval_scored_data"], artifacts["eval_scored_path"])


def _write_feature_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    artifacts["feature_importance_path"] = run_dir / "feature_importance.csv"
    save_frame(ctx["importance_df"], artifacts["feature_importance_path"])
    if not ctx["walk_forward_importance_df"].empty:
        artifacts["walk_forward_importance_path"] = run_dir / "walk_forward_feature_importance.csv"
        save_frame(
            ctx["walk_forward_importance_df"],
            artifacts["walk_forward_importance_path"],
        )
    if not ctx["walk_forward_feature_stability_df"].empty:
        artifacts["walk_forward_feature_stability_path"] = (
            run_dir / "walk_forward_feature_stability.csv"
        )
        save_frame(
            ctx["walk_forward_feature_stability_df"],
            artifacts["walk_forward_feature_stability_path"],
        )


def _write_eval_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    save_series(ctx["ic_series"], run_dir / "ic_test.csv", value_name="ic")
    save_series(
        ctx["pearson_ic_series"],
        run_dir / "ic_pearson_test.csv",
        value_name="ic",
    )
    if ctx["REPORT_TRAIN_IC"]:
        save_series(ctx["train_ic_series"], run_dir / "ic_train.csv", value_name="ic")
        save_series(
            ctx["train_pearson_ic_series"],
            run_dir / "ic_pearson_train.csv",
            value_name="ic",
        )
    if not ctx["quantile_ts"].empty:
        save_frame(ctx["quantile_ts"].reset_index(), run_dir / "quantile_returns.csv")
    save_series(
        ctx["turnover_series"],
        run_dir / "turnover_eval.csv",
        value_name="turnover",
    )
    if ctx["bucket_ic_records"]:
        artifacts["bucket_ic_path"] = run_dir / "bucket_ic.csv"
        save_frame(pd.DataFrame(ctx["bucket_ic_records"]), artifacts["bucket_ic_path"])
    if not ctx["recency_diagnostics"].empty:
        artifacts["recency_diagnostics_path"] = run_dir / "recency_diagnostics.csv"
        save_frame(ctx["recency_diagnostics"], artifacts["recency_diagnostics_path"])

    _write_rolling_artifacts(
        results=ctx["rolling_ic_results"],
        run_dir=run_dir,
        filename_template="ic_rolling_{label}.csv",
        artifacts=artifacts,
        artifacts_key="rolling_ic_files",
    )
    _write_rolling_artifacts(
        results=ctx["rolling_sharpe_results"],
        run_dir=run_dir,
        filename_template="backtest_rolling_sharpe_{label}.csv",
        artifacts=artifacts,
        artifacts_key="rolling_sharpe_files",
    )


def _write_final_oos_eval_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if ctx["final_oos_eval"] is not None:
        save_series(ctx["ic_series_oos"], run_dir / "ic_oos.csv", value_name="ic")
        save_series(
            ctx["pearson_ic_series_oos"],
            run_dir / "ic_pearson_oos.csv",
            value_name="ic",
        )
        if not ctx["quantile_ts_oos"].empty:
            save_frame(
                ctx["quantile_ts_oos"].reset_index(),
                run_dir / "quantile_returns_oos.csv",
            )
        save_series(
            ctx["turnover_series_oos"],
            run_dir / "turnover_eval_oos.csv",
            value_name="turnover",
        )
        if ctx["bucket_ic_records_oos"]:
            artifacts["bucket_ic_oos_path"] = run_dir / "bucket_ic_oos.csv"
            save_frame(
                pd.DataFrame(ctx["bucket_ic_records_oos"]),
                artifacts["bucket_ic_oos_path"],
            )
        if not ctx["recency_diagnostics_oos"].empty:
            artifacts["recency_diagnostics_oos_path"] = run_dir / "recency_diagnostics_oos.csv"
            save_frame(
                ctx["recency_diagnostics_oos"],
                artifacts["recency_diagnostics_oos_path"],
            )
        _write_rolling_artifacts(
            results=ctx["rolling_ic_oos_results"],
            run_dir=run_dir,
            filename_template="ic_rolling_{label}_oos.csv",
            artifacts=artifacts,
            artifacts_key="rolling_ic_oos_files",
        )
        _write_rolling_artifacts(
            results=ctx["rolling_sharpe_oos_results"],
            run_dir=run_dir,
            filename_template="backtest_rolling_sharpe_{label}_oos.csv",
            artifacts=artifacts,
            artifacts_key="rolling_sharpe_oos_files",
        )


def _write_rolling_artifacts(
    *,
    results: Mapping[str, pd.DataFrame],
    run_dir: Path,
    filename_template: str,
    artifacts: dict[str, Any],
    artifacts_key: str,
) -> None:
    if not results:
        return
    for label, frame in results.items():
        if frame.empty:
            continue
        out = frame.copy()
        out.index.name = "trade_date"
        path = run_dir / filename_template.format(label=label)
        save_frame(out.reset_index(), path)
        artifacts[artifacts_key][label] = str(path)


def _write_dropped_date_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
) -> None:
    if not ctx["dropped_date_counts"].empty:
        save_frame(
            ctx["dropped_date_counts"].rename("symbol_count").reset_index(),
            run_dir / "dropped_dates.csv",
        )


def _write_backtest_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if ctx["bt_stats"] is None:
        return

    _write_primary_backtest_series(ctx=ctx, run_dir=run_dir)
    _write_primary_backtest_exposures(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    write_position_postprocess_outputs(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_primary_execution_nav_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
    _write_primary_backtest_reports(ctx=ctx, run_dir=run_dir, artifacts=artifacts)

    (
        artifacts["backtest_benchmark_compare_entries"],
        artifacts["backtest_benchmark_compare_summary_path"],
    ) = _write_benchmark_compare_outputs(
        compare_specs=ctx.get("benchmark_compare_specs") or [],
        strategy_returns=ctx["bt_net_series"],
        period_info=ctx["bt_periods"],
        trading_days_per_year=ctx["BACKTEST_TRADING_DAYS_PER_YEAR"],
        entry_price_col=ctx["execution_model"].entry_policy.price_col,
        exit_price_col=ctx["execution_model"].exit_policy.price_col,
        primary_benchmark_symbol=ctx.get("benchmark_symbol"),
        primary_returns_file_path=ctx.get("benchmark_returns_file_path"),
        run_dir=run_dir,
        summary_filename="backtest_benchmark_compare_summary.csv",
        report_prefix="backtest_benchmark_compare",
    )


def _write_primary_backtest_series(*, ctx: Mapping[str, Any], run_dir: Path) -> None:
    _save_backtest_return_series(
        ctx["bt_net_series"], run_dir / "backtest_net.csv", value_name="net_return"
    )
    _save_backtest_return_series(
        ctx["bt_gross_series"], run_dir / "backtest_gross.csv", value_name="gross_return"
    )
    _save_backtest_return_series(
        ctx["bt_turnover_series"],
        run_dir / "backtest_turnover.csv",
        value_name="turnover",
    )
    if not ctx["bt_benchmark_series"].empty:
        save_series(
            ctx["bt_benchmark_series"],
            run_dir / "backtest_benchmark.csv",
            value_name="benchmark_return",
        )
    if not ctx["bt_active_series"].empty:
        save_series(
            ctx["bt_active_series"],
            run_dir / "backtest_active.csv",
            value_name="active_return",
        )
    if ctx["bt_periods"]:
        _save_backtest_periods(ctx["bt_periods"], run_dir / "backtest_periods.csv")


def _save_backtest_return_series(series: pd.Series, path: Path, *, value_name: str) -> None:
    frame = build_backtest_return_frame(series, value_column=value_name)
    assert_backtest_return_frame(frame, value_column=value_name)
    save_frame(frame, path)


def _save_backtest_periods(periods: list[dict[str, Any]], path: Path) -> None:
    frame = build_backtest_periods_frame(periods)
    assert_backtest_periods_frame(frame)
    save_frame(frame, path)


def _write_primary_backtest_exposures(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if not ctx["bt_style_exposure"].empty:
        artifacts["backtest_style_exposure_path"] = run_dir / "backtest_style_exposure.csv"
        save_frame(ctx["bt_style_exposure"], artifacts["backtest_style_exposure_path"])
    if not ctx["bt_industry_exposure"].empty:
        artifacts["backtest_industry_exposure_path"] = run_dir / "backtest_industry_exposure.csv"
        save_frame(ctx["bt_industry_exposure"], artifacts["backtest_industry_exposure_path"])
    if not ctx["bt_active_exposure_summary"].empty:
        artifacts["backtest_active_exposure_summary_path"] = (
            run_dir / "backtest_active_exposure_summary.csv"
        )
        save_frame(
            ctx["bt_active_exposure_summary"],
            artifacts["backtest_active_exposure_summary_path"],
        )


def _write_primary_execution_nav_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if not ctx["ideal_daily_nav_daily"].empty:
        artifacts["ideal_daily_nav_daily_path"] = run_dir / "ideal_daily_nav_daily.csv"
        save_frame(ctx["ideal_daily_nav_daily"], artifacts["ideal_daily_nav_daily_path"])
    if not ctx["ideal_daily_nav_orders"].empty:
        artifacts["ideal_daily_nav_orders_path"] = run_dir / "ideal_daily_nav_orders.csv"
        save_frame(ctx["ideal_daily_nav_orders"], artifacts["ideal_daily_nav_orders_path"])
    if not ctx["ideal_daily_nav_fills"].empty:
        artifacts["ideal_daily_nav_fills_path"] = run_dir / "ideal_daily_nav_fills.csv"
        save_frame(ctx["ideal_daily_nav_fills"], artifacts["ideal_daily_nav_fills_path"])
    if not ctx["execution_sim_orders"].empty:
        artifacts["execution_sim_orders_path"] = run_dir / "execution_sim_orders.csv"
        save_frame(ctx["execution_sim_orders"], artifacts["execution_sim_orders_path"])
    if not ctx["execution_sim_fills"].empty:
        artifacts["execution_sim_fills_path"] = run_dir / "execution_sim_fills.csv"
        save_frame(ctx["execution_sim_fills"], artifacts["execution_sim_fills_path"])
    if not ctx["execution_sim_executed_daily"].empty:
        artifacts["execution_sim_executed_daily_path"] = (
            run_dir / "execution_sim_executed_daily.csv"
        )
        save_frame(
            ctx["execution_sim_executed_daily"],
            artifacts["execution_sim_executed_daily_path"],
        )


def _write_primary_backtest_reports(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    primary_report = build_backtest_report(
        strategy_returns=ctx["bt_net_series"],
        periods_per_year=ctx["bt_stats"].get("periods_per_year", float("nan")),
        benchmark_returns=ctx["bt_benchmark_series"]
        if not ctx["bt_benchmark_series"].empty
        else None,
    )
    artifacts["backtest_report_path"] = run_dir / "backtest_report.csv"
    save_frame(primary_report.reset_index(), artifacts["backtest_report_path"])

    layer_comparison = build_backtest_layer_comparison_frame(
        strategy_stats=ctx["bt_stats"],
        ideal_daily_nav_summary=ctx.get("ideal_daily_nav_summary"),
        execution_sim_executed_summary=ctx.get("execution_sim_executed_summary"),
    )
    artifacts["backtest_layer_comparison_path"] = run_dir / "backtest_layer_comparison.csv"
    save_frame(layer_comparison, artifacts["backtest_layer_comparison_path"])

    if ctx["BACKTEST_TEARSHEET_ENABLED"]:
        artifacts["backtest_tearsheet_path"] = run_dir / "backtest_tearsheet.html"
        write_backtest_tearsheet(
            path=artifacts["backtest_tearsheet_path"],
            strategy_returns=ctx["bt_net_series"],
            strategy_stats=ctx["bt_stats"],
            benchmark_returns=ctx["bt_benchmark_series"]
            if not ctx["bt_benchmark_series"].empty
            else None,
            benchmark_stats=ctx["bt_benchmark_stats"],
            active_stats=ctx["bt_active_stats"],
            title=f"{ctx['run_name']} Backtest",
            benchmark_name=_benchmark_display_name(ctx),
            ideal_daily_nav_summary=ctx.get("ideal_daily_nav_summary"),
            ideal_daily_nav_daily=ctx.get("ideal_daily_nav_daily"),
            execution_sim_executed_summary=ctx.get("execution_sim_executed_summary"),
            execution_sim_executed_daily=ctx.get("execution_sim_executed_daily"),
        )


def _write_backtest_oos_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if ctx["bt_stats_oos"] is not None:
        _save_backtest_return_series(
            ctx["bt_net_series_oos"],
            run_dir / "backtest_net_oos.csv",
            value_name="net_return",
        )
        _save_backtest_return_series(
            ctx["bt_gross_series_oos"],
            run_dir / "backtest_gross_oos.csv",
            value_name="gross_return",
        )
        _save_backtest_return_series(
            ctx["bt_turnover_series_oos"],
            run_dir / "backtest_turnover_oos.csv",
            value_name="turnover",
        )
        if not ctx["bt_benchmark_series_oos"].empty:
            save_series(
                ctx["bt_benchmark_series_oos"],
                run_dir / "backtest_benchmark_oos.csv",
                value_name="benchmark_return",
            )
        if not ctx["bt_active_series_oos"].empty:
            save_series(
                ctx["bt_active_series_oos"],
                run_dir / "backtest_active_oos.csv",
                value_name="active_return",
            )
        if ctx["bt_periods_oos"]:
            _save_backtest_periods(ctx["bt_periods_oos"], run_dir / "backtest_periods_oos.csv")
        _write_oos_exposure_artifacts(ctx=ctx, run_dir=run_dir, artifacts=artifacts)
        primary_report_oos = build_backtest_report(
            strategy_returns=ctx["bt_net_series_oos"],
            periods_per_year=ctx["bt_stats_oos"].get("periods_per_year", float("nan")),
            benchmark_returns=ctx["bt_benchmark_series_oos"]
            if not ctx["bt_benchmark_series_oos"].empty
            else None,
        )
        artifacts["backtest_report_oos_path"] = run_dir / "backtest_report_oos.csv"
        save_frame(primary_report_oos.reset_index(), artifacts["backtest_report_oos_path"])
        if ctx["BACKTEST_TEARSHEET_ENABLED"]:
            artifacts["backtest_tearsheet_oos_path"] = run_dir / "backtest_tearsheet_oos.html"
            write_backtest_tearsheet(
                path=artifacts["backtest_tearsheet_oos_path"],
                strategy_returns=ctx["bt_net_series_oos"],
                strategy_stats=ctx["bt_stats_oos"],
                benchmark_returns=ctx["bt_benchmark_series_oos"]
                if not ctx["bt_benchmark_series_oos"].empty
                else None,
                benchmark_stats=ctx["bt_benchmark_stats_oos"],
                active_stats=ctx["bt_active_stats_oos"],
                title=f"{ctx['run_name']} OOS Backtest",
                benchmark_name=_benchmark_display_name(ctx),
            )
        (
            artifacts["backtest_benchmark_compare_oos_entries"],
            artifacts["backtest_benchmark_compare_summary_oos_path"],
        ) = _write_benchmark_compare_outputs(
            compare_specs=ctx.get("benchmark_compare_specs") or [],
            strategy_returns=ctx["bt_net_series_oos"],
            period_info=ctx["bt_periods_oos"],
            trading_days_per_year=ctx["BACKTEST_TRADING_DAYS_PER_YEAR"],
            entry_price_col=ctx["execution_model"].entry_policy.price_col,
            exit_price_col=ctx["execution_model"].exit_policy.price_col,
            primary_benchmark_symbol=ctx.get("benchmark_symbol"),
            primary_returns_file_path=ctx.get("benchmark_returns_file_path"),
            run_dir=run_dir,
            summary_filename="backtest_benchmark_compare_summary_oos.csv",
            report_prefix="backtest_benchmark_compare_oos",
        )


def _write_oos_exposure_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    if not ctx["bt_style_exposure_oos"].empty:
        artifacts["backtest_style_exposure_oos_path"] = run_dir / "backtest_style_exposure_oos.csv"
        save_frame(
            ctx["bt_style_exposure_oos"],
            artifacts["backtest_style_exposure_oos_path"],
        )
    if not ctx["bt_industry_exposure_oos"].empty:
        artifacts["backtest_industry_exposure_oos_path"] = (
            run_dir / "backtest_industry_exposure_oos.csv"
        )
        save_frame(
            ctx["bt_industry_exposure_oos"],
            artifacts["backtest_industry_exposure_oos_path"],
        )
    if not ctx["bt_active_exposure_summary_oos"].empty:
        artifacts["backtest_active_exposure_summary_oos_path"] = (
            run_dir / "backtest_active_exposure_summary_oos.csv"
        )
        save_frame(
            ctx["bt_active_exposure_summary_oos"],
            artifacts["backtest_active_exposure_summary_oos_path"],
        )


def _write_position_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    write_position_outputs(
        positions=ctx["positions_by_rebalance"],
        run_dir=run_dir,
        by_rebalance_name="positions_by_rebalance.csv",
        current_name="positions_current.csv",
        diff_name="rebalance_diff.csv",
        artifacts=artifacts,
        by_rebalance_key="positions_by_rebalance_path",
        current_key="positions_current_path",
        diff_key="positions_diff_path",
        enabled=bool(ctx["BACKTEST_ENABLED"] or not ctx["LIVE_ENABLED"]),
    )
    write_position_outputs(
        positions=ctx["positions_by_rebalance_oos"],
        run_dir=run_dir,
        by_rebalance_name="positions_by_rebalance_oos.csv",
        current_name="positions_current_oos.csv",
        diff_name="rebalance_diff_oos.csv",
        artifacts=artifacts,
        by_rebalance_key="positions_by_rebalance_oos_path",
        current_key="positions_current_oos_path",
        diff_key="positions_diff_oos_path",
        enabled=True,
    )
    write_position_outputs(
        positions=ctx["positions_by_rebalance_live"],
        run_dir=run_dir,
        by_rebalance_name="positions_by_rebalance_live.csv",
        current_name="positions_current_live.csv",
        diff_name="rebalance_diff_live.csv",
        artifacts=artifacts,
        by_rebalance_key="positions_by_rebalance_live_path",
        current_key="positions_current_live_path",
        diff_key="positions_diff_live_path",
        enabled=bool(ctx["LIVE_ENABLED"]),
    )

    if ctx["LIVE_ENABLED"]:
        artifacts["live_positions_file"] = artifacts["positions_by_rebalance_live_path"]
        artifacts["live_current_file"] = artifacts["positions_current_live_path"]


def _write_promotion_sidecar_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
    artifacts: dict[str, Any],
) -> None:
    frames = {
        "events": ctx.get("promotion_sidecar_events"),
        "orders": ctx.get("promotion_sidecar_orders"),
        "fills": ctx.get("promotion_sidecar_fills"),
        "positions": ctx.get("promotion_sidecar_positions"),
        "cash": ctx.get("promotion_sidecar_cash"),
        "violations": ctx.get("promotion_sidecar_violations"),
    }
    for name, frame in frames.items():
        if frame is None or frame.empty:
            continue
        key = f"promotion_sidecar_{name}_path"
        path = run_dir / f"promotion_sidecar_{name}.csv"
        save_frame(frame, path)
        artifacts[key] = path


def _write_auxiliary_artifacts(
    *,
    ctx: Mapping[str, Any],
    run_dir: Path,
) -> None:
    if ctx["walk_forward_results"]:
        save_frame(
            pd.DataFrame(ctx["walk_forward_results"]),
            run_dir / "walk_forward_summary.csv",
        )
    if ctx["perm_stats"] and ctx["perm_stats"].get("scores"):
        save_frame(
            pd.DataFrame({"ic": ctx["perm_stats"]["scores"]}),
            run_dir / "permutation_test.csv",
        )


def _write_benchmark_compare_outputs(
    *,
    compare_specs: list[dict[str, Any]],
    strategy_returns: pd.Series,
    period_info: list[dict[str, Any]],
    trading_days_per_year: int,
    entry_price_col: str,
    exit_price_col: str,
    primary_benchmark_symbol: str | None,
    primary_returns_file_path: Path | None,
    run_dir: Path,
    summary_filename: str,
    report_prefix: str,
) -> tuple[list[dict[str, Any]], Path | None]:
    if not compare_specs:
        return [], None

    report_entries: list[dict[str, Any]] = []
    used_slugs: set[str] = set()
    for spec in compare_specs:
        entry = build_benchmark_compare_entry(
            name=spec["name"],
            source_type=str(spec.get("source_type") or "returns_file"),
            returns_file=(
                str(spec["returns_file_path"])
                if spec.get("returns_file_path") is not None
                else None
            ),
            symbol=str(spec["symbol"]).strip() if spec.get("symbol") else None,
            benchmark_df=spec.get("benchmark_df"),
            benchmark_return_series=spec.get("series"),
            strategy_returns=strategy_returns,
            period_info=period_info,
            trading_days_per_year=trading_days_per_year,
            entry_price_col=entry_price_col,
            exit_price_col=exit_price_col,
        )
        slug = slugify_report_name(str(spec["name"]))
        if slug in used_slugs:
            suffix = 2
            while f"{slug}_{suffix}" in used_slugs:
                suffix += 1
            slug = f"{slug}_{suffix}"
        used_slugs.add(slug)

        report_path = run_dir / f"{report_prefix}_{slug}.csv"
        save_frame(entry["report_frame"].reset_index(), report_path)
        report_entries.append(
            {
                "name": entry["name"],
                "source_type": entry["source_type"],
                "returns_file": entry["returns_file"],
                "symbol": entry["symbol"],
                "is_primary": bool(
                    (
                        primary_returns_file_path is not None
                        and entry["returns_file"] is not None
                        and Path(entry["returns_file"]) == primary_returns_file_path
                    )
                    or (
                        primary_benchmark_symbol is not None
                        and entry["symbol"] is not None
                        and entry["symbol"] == primary_benchmark_symbol
                    )
                ),
                "aligned_periods": entry["aligned_periods"],
                "benchmark": entry["benchmark"],
                "active": entry["active"],
                "report_file": str(report_path),
            }
        )

    summary_path = run_dir / summary_filename
    save_frame(build_benchmark_compare_summary_frame(report_entries), summary_path)
    return report_entries, summary_path


def _benchmark_display_name(ctx: Mapping[str, Any]) -> str | None:
    benchmark_symbol = ctx.get("benchmark_symbol")
    if benchmark_symbol:
        return str(benchmark_symbol)
    benchmark_file = ctx.get("benchmark_returns_file_path")
    if benchmark_file:
        return Path(benchmark_file).stem
    return None
