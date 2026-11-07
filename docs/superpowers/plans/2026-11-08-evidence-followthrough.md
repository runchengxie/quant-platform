# Recoverable minute execution plan

> For agentic workers: use superpowers:executing-plans inline.

Goal: step and recover the existing minute matcher with explicit delayed reports.
Architecture: a public session composes the existing internal economic simulator.
Tech stack: locked Python, pandas and JSON.
Spec: [design](../specs/2026-11-08-evidence-followthrough.md).

- [x] Add parity, delayed-report and every-boundary recovery regressions.
- [x] Implement tagged checkpoints, immutable policy observations and entry guards.
- [x] Test multi-day T+1, fees, policy and impact type binding and input tampering.
- [ ] Complete full validation and independent review, then PR and merge.
