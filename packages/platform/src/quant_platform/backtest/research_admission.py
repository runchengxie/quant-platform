"""Declared research eligibility; this contract cannot certify its own evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResearchContract:
    decision_ns: int
    data_available_ns: int | None
    model_available_ns: int | None
    training_cutoff_ns: int
    labels_complete_ns: int
    execution_start_ns: int
    holding_end_ns: int
    prediction_start_ns: int
    prediction_end_ns: int
    evidence: Mapping[str, str] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    price_basis: str = "raw"
    result_semantics: str = "execution_ledger_daily_nav"


def assess_admission(contract: ResearchContract, *, formal: bool = False) -> dict:
    """Hard violations block every use; unknown provenance permits mechanisms only."""
    violations, unknown = [], []
    _temporal(contract, violations, unknown)
    if contract.price_basis != "raw":
        violations.append("nonraw_execution_prices")
    if contract.result_semantics != "execution_ledger_daily_nav":
        violations.append("incompatible_result_semantics")
    _evidence(contract, violations, unknown)
    status = (
        "blocked"
        if violations or (formal and unknown)
        else "mechanism_only"
        if unknown
        else "admitted"
    )
    return {
        "schema": "research-admission.v1",
        "status": status,
        "formal": formal,
        "violations": violations,
        "unknown": unknown,
        "evidence_refs": list(contract.evidence_refs),
        "authority": "caller_declarations_require_independent_audit",
    }


def _evidence(contract, violations, unknown):
    for dimension in ("availability", "universe", "corporate_actions", "market_rules"):
        value = contract.evidence.get(dimension, "unknown")
        if value not in {"verified", "assumed", "unknown", "failed"}:
            raise ValueError("invalid evidence status")
        if value == "failed":
            violations.append(f"{dimension}_failed")
        elif value != "verified":
            unknown.append(f"{dimension}_{value}")
    if not contract.evidence_refs or any(not ref.strip() for ref in contract.evidence_refs):
        unknown.append("evidence_references_missing")


def _temporal(contract, violations, unknown):
    clocks = (
        contract.decision_ns,
        contract.training_cutoff_ns,
        contract.labels_complete_ns,
        contract.execution_start_ns,
        contract.holding_end_ns,
        contract.prediction_start_ns,
        contract.prediction_end_ns,
    )
    if any(type(t) is not int for t in clocks):
        raise ValueError("clocks must be UTC integer nanoseconds")
    _availability(contract, violations, unknown)
    if contract.training_cutoff_ns > contract.decision_ns:
        violations.append("future_training_cutoff")
    if contract.labels_complete_ns > contract.decision_ns:
        violations.append("future_training_labels")
    if contract.labels_complete_ns > contract.training_cutoff_ns:
        violations.append("incomplete_training_labels")
    if (
        contract.model_available_ns is not None
        and contract.training_cutoff_ns > contract.model_available_ns
    ):
        violations.append("model_precedes_training")
    if not contract.decision_ns < contract.execution_start_ns < contract.holding_end_ns:
        violations.append("invalid_execution_interval")
    if (contract.prediction_start_ns, contract.prediction_end_ns) != (
        contract.execution_start_ns,
        contract.holding_end_ns,
    ):
        violations.append("prediction_execution_horizon_mismatch")


def _availability(contract, violations, unknown):
    for name, available in (
        ("data", contract.data_available_ns),
        ("model", contract.model_available_ns),
    ):
        if available is None:
            unknown.append(f"{name}_availability_unknown")
        elif type(available) is not int:
            raise ValueError("availability must be integer nanoseconds or None")
        elif available > contract.decision_ns:
            violations.append(f"future_{name}")
