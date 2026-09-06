from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from alpha_research.period_evaluation import (
    build_scored_data as _build_scored_data_impl,
)
from alpha_research.period_evaluation import (
    score_and_record_period_eval_metrics as _score_and_record_period_eval_metrics_impl,
)
from portfolio_backtester.period_outputs import (
    build_period_positions as _build_period_positions_impl,
)
from portfolio_backtester.period_outputs import (
    record_period_backtest_nav_outputs as _record_period_backtest_nav_outputs_impl,
)
from portfolio_backtester.period_outputs import (
    record_period_exposure_outputs as _record_period_exposure_outputs_impl,
)
from portfolio_backtester.portfolio import build_positions_by_rebalance

logger = logging.getLogger("strategy_pipeline")


def _build_period_positions(
    *,
    eval_df_full: pd.DataFrame,
    bt_rebalance: list[pd.Timestamp],
    context: Mapping[str, Any],
    allow_live_fallback: bool,
) -> tuple[pd.DataFrame | None, dict[str, Any], dict[str, pd.DataFrame]]:
    return _build_period_positions_impl(
        eval_df_full=eval_df_full,
        bt_rebalance=bt_rebalance,
        context=context,
        allow_live_fallback=allow_live_fallback,
        build_positions_by_rebalance_fn=build_positions_by_rebalance,
    )


def _record_period_backtest_nav_outputs(
    result: dict[str, Any],
    *,
    eval_df_full: pd.DataFrame,
    context: Mapping[str, Any],
    label_prefix: str,
    allow_live_fallback: bool,
) -> Any:
    return _record_period_backtest_nav_outputs_impl(
        result,
        eval_df_full=eval_df_full,
        context=context,
        label_prefix=label_prefix,
        allow_live_fallback=allow_live_fallback,
        build_positions_by_rebalance_fn=build_positions_by_rebalance,
    )


def _empty_period_result() -> dict[str, Any]:
    default_series = pd.Series(dtype=float)
    default_frame = pd.DataFrame()
    return {
        "ic_series": default_series,
        "ic_stats": {},
        "pearson_ic_series": default_series,
        "pearson_ic_stats": {},
        "error_metrics": {},
        "hit_rate": {},
        "topk_positive_ratio": {},
        "bucket_ic": [],
        "quantile_ts": default_frame,
        "quantile_mean": default_series,
        "turnover_series": default_series,
        "positions_by_rebalance": None,
        "position_postprocess": {"enabled": False},
        "position_postprocess_artifacts": {},
        "bt_stats": None,
        "bt_net_series": pd.Series(dtype=float, name="net_return"),
        "bt_gross_series": pd.Series(dtype=float, name="gross_return"),
        "bt_turnover_series": pd.Series(dtype=float, name="turnover"),
        "bt_benchmark_series": pd.Series(dtype=float, name="benchmark_return"),
        "bt_active_series": pd.Series(dtype=float, name="active_return"),
        "bt_benchmark_stats": None,
        "bt_active_stats": None,
        "bt_periods": [],
        "bt_style_exposure": default_frame,
        "bt_style_exposure_summary": {},
        "bt_industry_exposure": default_frame,
        "bt_industry_exposure_summary": {},
        "bt_active_exposure_summary": default_frame,
        "ideal_daily_nav_summary": None,
        "ideal_daily_nav_daily": default_frame,
        "ideal_daily_nav_orders": default_frame,
        "ideal_daily_nav_fills": default_frame,
        "execution_sim_summary": None,
        "execution_sim_orders": default_frame,
        "execution_sim_fills": default_frame,
        "execution_sim_executed_summary": None,
        "execution_sim_executed_daily": default_frame,
        "perm_stats": None,
        "scored_data": default_frame,
        "eval_rebalance_dates": [],
        "backtest_rebalance_dates": [],
    }


def _record_period_scored_data_and_exposure(
    result: dict[str, Any],
    *,
    eval_df_full: pd.DataFrame,
    positions_by_rebalance: Any,
    context: Mapping[str, Any],
) -> None:
    result["scored_data"] = _build_scored_data_impl(
        eval_df_full,
        price_col=context["price_col"],
        target=context["target"],
        price_passthrough_cols=context.get("price_passthrough_cols", []),
        passthrough_cols=context["passthrough_cols"],
        bucket_cols=context["bucket_cols"],
        feature_cols=context["features"],
        backtest_tradable_col=context["backtest_tradable_col"],
    )
    _record_period_exposure_outputs_impl(
        result,
        eval_df_full=eval_df_full,
        positions_by_rebalance=positions_by_rebalance,
        context=context,
    )


def _evaluate_period(
    label: str,
    model_eval: Any,
    test_df_full: pd.DataFrame,
    test_dates: np.ndarray,
    *,
    context: Mapping[str, Any],
    run_perm_test: bool,
    perm_train_df: pd.DataFrame | None = None,
    perm_test_df: pd.DataFrame | None = None,
    allow_live_fallback: bool = True,
) -> dict[str, Any]:
    label_prefix = f"[{label}] " if label else ""
    result = _empty_period_result()
    if test_df_full is None or test_df_full.empty:
        logger.info("%sEvaluation skipped: no data.", label_prefix)
        return result

    eval_df_full = _score_and_record_period_eval_metrics_impl(
        result,
        test_df_full=test_df_full,
        model_eval=model_eval,
        test_dates=test_dates,
        context=context,
        label_prefix=label_prefix,
        run_perm_test=run_perm_test,
        perm_train_df=perm_train_df,
        perm_test_df=perm_test_df,
    )
    positions_by_rebalance = _record_period_backtest_nav_outputs(
        result,
        eval_df_full=eval_df_full,
        context=context,
        label_prefix=label_prefix,
        allow_live_fallback=allow_live_fallback,
    )
    _record_period_scored_data_and_exposure(
        result,
        eval_df_full=eval_df_full,
        positions_by_rebalance=positions_by_rebalance,
        context=context,
    )
    return result
