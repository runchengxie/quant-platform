from dataclasses import replace
from datetime import datetime, timedelta

import pytest
from usd_ledger_fixtures import REF, D, at, config, decision, instrument, price, request

from portfolio_backtester.usd_ledger_inputs import (
    select_usd_fx,
    select_usd_price,
    validate_usd_request,
)
from portfolio_backtester.usd_ledger_models import USDFXObservation, USDValidationError


def fx(base, quote, rate, day=1, **overrides):
    row = USDFXObservation(
        base, quote, at(day), at(day), D(rate), "quote_per_base", REF, "verified"
    )
    return replace(row, **overrides)


def test_direct_inverse_and_usd_identity():
    r = request(
        instruments=(instrument("A", "GBP"), instrument("B", "HKD")),
        prices=(),
        decisions=(),
        fx=(fx("GBP", "USD", "1.25"), fx("USD", "HKD", "8")),
        config=config(fx_pairs={"GBP": ("GBP", "USD"), "HKD": ("USD", "HKD")}),
    )
    validate_usd_request(r)
    assert select_usd_fx(r, "GBP", at(2))[0] == D("1.25")
    assert select_usd_fx(r, "HKD", at(2))[0] == D("0.125")
    assert select_usd_fx(r, "USD", at(2)) == (D("1"), None)


def test_future_available_row_does_not_replace_eligible_mark():
    r = request(prices=(price(), price(day=2, value="999", available_at=at(3))))
    validate_usd_request(r)
    assert select_usd_price(r, "A", at(2)).price == D("10")


@pytest.mark.parametrize("bad", [True, 10.0, "10", D("NaN"), D("Infinity"), D("0"), D("-1")])
def test_invalid_price_numbers_fail(bad):
    with pytest.raises(USDValidationError):
        validate_usd_request(request(prices=(price(price=bad),)))


@pytest.mark.parametrize(
    "changes",
    [
        {"price_at": datetime(2026, 1, 1)},
        {"unit": "adjusted_total_return"},
        {"available_at": at(1) - timedelta(seconds=1)},
        {"instrument_id": "unknown"},
        {"session_policy_id": "other-session"},
        {"execution_eligible": "yes"},
    ],
)
def test_invalid_observation_metadata_fails(changes):
    with pytest.raises(USDValidationError):
        validate_usd_request(request(prices=(price(**changes),)))


@pytest.mark.parametrize(
    "changes",
    [
        {"instruments": (instrument(), instrument())},
        {"prices": (price(), price())},
        {"instruments": (replace(instrument(), asset_type="future"),)},
        {"config": config(return_basis="total")},
        {"config": config(sizing_mode="margin")},
        {"config": config(commission_bps=D("10000"))},
        {"valuation_times": (at(2), at(3))},
        {"valuation_times": (at(1),)},
        {"decisions": (decision(), decision())},
        {"decisions": (decision(weights={"A": D("1.1")}),)},
        {"decisions": (decision(times={"A": at(1)}),)},
        {"decisions": (decision(times={}),)},
    ],
)
def test_invalid_request_fails(changes):
    with pytest.raises(USDValidationError):
        validate_usd_request(request(**changes))


def test_source_replacement_and_unselected_fx_are_rejected():
    other = replace(price(day=2), source_ref=type(REF)("replacement", "b" * 64))
    with pytest.raises(USDValidationError):
        validate_usd_request(request(prices=(price(), other)))
    with pytest.raises(USDValidationError):
        validate_usd_request(request(instruments=(instrument(currency="GBP"),)))


def test_missing_stale_and_carried_execution_fail():
    r = request(prices=(price(),), config=config(max_price_age=timedelta(hours=2)))
    for time, execution in [(at(2), False), (at(1, 1), True)]:
        with pytest.raises(USDValidationError):
            select_usd_price(r, "A", time, execution=execution)
    with pytest.raises(USDValidationError):
        select_usd_fx(
            request(
                fx=(fx("GBP", "USD", "1.25"),),
                config=config(fx_pairs={"GBP": ("GBP", "USD")}, max_fx_age=timedelta(hours=1)),
            ),
            "GBP",
            at(2),
        )


def test_assumed_marks_are_valuation_only():
    r = request(
        prices=(price(availability_basis="assumed_date_lag"),),
        config=config(allow_assumed_availability=True),
    )
    validate_usd_request(r)
    assert select_usd_price(r, "A", at(1)).price == D("10")
    with pytest.raises(USDValidationError):
        select_usd_price(r, "A", at(1), execution=True)
    with pytest.raises(USDValidationError):
        validate_usd_request(replace(r, config=config()))


def test_execution_exact_mark_requires_eligibility():
    r = request(prices=(price(hour=1, execution_eligible=False),))
    with pytest.raises(USDValidationError):
        select_usd_price(r, "A", at(1, 1), execution=True)


def test_unused_instruments_do_not_require_observations():
    validate_usd_request(request(prices=(), decisions=()))
    validate_usd_request(request(instruments=(), prices=(), decisions=()))


def test_overlap_is_rejected():
    with pytest.raises(USDValidationError):
        validate_usd_request(request(decisions=(decision(times={"A": at(3)}), decision(day=2))))
