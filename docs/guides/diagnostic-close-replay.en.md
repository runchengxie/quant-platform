# Next-close diagnostic replay

Language: English · [简体中文](diagnostic-close-replay.md)

`portfolio_backtester.target_close_replay.replay_close_targets` compares target portfolios on an explicit trading calendar. It uses fractional adjusted units. It is not a broker-fill simulator or a cash-dividend ledger.

## Inputs and execution timing

The target table has `formation_date`, `symbol`, and `weight`. The price table is indexed by trading date, with symbols as columns. Targets must be non-negative, and weights for each formation date cannot exceed 1. Duplicate target keys and missing target price columns raise errors.

Each target is executed at the first available close strictly after its formation date. A formation with no later price date is not executed. Target weights are charged the default `cost_bps=25` basis points per trade direction, based on actual buy and sell notional. The replay solves for post-cost portfolio value so that cash, holdings, and fees remain self-financing. Holdings drift between rebalances rather than resetting to target weights every day.

Callers may provide Boolean matrices aligned exactly to the price table:

- `suspended`: for a confirmed suspension, existing holdings keep their last observed mark.
- `buy_blocked`: blocks buys in the specified symbols.
- `sell_blocked`: blocks sells in the specified symbols.

If a required trade is blocked, the entire basket rebalance is deferred. A newer target replaces the pending target. Directional blocks do not change observed valuation prices. Missing prices for held or traded symbols raise an error; the replay does not fill those gaps automatically.

This policy does not model exchange queues, partial fills, board-lot rules, or actual auction prices.

## Exposure changes

`exposure` is a decision-date-indexed position ratio in `(0, 1]`; it is also executed at the next available close. Between stock-selection dates, an exposure change scales the drifted holdings proportionally. Full liquidation requires an explicit zero-weight target for each stock. This interface does not calculate cash interest or separate corporate-action payments.

## Audit helpers

- `holdings_pnl.holding_pnl` computes per-symbol price P&L from prior-close units, including on exit dates. Its first row is an opening snapshot with zero P&L. Reconcile fees and cash returns separately.
- `drawdown_episodes.drawdown_episodes` records the peak, trough, recovery date, and underwater trading days. Episodes still open at the sample end are right-censored.
- `volatility_exposure.volatility_exposure` uses the sample standard deviation of the previous 60 return observations, with a 15% annualized target and 25% minimum exposure by default. It does not use leverage. Its output is a decision, not a fill.
- `matched_volatility.match_realized_volatility` rescales common-period net returns to the lowest realized volatility after the fact. It is diagnostic only: it uses future full-sample information and does not recalculate fees.

These helpers validate calculations under their stated inputs. Callers must separately verify historical data availability, dividend-adjustment conventions, delisting treatment, and practical execution feasibility.
