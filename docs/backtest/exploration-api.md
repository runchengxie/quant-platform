# Backtest exploration APIs

These mechanisms support explicit research experiments. They do not certify data,
broker execution, a strategy or a production deployment.

- `backtest.research_admission.ResearchContract` uses UTC integer nanoseconds.
  `assess_admission` blocks known temporal/semantic violations even when other
  evidence is unknown. Unknown evidence permits mechanism-only work and blocks
  formal use. Evidence labels/references are caller declarations requiring audit.
- `backtest.stress.JointStress` and `stress_bars` transform prices and capacity
  together without modifying inputs. Prices respect the supplied daily limits;
  VWAP and amount remain consistent with synthetic volume. Randomness is keyed by
  seed, symbol, UTC event clock and stream, independent of order/draw counts.
  Risk and impact multipliers must be applied explicitly by the caller. No scenario
  distribution is a future probability estimate.
- `backtest.checkpoints.ExecutionState` composes `AccountEventAdapter` and
  `LinearImpact`. Physical fills must go through `apply_fill` with an external
  reference price. Both owners are cloned and commit together; physical fill IDs
  deduplicate impact as well as accounting. Store every mutable policy/driver field
  in `policy_state`, advance `cursor` only after each committed input action, and
  bind the full immutable tape through `EventAccountConfig.input_binding`.
  Restore validates content, config/source/input identity and keyed-RNG version.
  External policy closures, sockets and unsaved side effects are not recoverable.
- `analytics.cost_scope.fit_cost_scope` fits nonnegative base/square-root
  participation coefficients on signed decision-mid shortfall including fees once.
  Supply both completed_ns and available_ns: incomplete/unavailable outcomes cannot
  enter the fit. Participation is filled shares / market shares for the same
  execution interval. Calibrate each side/liquidity bucket/execution horizon
  separately; coefficients preserve source binding, cutoff and observed domain.
  `validate_cost_scope` requires the same explicit source binding and only later
  observations, retaining unsupported scopes and signed errors. Minimum sample
  counts establish mechanics, not statistical adequacy or real calibration.
- `portfolio.multiperiod.plan_trades` accepts a `MultiPeriodRequest` containing
  decision-time forecasts and PSD covariance estimates. Weights and costs use
  fixed decision-NAV units; expected returns never fund cash. Per-period holdings,
  trade caps, tradability, reserved cash and cumulative estimated costs constrain
  the path. There is no terminal liquidation or automatic future-data access.
  Execute only `first_trade`, then replan from actual delivered state. Independent
  residual checks reject failed/infeasible solves. This is an unlevered research
  prototype, without financing, shorts, exchange queue or robust model guarantees.

Account economic/visible state and conservative causal-prefix delivery remain
owned by the event adapter. The existing synthetic Engine ledger comparison has
its own narrower scope and does not certify delayed-report or impact parity.
