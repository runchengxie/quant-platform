from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_factor_diagnostics_summary as _build_factor_diagnostics_summary,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_fundamentals_section as _build_fundamentals_section,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_industry_section as _build_industry_section,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_promotion_sidecar_section as _build_promotion_sidecar_section,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_quality_section as _build_quality_section,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_recency_diagnostics_section as _build_recency_diagnostics_section,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_signal_stability_summary as _build_signal_stability_summary,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_turnover_attribution_summary as _build_turnover_attribution_summary,
)
from strategy_pipeline.pipeline.output_summary_diagnostic_sections import (
    _build_walk_forward_section as _build_walk_forward_section,
)
from strategy_pipeline.pipeline.output_summary_eval_sections import (
    _build_backtest_section as _build_backtest_section,
)
from strategy_pipeline.pipeline.output_summary_eval_sections import (
    _build_eval_section as _build_eval_section,
)
from strategy_pipeline.pipeline.output_summary_eval_sections import (
    _build_final_oos_section as _build_final_oos_section,
)
from strategy_pipeline.pipeline.output_summary_eval_sections import (
    _build_oos_backtest_section as _build_oos_backtest_section,
)
from strategy_pipeline.pipeline.output_summary_eval_sections import (
    _build_oos_positions_section as _build_oos_positions_section,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_backtest_exposure_summary as _build_backtest_exposure_summary,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_execution_sim_summary as _build_execution_sim_summary,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_ideal_daily_nav_summary as _build_ideal_daily_nav_summary,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_live_section as _build_live_section,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_position_postprocess_summary as _build_position_postprocess_summary,
)
from strategy_pipeline.pipeline.output_summary_execution_sections import (
    _build_positions_section as _build_positions_section,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _date_bounds_text as _date_bounds_text,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _date_list_text as _date_list_text,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _date_text as _date_text,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _frame_records as _frame_records,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _json_scalar as _json_scalar,
)
from strategy_pipeline.pipeline.output_summary_formatting import (
    _path_text as _path_text,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_data_section as _build_data_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_dataset_section as _build_dataset_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_label_section as _build_label_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_model_detail_section as _build_model_detail_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_run_section as _build_run_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_signal_artifact_section as _build_signal_artifact_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_split_section as _build_split_section,
)
from strategy_pipeline.pipeline.output_summary_run_sections import (
    _build_universe_section as _build_universe_section,
)


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
