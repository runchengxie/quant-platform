"""Composable, pure pre-trade risk decisions."""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol


class RiskOutcome(StrEnum):
    PASS = "PASS"
    REJECT = "REJECT"
    ADJUST = "ADJUST"

@dataclass(frozen=True, slots=True)
class RiskDecision:
    outcome: RiskOutcome
    rule: str
    reason: str
    order: Any = None
    metrics: Mapping[str, Any] = None  # type: ignore[assignment]

class RiskRule(Protocol):
    name: str
    def evaluate(
        self, order: Any, portfolio: Any, market_state: Any, config: Mapping[str, Any]
    ) -> RiskDecision: ...

class PreTradeRiskPipeline:
    def __init__(self, rules: Sequence[RiskRule]) -> None:
        self._rules = tuple(rules)

    def evaluate(
        self,
        order: Any,
        portfolio: Any = None,
        market_state: Any = None,
        config: Mapping[str, Any] | None = None,
    ) -> tuple[Any, tuple[RiskDecision, ...]]:
        current = order
        decisions: list[RiskDecision] = []
        for rule in self._rules:
            decision = rule.evaluate(current, portfolio, market_state, config or {})
            decisions.append(decision)
            if decision.outcome is RiskOutcome.REJECT:
                return current, tuple(decisions)
            if decision.outcome is RiskOutcome.ADJUST:
                if decision.order is None:
                    raise ValueError(f"{rule.name} returned ADJUST without an order")
                current = decision.order
        return current, tuple(decisions)
