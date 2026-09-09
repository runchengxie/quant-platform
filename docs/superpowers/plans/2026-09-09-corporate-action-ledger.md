# Corporate-action ledger implementation plan

> For agentic workers: use superpowers:subagent-driven-development. Track steps with checkboxes.

Goal: add opt-in raw-share corporate-action accounting to the existing continuous execution ledger.

Architecture: immutable caller-normalized events feed a run-local rights ledger. Existing execution remains responsible for orders, fills, capacity, fees and T+1. Corporate actions are processed before orders and record-date entitlements captured after orders. Legacy calls retain their existing results.

Tech stack: Python, pandas, dataclasses, pytest.

Spec: this public implementation contract expands the user-approved generic corporate-action scope. No private strategy, vendor data or parameters enter this repository.

## Global Constraints

- Reuse the continuous execution engine. Do not create another backtester.
- Public mechanisms and synthetic fixtures only. No credentials, vendor assumptions or real datasets.
- Explicit opt-in raw-price basis. Reject adjusted-price basis with corporate actions.
- Every event has a unique identity, symbol, available date, record date and ex date. Cash actions require a payment date. Stock distributions require a tradable date. Reject malformed, duplicate or temporally inconsistent events.
- Entitlements are based on record-date closing shares, including that day's buys and excluding sells. Recognize economic receivables at ex date so cum-dividend prices do not double count rights on record date.
- Cash receivables count in NAV but are never spendable before payment. Stock receivables are marked at current raw price and are never sellable before their explicit tradable date. Payment transfers value, without producing another return.
- Require available_date <= record_date < ex_date, and relevant payment/tradable date >= ex_date. Strict calendar coverage within the run. Out-of-window settlements remain receivables. A run starts with cash only, so events recorded before its first executable day confer no rights.
- Split/bonus distributions use explicit additional shares per record-date share, not an inferred price adjustment. Fractional share entitlement is retained as a disclosed analytical convention until lot-policy work, with no invented cash-in-lieu proceeds.
- On an ex date, cancel outstanding orders for the affected symbol with an explicit corporate-action status rather than carrying pre-action quantities across the event. Fresh same-day target orders may be built afterward. Report this convention.
- Missing raw marks around held corporate actions fail closed, including suspended instruments without an explicitly supplied valuation mark. Never carry a cum-action mark silently through ex date.
- Preserve all no-action API/results, and dated fee behavior. No default historical tax rate: accept an explicit flat withholding rate per event, disclose it, and do not call it holding-period tax replication.

### Task 1: Corporate-action accounting integrated with execution

Files:
- Create `packages/portfolio-backtester/src/portfolio_backtester/corporate_actions.py`: immutable `CorporateAction` event and validation.
- Create `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/corporate_actions.py`: run-local rights state, opening-day settlement and closing entitlement capture.
- Modify `execution_sim/core.py`, `models.py`, `results.py`, `reporting.py` and public exports as needed for explicit optional inputs and opt-in receipts.
- Test `tests/test_execution_corporate_actions.py`.
- Document `docs/corporate-action-ledger.md`.

Interfaces:
- `CorporateAction(event_id, symbol, available_date, record_date, ex_date, cash_per_share=0.0, cash_pay_date=None, stock_per_share=0.0, stock_tradable_date=None, withholding_rate=0.0)`.
- Extend `simulate_execution_adjusted_nav(..., corporate_actions=None, price_basis=None)` where non-None actions require `price_basis='raw'`. Explicit empty actions still establish raw-share contract.
- Expose action and end-of-day holdings receipts in the result through backward-compatible optional DataFrame fields. Include cash receivable and stock receivable market value in opt-in daily output, keeping legacy columns unchanged when disabled.

- [ ] Write hand-calculated integration tests first. A 1000 cash account buys 100 shares at 10 on record date, then price becomes 9 on ex date with 1 cash/share due two sessions later. Expected ex-date invested value 900, cash receivable 100, cash 0, NAV 1000. Payment produces cash 100 and zero receivable without changing NAV. A new target on the intervening day cannot spend the 100 receivable.
- [ ] Test selling after record date retains rights, buying after record date obtains none, future event changes do not alter earlier rows, 20% explicit withholding produces NAV 980, duplicate event identity and invalid dates fail, raw basis required even for empty action list, missing marks on ex date fail, unrelated events do not cancel unrelated orders.
- [ ] Test a 1-for-1 bonus: 100 record shares at 10 become 100 held plus 100 stock receivable at 5 on ex date. NAV remains 1000. Before tradable date only original shares can sell. On tradable date the additional 100 shares transfer to sellable shares with no NAV jump. Cover record-date buys and T+1 across weekend/holiday in a supplied session calendar.
- [ ] Run `uv run pytest tests/test_execution_corporate_actions.py -q` and save expected missing-feature failures.
- [ ] Implement event normalization/validation and ledger hooks. The core accounting identity is `nav = cash + held_shares_value + cash_receivable + stock_receivable_value`. Capture rights after fills on record date. On ex date create rights exactly once. On payment/release date settle exactly once. Use fresh per-run state. Include rights in target sizing but not spendable cash or sellable quantity.
- [ ] Run focused tests and regression tests for execution, dated fees, market rules and quote safety. Confirm exact no-action equivalence.
- [ ] Run `uv run ruff check .`, `uv run pytest -q`, `git diff --check`, self-review, commit and write RED/GREEN evidence and limitations to the task report.

## Subsequent independent slices

Dated quantity schedules and private data normalization follow this accounting slice. The full matched performance matrix depends on both and on audited historical inputs. This plan does not claim those deliverables are complete.
