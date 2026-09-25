"""Diagnostics, readiness, and promotion summary sections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from strategy_pipeline.pipeline.output_summary_formatting import (
    _frame_records,
    _path_text,
)


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
