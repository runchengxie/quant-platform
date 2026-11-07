# Exploration mechanisms validation — 2026-11-08

Implementation `15d8f26f587007c3c97f775e915b3046e0d20e56` passes the complete
locked all-groups Platform suite: 2,140 passed, 25 skipped, exit 0, 96.31 s.
Eight existing pandas/NumPy deprecation or constant-series warnings remain.
Ruff, complete formatting and strict ty checks pass. No baseline was relaxed.

Synthetic acceptance covers known future training even with unknown model clocks,
unknown formal evidence, event-keyed order-invariant joint stress, full economic
and visible account/impact/policy checkpoints at every replay boundary, cancel
races and duplicate physical reports, atomic price-limit rejection, completion
and availability cutoff separation, source-bound cost holdouts and extrapolation
rejection, analytic horizon solutions, cash/fees/reservations, PSD risk and
infeasible plans.

The fixed real Engine binary for source
`c65548a4ee1e938125cce1edbcc282c760c4c8f2` also passes all 14 tests in
`tests/test_engine_ledger_comparison.py` when its actual SHA-256 is supplied.
That existing comparison covers its declared synchronous orders/fills/daily
balances and retains excluded semantics. It does not certify asynchronous
recovery or market-impact equivalence across backends.

Commands: `uv sync --locked --all-groups`; then the installed environment via
`uv run --no-sync pytest`, `ruff check .`, `ruff format --check .` and
`ty check --error-on-warning`. Task-specific cache directories avoid sandbox
writes to shared caches. Private campaign data and raw logs stay in Research DATA.
The companion [API boundaries](exploration-api.md) distinguish mechanism evidence
from market calibration and formal research admission. Subsequent task commits
record validation/navigation only.

The first remote CI run caught bold markup in this newly added receipt, which
violated the repository documentation-style gate. The markup was removed and
both documentation test groups rerun; no implementation or test gate changed.
