import pandas as pd

from strategy_pipeline.pipeline.output_artifacts import (
    _initial_artifacts,
    _write_dataset_artifacts,
    _write_position_outputs,
    _write_primary_backtest_series,
)


def _scored_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "trade_date": ["20200103", "20200103"],
            "symbol": ["AAA", "BBB"],
            "pred": [0.2, 0.1],
            "signal_eval": [0.2, 0.1],
            "signal_backtest": [0.2, 0.1],
        }
    )


def _context(
    *,
    save_signal_artifact: bool,
    save_scored_artifact: bool = False,
    save_pricing_artifact: bool = False,
) -> dict:
    return {
        "SAVE_DATASET": False,
        "SAVE_SIGNAL_ARTIFACT": save_signal_artifact,
        "SAVE_SCORED_ARTIFACT": save_scored_artifact,
        "SAVE_PRICING_ARTIFACT": save_pricing_artifact,
        "eval_scored_data": _scored_frame(),
        "backtest_pricing_df": pd.DataFrame(
            {
                "trade_date": ["20200102", "20200102"],
                "symbol": ["AAA", "BBB"],
                "close": [10.0, 20.0],
                "amount": [1000.0, 2000.0],
                "medadv20_amount": [900.0, 1800.0],
            }
        ),
        "MODEL_TYPE": "xgb_regressor",
        "run_hash": "deadbeef",
        "run_name": "artifact_test",
        "features": ["sma_5"],
        "SIGNAL_DIRECTION": 1.0,
        "BACKTEST_ENABLED": True,
        "LIVE_ENABLED": False,
    }


def test_signal_artifact_is_not_written_by_default(tmp_path):
    artifacts = _initial_artifacts()

    _write_dataset_artifacts(
        ctx=_context(save_signal_artifact=False), run_dir=tmp_path, artifacts=artifacts
    )

    assert artifacts["signals_path"] is None
    assert artifacts["signals_meta_path"] is None
    assert not (tmp_path / "signals.parquet").exists()
    assert not (tmp_path / "signals.meta.json").exists()


def test_signal_artifact_writes_when_enabled(tmp_path):
    artifacts = _initial_artifacts()

    _write_dataset_artifacts(
        ctx=_context(save_signal_artifact=True), run_dir=tmp_path, artifacts=artifacts
    )

    assert artifacts["signals_path"] == tmp_path / "signals.parquet"
    assert artifacts["signals_meta_path"] == tmp_path / "signals.meta.json"
    assert (tmp_path / "signals.parquet").exists()
    assert (tmp_path / "signals.meta.json").exists()


def test_legacy_scored_artifact_remains_independent(tmp_path):
    artifacts = _initial_artifacts()

    _write_dataset_artifacts(
        ctx=_context(save_signal_artifact=False, save_scored_artifact=True),
        run_dir=tmp_path,
        artifacts=artifacts,
    )

    assert artifacts["signals_path"] is None
    assert artifacts["eval_scored_path"] == tmp_path / "eval_scored.parquet"
    assert not (tmp_path / "signals.parquet").exists()
    assert (tmp_path / "eval_scored.parquet").exists()


def test_pricing_artifact_writes_the_backtest_panel_when_enabled(tmp_path):
    artifacts = _initial_artifacts()

    _write_dataset_artifacts(
        ctx=_context(save_signal_artifact=False, save_pricing_artifact=True),
        run_dir=tmp_path,
        artifacts=artifacts,
    )

    assert artifacts["pricing_path"] == tmp_path / "backtest_pricing.parquet"
    pricing = pd.read_parquet(tmp_path / "backtest_pricing.parquet")
    assert pricing[["trade_date", "symbol", "close", "amount"]].to_dict("records") == [
        {
            "trade_date": "20200102",
            "symbol": "AAA",
            "close": 10.0,
            "amount": 1000.0,
        },
        {
            "trade_date": "20200102",
            "symbol": "BBB",
            "close": 20.0,
            "amount": 2000.0,
        },
    ]


def test_position_outputs_select_current_with_integer_yyyymmdd_dates(tmp_path):
    artifacts = _initial_artifacts()
    positions = pd.DataFrame(
        {
            "entry_date": [20200102, 20200103, 20200103],
            "rebalance_date": [20200101, 20200102, 20200102],
            "symbol": ["A", "B", "C"],
            "weight": [0.2, 0.3, 0.4],
        }
    )

    _write_position_outputs(
        positions=positions,
        run_dir=tmp_path,
        by_rebalance_name="positions_by_rebalance_live.csv",
        current_name="positions_current_live.csv",
        diff_name="rebalance_diff_live.csv",
        artifacts=artifacts,
        by_rebalance_key="positions_by_rebalance_live_path",
        current_key="positions_current_live_path",
        diff_key="positions_diff_live_path",
        enabled=True,
    )

    current = pd.read_csv(tmp_path / "positions_current_live.csv")
    assert current["symbol"].tolist() == ["B", "C"]
    assert current["entry_date"].tolist() == [20200103, 20200103]


def test_backtest_output_series_use_contract_period_end_column(tmp_path):
    period_index = pd.to_datetime(["2026-01-31", "2026-02-28"])
    ctx = {
        "bt_net_series": pd.Series([0.01, -0.02], index=period_index, name="net_return"),
        "bt_gross_series": pd.Series([0.02, -0.01], index=period_index, name="gross_return"),
        "bt_turnover_series": pd.Series([1.0, 0.5], index=period_index, name="turnover"),
        "bt_benchmark_series": pd.Series(dtype=float, name="benchmark_return"),
        "bt_active_series": pd.Series(dtype=float, name="active_return"),
        "bt_periods": [
            {
                "rebalance_date": pd.Timestamp("2026-01-05"),
                "entry_idx": 0,
                "planned_exit_idx": 1,
                "exit_idx": 1,
                "entry_date": pd.Timestamp("2026-01-06"),
                "planned_exit_date": pd.Timestamp("2026-01-31"),
                "exit_date": pd.Timestamp("2026-01-31"),
                "exit_delay_steps": 0,
            }
        ],
    }

    _write_primary_backtest_series(ctx=ctx, run_dir=tmp_path)

    net = pd.read_csv(tmp_path / "backtest_net.csv")
    periods = pd.read_csv(tmp_path / "backtest_periods.csv")
    assert net.columns.tolist() == ["period_end", "net_return"]
    assert periods.columns.tolist() == list(ctx["bt_periods"][0])
