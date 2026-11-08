# Capital-return and reconciliation primitives

Expose strategy-independent mechanisms for separating capital changes from
investment results and comparing supplied local/external evidence without edits.

Unitized capital observations declare a complete valuation immediately before a
signed external flow and the valuation immediately after it. Enforce increasing
integer UTC ns clocks, finite positive NAV, and after=before+flow. Report exact
linked time-weighted return, net monetary gain and explicitly approximate Modified
Dietz return. Do not assume a unique IRR or infer missing valuations. Full redemption
ends the supported positive-capital series; callers must stop before that boundary.

Read-only reconciliation requires aligned economic clocks, external availability
by decision, complete source-bound snapshots, finite balances, integer shares,
normalized open-order evidence and physical fill IDs. Report cash/share/order/fill
mismatches and a blocked decision; never overwrite local books or contact a venue.

Extend the existing supplied-event account with declared cashflow and fee_adjustment
events at an already projected economic clock, preserving atomicity, delayed reports
and event-ID idempotency. Reject a fee credit or a balance below configured credit.
Dividends remain existing entitlement events, never external deposits.

Expose existing robust uncertainty primitives through a modern public portfolio
module; do not copy their implementation or imply a calibrated uncertainty radius.
Only synthetic fixtures and reusable mechanisms belong in this public repository.
