# Capital and reconciliation implementation plan

> For agentic workers: use superpowers:executing-plans inline.

Goal: distinguish investment returns from capital events and block mismatched books.
Architecture: pure public analytics/reconciliation plus existing event accounting.
Tech stack: locked Python, pandas, existing contracts and JSON.
Spec: [design](../specs/2026-11-08-falsification-primitives.md).

Review focus: missing/late snapshots, false completeness, zero capital, duplicate
cash events, pending-report state, fractional shares and tolerance misuse.

- [ ] Write failing cashflow return, external reconciliation and event tests.
- [ ] Implement analytics/capital_returns.py, backtest/reconciliation.py and minimal
  account_events.py changes; alias existing robust primitives, with synthetic tests.
- [ ] Run full provider tests, Ruff/format/typing, independent review and remote CI.
- [ ] Merge the provider before consumer pinning; clean only task resources.
