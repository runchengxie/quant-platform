from __future__ import annotations

from strategy_pipeline.control_plane.ports import (
    NativeAlphaOwnerAdapter,
    NativeDataOwnerAdapter,
    NativeExecutionBoundaryAdapter,
    NativePortfolioOwnerAdapter,
    OwnerStageReceipt,
    PipelineOwnerPorts,
    PipelineRunReceipt,
    TrainEvalServiceHooks,
    completed_run_receipt,
)


def test_owner_adapters_expose_owner_neutral_control_plane_ports() -> None:
    hooks = TrainEvalServiceHooks(
        backtest_topk=lambda: "backtest",
        bucket_ic_summary=lambda: "ic",
        walk_forward_backtest=lambda: "walk-forward",
        period_evaluation=lambda: "period",
        live_snapshot=lambda: "live",
    )
    ports = PipelineOwnerPorts(
        data=NativeDataOwnerAdapter(lambda **_: {"stage": "data"}),
        alpha=NativeAlphaOwnerAdapter(
            lambda **_: {"stage": "alpha"},
            lambda **_: {"stage": "train-eval"},
        ),
        portfolio=NativePortfolioOwnerAdapter(hooks, lambda **_: {"stage": "oos"}),
        execution_boundary=NativeExecutionBoundaryAdapter(lambda **_: None),
    )

    assert ports.owner_ids() == (
        "market-data-platform",
        "alpha-research",
        "portfolio-backtester",
        "strategy-pipeline",
    )
    assert ports.data.load_research_panel() == {"stage": "data"}
    assert ports.alpha.run_train_eval(request="request") == {"stage": "train-eval"}
    assert ports.portfolio.run_final_oos() == {"stage": "oos"}


def test_completed_run_receipt_is_serializable_without_owner_imports() -> None:
    ports = PipelineOwnerPorts(
        data=NativeDataOwnerAdapter(lambda **_: {}),
        alpha=NativeAlphaOwnerAdapter(lambda **_: {}, lambda **_: {}),
        portfolio=NativePortfolioOwnerAdapter(
            TrainEvalServiceHooks(*(lambda: None for _ in range(5))),
            lambda **_: {},
        ),
        execution_boundary=NativeExecutionBoundaryAdapter(lambda **_: None),
    )

    receipt = completed_run_receipt("demo.yml", ports)

    assert isinstance(receipt, PipelineRunReceipt)
    assert receipt.to_dict() == {
        "schema_version": "strategy-pipeline.run-receipt/v1",
        "status": "completed",
        "config_ref": "demo.yml",
        "stages": [
            {
                "stage": "data",
                "owner_id": "market-data-platform",
                "status": "completed",
                "metadata": {},
            },
            {
                "stage": "alpha",
                "owner_id": "alpha-research",
                "status": "completed",
                "metadata": {},
            },
            {
                "stage": "portfolio",
                "owner_id": "portfolio-backtester",
                "status": "completed",
                "metadata": {},
            },
            {
                "stage": "artifact_handoff",
                "owner_id": "strategy-pipeline",
                "status": "completed",
                "metadata": {},
            },
        ],
    }


def test_owner_stage_receipt_serializes_metadata() -> None:
    receipt = OwnerStageReceipt(stage="data", owner_id="market-data-platform", metadata={"rows": 3})

    assert receipt.to_dict() == {
        "stage": "data",
        "owner_id": "market-data-platform",
        "status": "completed",
        "metadata": {"rows": 3},
    }
