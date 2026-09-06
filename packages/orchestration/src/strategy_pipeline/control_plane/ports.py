"""Protocols implemented by private owners and storage adapters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from .contracts import ArtifactRef, HandoffRequest, PublicationRequest, RunRequest


@runtime_checkable
class RunOwner(Protocol):
    def run(self, request: RunRequest) -> ArtifactRef: ...


@runtime_checkable
class ArtifactPublisher(Protocol):
    def publish(self, request: PublicationRequest) -> ArtifactRef: ...


@runtime_checkable
class HandoffPublisher(Protocol):
    def publish(self, request: HandoffRequest) -> ArtifactRef: ...


ArtifactWriter = Callable[[PublicationRequest], ArtifactRef]


State = dict[str, Any]
StateCallable = Callable[..., State]
ValueCallable = Callable[..., Any]
VoidCallable = Callable[..., None]


@dataclass(frozen=True)
class TrainEvalServiceHooks:
    """Owner-provided callbacks used by a generic orchestration runner."""

    backtest_topk: ValueCallable
    bucket_ic_summary: ValueCallable
    walk_forward_backtest: ValueCallable
    period_evaluation: ValueCallable
    live_snapshot: ValueCallable


@runtime_checkable
class DataOwnerPort(Protocol):
    owner_id: str

    def load_research_panel(self, **kwargs: Any) -> State: ...


@runtime_checkable
class AlphaOwnerPort(Protocol):
    owner_id: str

    def prepare_feature_dataset(self, **kwargs: Any) -> State: ...

    def run_train_eval(self, *, request: Any) -> State: ...


@runtime_checkable
class PortfolioOwnerPort(Protocol):
    owner_id: str

    @property
    def train_eval_hooks(self) -> TrainEvalServiceHooks: ...

    def run_final_oos(self, **kwargs: Any) -> State: ...


@runtime_checkable
class ExecutionBoundaryPort(Protocol):
    owner_id: str

    def publish_research_handoff(self, **kwargs: Any) -> None: ...


@dataclass(frozen=True)
class NativeDataOwnerAdapter:
    load_research_panel_fn: StateCallable
    owner_id: str = "market-data-platform"

    def load_research_panel(self, **kwargs: Any) -> State:
        return self.load_research_panel_fn(**kwargs)


@dataclass(frozen=True)
class NativeAlphaOwnerAdapter:
    prepare_feature_dataset_fn: StateCallable
    run_train_eval_fn: StateCallable
    owner_id: str = "alpha-research"

    def prepare_feature_dataset(self, **kwargs: Any) -> State:
        return self.prepare_feature_dataset_fn(**kwargs)

    def run_train_eval(self, *, request: Any) -> State:
        return self.run_train_eval_fn(request=request)


@dataclass(frozen=True)
class NativePortfolioOwnerAdapter:
    train_eval_hooks: TrainEvalServiceHooks
    run_final_oos_fn: StateCallable
    owner_id: str = "portfolio-backtester"

    def run_final_oos(self, **kwargs: Any) -> State:
        return self.run_final_oos_fn(**kwargs)


@dataclass(frozen=True)
class NativeExecutionBoundaryAdapter:
    publish_research_handoff_fn: VoidCallable
    owner_id: str = "strategy-pipeline"

    def publish_research_handoff(self, **kwargs: Any) -> None:
        self.publish_research_handoff_fn(**kwargs)


@dataclass(frozen=True)
class PipelineOwnerPorts:
    data: DataOwnerPort
    alpha: AlphaOwnerPort
    portfolio: PortfolioOwnerPort
    execution_boundary: ExecutionBoundaryPort

    def owner_ids(self) -> tuple[str, ...]:
        return (
            self.data.owner_id,
            self.alpha.owner_id,
            self.portfolio.owner_id,
            self.execution_boundary.owner_id,
        )


@dataclass(frozen=True)
class OwnerStageReceipt:
    stage: str
    owner_id: str
    status: str = "completed"
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "owner_id": self.owner_id,
            "status": self.status,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PipelineRunReceipt:
    config_ref: str | None
    stages: tuple[OwnerStageReceipt, ...]
    status: str = "completed"
    schema_version: str = "strategy-pipeline.run-receipt/v1"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "config_ref": self.config_ref,
            "stages": [stage.to_dict() for stage in self.stages],
        }


def completed_run_receipt(
    config_ref: str | None,
    ports: PipelineOwnerPorts,
) -> PipelineRunReceipt:
    return PipelineRunReceipt(
        config_ref=config_ref,
        stages=tuple(
            OwnerStageReceipt(stage=stage, owner_id=owner_id)
            for stage, owner_id in zip(
                ("data", "alpha", "portfolio", "artifact_handoff"),
                ports.owner_ids(),
                strict=True,
            )
        ),
    )
