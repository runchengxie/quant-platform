from quant_execution_engine.risk_pipeline import (
    PreTradeRiskPipeline,
    RiskDecision,
    RiskOutcome,
)


class Rule:
    def __init__(self, name, decision): self.name, self.decision = name, decision
    def evaluate(self, order, portfolio, market_state, config):
        return self.decision

def test_pipeline_chains_adjustments_and_stops_on_reject() -> None:
    rules = [
        Rule("cap", RiskDecision(RiskOutcome.ADJUST, "cap", "reduced", order=5)),
        Rule("cash", RiskDecision(RiskOutcome.REJECT, "cash", "insufficient")),
        Rule("later", RiskDecision(RiskOutcome.PASS, "later", "ok")),
    ]
    order, decisions = PreTradeRiskPipeline(rules).evaluate(10)
    assert order == 5
    assert [item.rule for item in decisions] == ["cap", "cash"]
