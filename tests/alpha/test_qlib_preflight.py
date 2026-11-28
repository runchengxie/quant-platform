import json

import pytest


def context():
    return {
        "data_revision": "synthetic-v1",
        "universe_revision": "fixed-v1",
        "calendar_revision": "synthetic-days-v1",
        "execution_policy_revision": "next-session-v1",
        "frequency": "day",
        "dependency_lock_sha256": "a" * 64,
    }


def run(expression, **kwargs):
    from alpha_research.qlib_preflight import preflight_qlib_expression

    return preflight_qlib_expression(
        expression, allowed_fields=["close", "volume"], context=context(), **kwargs
    )


def test_real_qlib_windows_and_json_only_receipt():
    pytest.importorskip("qlib")
    result = run("Mean(Ref($close, 1), 5) / $volume")
    assert result["status"] == "admitted"
    assert result["left_window"] == 5
    assert result["right_window"] == 0
    assert result["dependencies"] == ["close", "volume"]
    assert result["backend"] == "qlib"
    assert result["backend_version"] == "0.9.7"
    json.dumps(result, allow_nan=False)


def test_future_signal_is_rejected_but_explicit_label_can_use_bounded_horizon():
    pytest.importorskip("qlib")
    assert run("Ref($close, -2)")["diagnostic"]["code"] == "future_reference"
    label = run("Ref($close, -2)", role="label", label_lookahead=2)
    assert label["status"] == "admitted"
    assert label["role"] == "label"
    assert run("Ref($close, -3)", role="label", label_lookahead=2)["status"] == "rejected"


@pytest.mark.parametrize(
    "expression",
    [
        "$unknown",
        "Mean($close, 0)",
        "Mean($close, 1.5)",
        "Ref($close, True)",
        "Mean($close, 999999999)",
        "__import__('os').system('true')",
        "$close.__class__",
        "$close[0]",
        "[x for x in []]",
        "Unknown($close)",
        "1",
        "Mean($close, -5)",
        "$$financial_field",
        "2**999999999",
    ],
)
def test_unregistered_or_unsafe_candidate_is_rejected(expression):
    pytest.importorskip("qlib")
    result = run(expression)
    assert result["status"] == "rejected"
    assert result["diagnostic"]["code"]


def test_context_and_role_are_part_of_identity_but_whitespace_is_not():
    pytest.importorskip("qlib")
    from alpha_research.qlib_preflight import preflight_qlib_expression

    first = run("Mean($close, 5)")
    assert first["root_sha256"] == run("Mean( $close , 5 )")["root_sha256"]
    changed = context()
    changed["universe_revision"] = "different"
    other = preflight_qlib_expression(
        "Mean($close, 5)", allowed_fields=["close", "volume"], context=changed
    )
    assert first["root_sha256"] != other["root_sha256"]
    assert (
        first["root_sha256"]
        != run("Mean($close,5)", role="label", label_lookahead=1)["root_sha256"]
    )


def test_missing_optional_dependency_never_silently_uses_local_evaluator(monkeypatch):
    import alpha_research.qlib_preflight as module

    def missing():
        raise ImportError("optional pyqlib not installed")

    monkeypatch.setattr(module, "_runtime", missing)
    assert run("Mean($close, 5)")["status"] == "unavailable"


def test_invalid_context_and_budget_fail_before_admission():
    from alpha_research.qlib_preflight import preflight_qlib_expression

    result = preflight_qlib_expression("$close", allowed_fields=["close"], context={})
    assert result["status"] == "rejected"
    assert result["diagnostic"]["code"] == "invalid_context"
    assert run("$close", role="signal", label_lookahead=1)["status"] == "rejected"


def test_nonstring_role_is_a_structured_json_rejection():
    result = run("$close", role=[])
    assert result["status"] == "rejected"
    json.dumps(result, allow_nan=False)


def test_overflow_in_scalar_subexpressions_cannot_enter_a_signal():
    pytest.importorskip("qlib")
    assert run("$close + " + "*".join(["1e12"] * 26))["status"] == "rejected"


def test_reused_qlib_operators_match_a_synthetic_numeric_reference(monkeypatch):
    import ast

    import numpy as np
    import pandas as pd

    pytest.importorskip("qlib")
    import alpha_research.qlib_preflight as module

    runtime = module._runtime()
    series = pd.Series([1.0, 4.0, 2.0, 8.0, 3.0, 9.0])

    def synthetic_input(self, instrument, start_index, end_index, *args):
        return series.loc[start_index:end_index].copy()

    monkeypatch.setattr(runtime["operators"]["Feature"], "_load_internal", synthetic_input)
    formula = "Mean($close, 3) + Ref($close, 1)"
    assert run(formula)["status"] == "admitted"
    tree = ast.parse(runtime["parse"](formula), mode="eval")
    expression = module._construct(tree.body, runtime, {"close"}, set())
    actual = expression.load("SYN_QLIB_PREFLIGHT_GOLDEN", 0, 5, "day")
    expected = series.rolling(3, min_periods=1).mean() + series.shift(1)
    np.testing.assert_allclose(actual.to_numpy(), expected.to_numpy(), equal_nan=True)
