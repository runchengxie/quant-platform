# Accounting and execution roadmap

Language: English · [简体中文](accounting-execution-roadmap.md)

This roadmap tracks the shared accounting ledger used by signal backtests, position replays, and capacity diagnostics. The main contracts through phases 0–6 are implemented. Several features remain opt-in to preserve existing return and result contracts. Corporate-action values and calibrated market-impact models are still open work; the roadmap does not claim that every cost component is measured.

## Accounting contract

Backtest paths should follow the same auditable chain:

```text
target weights → orders → fills → positions and cash → daily NAV → report
```

The framework should also:

1. Keep explicit fees separate from modeled execution costs.
2. Use documented turnover definitions across entry points.
3. Fail when a configured execution constraint is missing required inputs; do not silently disable it.
4. Keep third-party framework objects out of public results and cross-repository artifacts.
5. Declare backend capabilities honestly. A period-return replay must not imply that it produced orders, fills, or a daily ledger when it did not.

## Implemented contracts

### Backend boundary and shared ledger

The execution contract defines `Instrument`, `Target`, `OrderIntent`, `OrderEvent`, `Fill`, and `LedgerSnapshot`. Order states are `created`, `submitted`, `accepted`, `partial`, `filled`, `cancelled`, `expired`, and `rejected`. `event_id` is the idempotency key: duplicate deliveries are ignored, conflicting payloads are rejected, and events are reduced in deterministic time-and-ID order.

The canonical result contract records backend capabilities for order lifecycle, partial fills, daily ledgers, long/short support, and market rules. The native period-replay backend preserves its historical behavior by default: order and daily-ledger outputs remain unavailable. Setting `ledger=True` opts into the shared execution simulator and unified ledger. The score-driven `backtest_topk` API also preserves its historical five-element return shape by default and appends a `UnifiedLedger` only when enabled. `run_position_backtest` records the execution simulator's `orders`, `fills`, and daily rows when that path is used; ideal-NAV and capacity-adjusted-NAV calculations also use the shared simulator.

The unified ledger contains `targets`, `orders`, `fills`, `daily_positions`, `daily_cash`, `daily_nav`, `cost_breakdown`, and `turnover_breakdown`. Unsupported native outputs remain explicit rather than being represented by fabricated empty results.

### Turnover and costs

The result model distinguishes name replacement from weight turnover and reports buy weight, sell weight, gross traded weight, half-L1 turnover, and one-way turnover where available. Existing historical cost conventions and aggregate fields remain supported.

`CostBreakdown` separates eight components: commission, stamp tax, transfer fee, spread, temporary impact, permanent impact, opportunity cost, and financing. The totals reconcile as:

```text
fee_cost = commission + stamp_tax + transfer_fee
slippage_cost = spread_cost + temporary_impact + permanent_impact
                 + opportunity_cost + financing_cost
total_cost = fee_cost + slippage_cost
```

`DetailedTradeFeeModel.notional_cost_breakdown()` currently calculates commission, stamp tax, transfer fee, and spread cost; those four amounts sum to `notional_cost()`. If no detailed fee model is supplied, a configured flat cost is recorded as spread cost. Temporary and permanent impact, opportunity cost, and financing cost remain zero until a model supplies them. These zero values are placeholders, not calibrated estimates.

Minimum commission is nonlinear when an order is split into fills. Its charging unit must be explicit. Before claiming cash conservation, test portfolio-value scaling together with minimum commission and verify that executed buys cannot make cash negative. A per-security, side, and trading-date unit is a possible policy, subject to broker-specific overrides; it is not a universal default established by this repository.

### A-share rules and timestamps

Execution rules are opt-in and default off, preserving the fixed comparison scenarios. `round_lot` rounds buys down to whole lots; sells can liquidate odd lots. `enforce_t1` limits sales to the pre-open `t1_available` snapshot, excluding shares bought that day. `enforce_price_limits` uses the configured `limit_up_col` and `limit_down_col` flags to skip buys at limit-up and sells at limit-down. `enforce_listing_status` uses `listing_status_col` and skips fills when the row is not `listed`.

