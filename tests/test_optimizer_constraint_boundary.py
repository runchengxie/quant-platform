"""Public optimizer results must enforce constraints independently of the backend."""

import numpy as np
import pandas as pd
import pytest

from quant_platform.portfolio.optimization import (
    EqualWeightOptimizerBackend,
    HrpOptimizerBackend,
    InverseVolOptimizerBackend,
    LinearExposureConstraint,
    OptimizerRegistry,
    PortfolioOptimizationRequest,
    PortfolioOptimizationResult,
    QpMinVarianceOptimizerBackend,
)


def _request(**kwargs: object) -> PortfolioOptimizationRequest:
    return PortfolioOptimizationRequest(
        returns=pd.DataFrame({"A": [0.01, -0.01, 0.02], "B": [-0.02, 0.02, 0.01]}),
        **kwargs,
    )


@pytest.mark.parametrize("bounds", [{"lower": 0.7}, {"upper": 0.3}, {"lower": 0.7, "upper": 0.7}])
@pytest.mark.parametrize("through_registry", [False, True])
def test_untrusted_results_cannot_bypass_linear_exposure_bounds(bounds, through_registry):
    request = _request(
        linear_constraints=(
            LinearExposureConstraint("allocation", pd.Series({"B": 0.0, "A": 1.0}), **bounds),
        )
    )
    result = PortfolioOptimizationResult("external.unchecked", pd.Series({"B": 0.5, "A": 0.5}))

    class UncheckedBackend:
        name = "external.unchecked"

        def run(self, request):
            return result

    registry = OptimizerRegistry()
    registry.register(UncheckedBackend())
    with pytest.raises(ValueError, match="allocation"):
        if through_registry:
            registry.run("external.unchecked", request)
        else:
            result.validate(request)


@pytest.mark.parametrize(
    "backend", [EqualWeightOptimizerBackend(), HrpOptimizerBackend(), InverseVolOptimizerBackend()]
)
@pytest.mark.parametrize("single_asset", [False, True])
def test_baselines_reject_even_satisfied_constraints_before_computing(backend, single_asset):
    # Insufficient observations would fail inverse-vol estimation if rejection ran late.
    returns = pd.DataFrame({"A": [0.01], "B": [0.02]})
    if single_asset:
        returns = returns[["A"]]
    request = PortfolioOptimizationRequest(
        returns=returns,
        linear_constraints=(
            LinearExposureConstraint("constant", pd.Series(1.0, index=returns.columns), lower=1.0),
        ),
    )
    with pytest.raises(ValueError, match=r"does not support linear_constraints"):
        backend.run(request)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_validation_rejects_nonfinite_exposure_even_after_request_mutation(value):
    request = _request(
        linear_constraints=(
            LinearExposureConstraint("allocation", pd.Series({"A": 1.0, "B": 0.0}), lower=0.4),
        )
    )
    request.linear_constraints[0].values.iloc[0] = value
    result = PortfolioOptimizationResult("external.unchecked", pd.Series({"A": 0.5, "B": 0.5}))
    with pytest.raises(ValueError, match=r"allocation.*finite"):
        result.validate(request)


@pytest.mark.parametrize("index", [["A", "A", "B"], [1, "1", "B"]])
def test_request_rejects_duplicate_exposure_assets_after_string_normalization(index):
    returns = pd.DataFrame([[0.01, 0.02]], columns=[index[0], "B"])
    with pytest.raises(ValueError, match="unique"):
        PortfolioOptimizationRequest(
            returns=returns,
            linear_constraints=(
                LinearExposureConstraint(
                    "allocation", pd.Series([1.0, 2.0, 0.0], index=index), lower=0.4
                ),
            ),
        )


def test_result_rejects_duplicate_weight_assets_after_string_normalization():
    request = PortfolioOptimizationRequest(returns=pd.DataFrame([[0.01, 0.02]], columns=[1, "B"]))
    result = PortfolioOptimizationResult(
        "external.unchecked", pd.Series([0.2, 0.3, 0.5], index=[1, "1", "B"])
    )
    with pytest.raises(ValueError, match="unique"):
        result.validate(request)


def test_qp_and_reordered_results_honor_exact_exposure_bounds():
    request = _request(
        linear_constraints=(
            LinearExposureConstraint(
                "allocation", pd.Series({"B": 0.0, "A": 1.0}), lower=0.7, upper=0.7
            ),
        )
    )
    result = QpMinVarianceOptimizerBackend().run(request)
    assert result.weights["A"] == pytest.approx(0.7, abs=1e-7)
    PortfolioOptimizationResult("external.valid", pd.Series({"B": 0.3, "A": 0.7})).validate(request)


@pytest.mark.parametrize("exposure", [0.7 - 5e-8, 0.7 + 5e-8])
def test_linear_validation_accepts_qp_roundoff(exposure):
    request = _request(
        linear_constraints=(
            LinearExposureConstraint(
                "allocation", pd.Series({"A": 1.0, "B": 0.0}), lower=0.7, upper=0.7
            ),
        )
    )
    PortfolioOptimizationResult(
        "external.valid", pd.Series({"A": exposure, "B": 1.0 - exposure})
    ).validate(request)


@pytest.mark.parametrize("exposure", [0.7 - 2e-7, 0.7 + 2e-7])
def test_linear_validation_rejects_violations_beyond_qp_roundoff(exposure):
    request = _request(
        linear_constraints=(
            LinearExposureConstraint(
                "allocation", pd.Series({"A": 1.0, "B": 0.0}), lower=0.7, upper=0.7
            ),
        )
    )
    with pytest.raises(ValueError, match="allocation"):
        PortfolioOptimizationResult(
            "external.invalid", pd.Series({"A": exposure, "B": 1.0 - exposure})
        ).validate(request)


def test_constraint_names_cannot_hide_another_constraints_upper_violation():
    request = _request(
        linear_constraints=(
            LinearExposureConstraint("allocation", pd.Series({"A": 1.0, "B": 0.0}), upper=0.3),
            LinearExposureConstraint(
                "allocation.upper", pd.Series({"A": 1.0, "B": 0.0}), lower=0.1
            ),
        )
    )
    with pytest.raises(ValueError, match=r"allocation.*upper"):
        PortfolioOptimizationResult("external.invalid", pd.Series({"A": 0.5, "B": 0.5})).validate(
            request
        )
