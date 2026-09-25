from __future__ import annotations

from datetime import date

import pandas as pd

from strategy_pipeline.pipeline.output_summary_sections import (
    _build_backtest_exposure_summary,
    _date_bounds_text,
    _date_text,
    _frame_records,
)


def test_summary_helpers_normalize_paths_dates_and_frames() -> None:
    summary = _build_backtest_exposure_summary(
        style_path="artifacts/style.parquet",
        industry_path=None,
        active_summary_path="artifacts/active.json",
        style_summary={"latest_rebalance_date": "2026-01-02", "factors": {"size": 1}},
        industry_summary={"latest_entry_date": "2026-01-03"},
    )

    assert summary["style_file"] == "artifacts/style.parquet"
    assert summary["industry_file"] is None
    assert summary["latest_rebalance_date"] == "2026-01-02"
    assert summary["latest_entry_date"] == "2026-01-03"
    assert _date_text(date(2026, 1, 2)) == "20260102"
    assert _date_bounds_text(["2026-01-03", "2026-01-01"]) == {
        "start": "20260101",
        "end": "20260103",
    }
    assert _frame_records(pd.DataFrame({"value": [1.0, None]})) == [
        {"value": 1.0},
        {"value": None},
    ]


def test_execution_summary_preserves_missing_and_disabled_shapes() -> None:
    from portfolio_backtester.execution_sim import ExecutionSimConfig
    from strategy_pipeline.pipeline.output_summary_sections import _build_execution_sim_summary

    summary = _build_execution_sim_summary(
        summary=None,
        config=ExecutionSimConfig(enabled=False),
        orders_path=None,
        fills_path=None,
        executed_summary=None,
        executed_daily_path=None,
    )

    assert summary["enabled"] is False
    assert summary["status"] == "disabled"
    assert summary["orders_file"] is None
    assert summary["fills_file"] is None
    assert summary["executed"] == {
        "enabled": False,
        "status": "disabled",
        "daily_file": None,
    }


def test_summary_aggregator_keeps_section_order_and_names(monkeypatch) -> None:
    import strategy_pipeline.pipeline.output_summary_sections as sections

    builders = (
        "_build_run_section",
        "_build_data_section",
        "_build_dataset_section",
        "_build_signal_artifact_section",
        "_build_model_detail_section",
        "_build_universe_section",
        "_build_label_section",
        "_build_split_section",
        "_build_eval_section",
        "_build_backtest_section",
        "_build_final_oos_section",
        "_build_recency_diagnostics_section",
        "_build_factor_diagnostics_summary",
        "_build_positions_section",
        "_build_live_section",
        "_build_promotion_sidecar_section",
        "_build_quality_section",
        "_build_fundamentals_section",
        "_build_industry_section",
        "_build_walk_forward_section",
    )
    for name in builders:
        monkeypatch.setattr(sections, name, lambda *args, _name=name, **kwargs: _name)

    context = {"quantile_mean": object(), "quantile_mean_oos": object()}
    summary = sections.build_run_summary_sections(context=context, artifacts={})

    expected = (
        "run",
        "data",
        "dataset",
        "signals",
        "model_detail",
        "universe",
        "label",
        "split",
        "eval",
        "backtest",
        "final_oos",
        "recency_diagnostics",
        "factor_diagnostics",
        "positions",
        "live",
        "promotion_sidecar",
        "quality",
        "fundamentals",
        "industry",
        "walk_forward",
    )
    assert tuple(summary) == expected
    assert tuple(summary.values()) == builders


def test_legacy_summary_builder_imports_resolve_to_new_owners() -> None:
    from strategy_pipeline.pipeline import (
        output_summary_diagnostic_sections as diagnostic,
    )
    from strategy_pipeline.pipeline import (
        output_summary_eval_sections as evaluation,
    )
    from strategy_pipeline.pipeline import (
        output_summary_execution_sections as execution,
    )
    from strategy_pipeline.pipeline import (
        output_summary_formatting as formatting,
    )
    from strategy_pipeline.pipeline import (
        output_summary_run_sections as run,
    )
    from strategy_pipeline.pipeline import output_summary_sections as legacy

    owners = {
        formatting: (
            "_path_text",
            "_date_text",
            "_date_list_text",
            "_date_bounds_text",
            "_json_scalar",
            "_frame_records",
        ),
        execution: (
            "_build_backtest_exposure_summary",
            "_build_execution_sim_summary",
            "_build_ideal_daily_nav_summary",
            "_build_position_postprocess_summary",
            "_build_positions_section",
            "_build_live_section",
        ),
        run: (
            "_build_run_section",
            "_build_data_section",
            "_build_dataset_section",
            "_build_signal_artifact_section",
            "_build_model_detail_section",
            "_build_universe_section",
            "_build_label_section",
            "_build_split_section",
        ),
        evaluation: (
            "_build_eval_section",
            "_build_backtest_section",
            "_build_oos_backtest_section",
            "_build_oos_positions_section",
            "_build_final_oos_section",
        ),
        diagnostic: (
            "_build_recency_diagnostics_section",
            "_build_turnover_attribution_summary",
            "_build_signal_stability_summary",
            "_build_factor_diagnostics_summary",
            "_build_quality_section",
            "_build_promotion_sidecar_section",
            "_build_fundamentals_section",
            "_build_industry_section",
            "_build_walk_forward_section",
        ),
    }

    for owner, names in owners.items():
        for name in names:
            assert getattr(legacy, name) is getattr(owner, name)
    assert callable(legacy.build_run_summary_sections)
