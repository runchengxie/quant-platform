"""Position and execution summary sections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from portfolio_backtester.execution_sim import describe_execution_sim_config
from strategy_pipeline.pipeline.output_summary_formatting import _date_text, _path_text


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
