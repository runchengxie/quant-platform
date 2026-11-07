# Account feedback validation — 2026-11-07

Financial implementation tested at `80c7786`; subsequent changes in this task
record validation and navigation only. Target base was
`f16bcf8002dd2e25b7e7f9529237ad61c97d595a`, unchanged at final fetch.

The task worktree used Python 3.13.14 and dependencies installed by
`uv sync --locked --all-groups` (exit 0). Default-cache access initially failed in
the sandbox, and the temporary-cache network attempt failed; authorized setup
using the existing cache completed. Validation then used the installed environment
with a task-local cache and `uv run --no-sync` to avoid sandbox cache writes.

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run --no-sync pytest` | 0 | 2,115 passed, 25 skipped, 8 warnings; 210.49 seconds |
| `uv run --no-sync ruff check .` | 0 | All checks passed |
| `uv run --no-sync ty check` | 0 | All checks passed |
| `uv run --no-sync ruff format --check` on changed Python files | 0 | All 9 files formatted |
| `git diff --check` and staged equivalent | 0 | No whitespace errors |

Warnings concern existing pandas deprecations and NumPy division on constant
series. The first broad run failed the existing file-size gate after extending
the simulator. Input validation was factored into `_minute_validation.py`, leaving
the gate and its baseline unchanged; the full rerun above passed.

Tests cover partial fills, pending-order preservation, immutable snapshots,
strict decision clocks, dividend payment/ex references before the next decision,
strict default cost coverage and explicit legacy fallback, impact-aware cash
limits, persistent execution prices, checkpoint recovery, decay, flat-market
round trips and same-clock splitting. An independent reviewer reproduced and
identified three clock/default issues; all were fixed and rechecked without
remaining Important findings.

Real historical integration is recorded in the private Research repository.
This public test evidence does not calibrate liquidity, impact, signal horizons,
market completeness or strategy profitability. No production service is deployed.
