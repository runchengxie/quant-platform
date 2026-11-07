from dataclasses import replace

import pytest

from quant_platform.backtest.research_admission import ResearchContract, assess_admission


def contract():
    return ResearchContract(
        decision_ns=100,
        data_available_ns=90,
        model_available_ns=95,
        training_cutoff_ns=80,
        labels_complete_ns=70,
        execution_start_ns=110,
        holding_end_ns=200,
        prediction_start_ns=110,
        prediction_end_ns=200,
        evidence=dict.fromkeys(
            ("availability", "universe", "corporate_actions", "market_rules"), "verified"
        ),
        evidence_refs=("audit:v1",),
    )


def test_complete_contract_and_unknown_evidence_are_distinct():
    assert assess_admission(contract(), formal=True)["status"] == "admitted"
    unknown = replace(contract(), data_available_ns=None, evidence={})
    assert assess_admission(unknown)["status"] == "mechanism_only"
    assert assess_admission(unknown, formal=True)["status"] == "blocked"


@pytest.mark.parametrize(
    "changes",
    [
        {"data_available_ns": 101},
        {"model_available_ns": 101},
        {"labels_complete_ns": 81},
        {"prediction_end_ns": 199},
        {"price_basis": "adjusted"},
        {"result_semantics": "period_return"},
    ],
)
def test_invalid_economic_or_causal_contract_is_blocked(changes):
    assert assess_admission(replace(contract(), **changes))["status"] == "blocked"


def test_unknown_model_clock_cannot_hide_known_future_training():
    bad = replace(
        contract(), model_available_ns=None, training_cutoff_ns=150, labels_complete_ns=140
    )
    assert assess_admission(bad)["status"] == "blocked"
