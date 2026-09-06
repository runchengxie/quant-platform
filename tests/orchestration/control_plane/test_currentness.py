from strategy_pipeline import (
    PublicationCurrentnessPolicy,
    evaluate_input_currentness,
)


def _availability(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "available": True,
        "source_date": "20260903",
        "signal_date": "20260904",
        "required_input_date": "20260903",
        "input_source": "canonical",
        "current_as_of": "20260903",
        "max_input_date": "20260903",
        "input_mode": "all",
        "input_count": 20,
        "input_policy_id": "policy:v1",
        "issues": (),
    }
    result.update(overrides)
    return result


def test_currentness_accepts_current_owner_bundle() -> None:
    result = evaluate_input_currentness(
        _availability(),
        PublicationCurrentnessPolicy(),
    )

    assert result.ready
    assert result.to_dict()["source_date"] == "20260903"


def test_currentness_rejects_stale_production_bundle() -> None:
    result = evaluate_input_currentness(
        _availability(current_as_of="20260902"),
        PublicationCurrentnessPolicy(),
    )

    assert not result.ready
    assert "expected 20260903" in result.reasons[0]


def test_research_policy_can_allow_stale_bundle() -> None:
    result = evaluate_input_currentness(
        _availability(current_as_of="20260902"),
        PublicationCurrentnessPolicy(publication_tier="research"),
    )

    assert result.ready
