"""Capacity experiments preserve inputs and disclose quantity changes."""

import pytest

from scripts.benchmarks.capacity_pressure import Scenario, experiment, fixed_fill_cost_control


def test_determinism_and_absolute_initial_quantity_across_capital():
    low = experiment(Scenario(capital=100_000))
    high = experiment(Scenario(capital=10_000_000))
    assert low[0] == experiment(Scenario(capital=100_000))[0]
    assert low[1]["orders"].iloc[0].quantity == high[1]["orders"].iloc[0].quantity
    assert low[0]["terminal_inventory_shares"] == 0
    assert low[0]["buy_unfilled_reference_cny"] >= 0


def test_scaled_targets_increase_demand_and_fixed_fill_cost_control_reconciles():
    small, ledgers = experiment(Scenario(capital=100_000, mode="scaled_weight"))
    large, _ = experiment(Scenario(capital=10_000_000, mode="scaled_weight"))
    assert large["buy_desired_shares"] > small["buy_desired_shares"]
    controls = fixed_fill_cost_control(ledgers["fills"], small["net_pnl_cny"])
    assert len({row["fixed_fills_sha256"] for row in controls}) == 1
    assert controls[-1]["net_pnl_cny"] < controls[0]["net_pnl_cny"]


def test_per_symbol_bar_capacity_and_terminal_accounting():
    summary, frames = experiment(
        Scenario(capital=10_000_000, mode="scaled_weight", participation=0.01)
    )
    assert frames["bars"].shape[0] == 4620
    assert frames["targets"].shape[0] == 140
    assert frames["fills"].groupby(["time", "symbol"]).quantity.sum().max() <= 100
    assert summary["buy_fill_rate"] < 1
    assert summary["terminal_nav_cny"] == pytest.approx(
        summary["terminal_cash_cny"] + summary["terminal_positions_value_cny"]
    )