If enabled rules require input columns that are absent, execution fails rather than silently proceeding without those rules. A warning records when the simulator runs with all A-share rules disabled.

Fills retain `signal_time`, `decision_time`, `order_time`, `fill_time`, and `valuation_time` in `Asia/Shanghai`. Corporate-action input hooks exist, but real dividend and split adjustments are not yet implemented. Dated fee schedules and more detailed checks separating execution from valuation prices remain open.

### Capacity diagnostics

The capacity report evaluates a portfolio-value and participation-rate grid. Its `capacity_calibration` includes `break_even_capacity`, `fill_rate_95_capacity`, `alpha_retention_90_capacity`, `sharpe_retention_90_capacity`, `marginal_return_per_unit_capital`, and `marginal_sharpe_retention_per_unit_capital`. Concentration uses `by_symbol` and symbol HHI. It adds `by_liquidity` when pricing includes a liquidity column and `by_industry` when positions include an industry column; those group reports include shares and HHI.

These outputs are diagnostics based on the supplied daily liquidity inputs. They do not model intraday queue priority, a broker-specific market-impact curve, or guarantee that an order can be filled. Use liquidity from the actual execution window when the strategy trades only during a limited part of the session.

### Period summaries and reproducibility

Period metrics are derived from daily NAV. Calendar-year returns compound within each year and retain `yearly_returns`, `years_count`, `best_year`, and `worst_year`. When source paths are supplied, run metadata can record `repo_commit`, `market`, `backend_name`, `capability_snapshot`, `config_hash`, `input_data_hash`, `positions_hash`, `pricing_hash`, `universe_fingerprint`, `calendar_window`, `fee_schedule_version`, `slippage_calibration_version`, `dependency_versions`, `random_seed`, `run_timestamp`, and `run_dir`. Missing version information is recorded as unknown or unversioned rather than inferred.

## Remaining work

- Apply real corporate-action values when a verified data source and contract are available.
- Add calibrated models for temporary and permanent market impact, opportunity cost, and financing cost.
- Improve checks that distinguish execution prices from valuation prices and detect timing leakage.
- Validate cash scaling together with per-order minimum commissions.
- Review a Backtrader differential adapter only for a concrete use case. Do not replace the native path on the basis of architectural compatibility alone.

## Backend status

There is no external backend adapter in the current supported path. LEAN remains an architecture reference, and Qlib/LEAN migration candidates are not part of `main`. Backtrader is a future evaluation candidate; vn.py is outside this repository's scope. `native.position_replay` remains the registered backend until an adapter passes the repository's integration gates and fixed-scenario comparisons.

## Regression coverage

Relevant implementation and tests include:

- Backend capabilities and canonical results are implemented in `packages/portfolio-backtester/src/portfolio_backtester/backends/base.py`; the optional native ledger is in `packages/portfolio-backtester/src/portfolio_backtester/backends/native.py`. Regression tests: `tests/test_ledger_stage2_contract.py`.
- The unified ledger adapter is in `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/results.py`. Regression tests: `tests/test_execution_ledger.py` and `tests/test_ledger_stage2_contract.py`.
- Cost breakdown and detailed fee calculation are in `packages/portfolio-backtester/src/portfolio_backtester/types.py` and `packages/portfolio-backtester/src/portfolio_backtester/_execution_models.py`. Regression tests: `tests/test_cost_breakdown.py`.
- Market-rule configuration is in `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/config.py`. Regression tests: `tests/test_execution_sim_market_rules.py` and `tests/test_execution_corporate_actions.py`.
- Capacity reports: `tests/test_capacity_report_phase5.py`.
- Yearly metrics and run metadata: `tests/test_run_metadata_phase6.py`.

The accounting regression gate also calls for cash and position-value reconciliation, NAV identity under zero return and zero cost, monotonicity under higher costs and tighter capacity, equivalence checks between Top-K targets and position replay, per-order minimum-commission checks, manually reconciled daily cash/holdings/NAV examples, and cases for sparse weights, missing prices, delayed fills, duplicate or out-of-order events, and third-party object isolation. Fixed-scenario differences between the native path and any approved adapter must be classified before an adapter can replace the native backend.
