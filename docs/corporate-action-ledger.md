# Raw-share corporate-action ledger

`simulate_execution_adjusted_nav` now accepts an optional tuple of caller-normalized `CorporateAction` events. The option is deliberately opt-in. Existing calls keep their previous result shape and price-return behavior.

## Contract

- Events require `available_date <= record_date < ex_date`.
- Cash distributions require `cash_pay_date`, and stock distributions require `stock_tradable_date`.
- Dates must be supplied execution-calendar sessions when they fall inside the simulated interval.
- `corporate_actions` requires `price_basis="raw"`, including an explicitly empty list.
- Duplicate event IDs and malformed amounts are rejected.
- Rights are calculated from record-date closing shares after that day’s fills. Cash rights become receivables on the ex date and become spendable on the payment date. Stock rights are marked at the raw price and become sellable on the supplied tradable date.
- A flat withholding rate may be supplied per event. It is an explicit analytical assumption and does not represent historical tax replication.
- Missing raw marks around an outstanding corporate action fail closed.

The opt-in result adds `actions` and `holdings` receipts. Daily rows add `cash_receivable` and `stock_receivable_value`. The summary records the accounting conventions. The event ledger does not infer price adjustments, cash-in-lieu proceeds or missing settlement dates.

## Scope boundary

This is a public accounting mechanism with synthetic fixtures. It does not provide historical Chinese broker fees, vendor corporate-action completeness, board-specific quantity schedules or a live trading claim. Private research must normalize and hash its input events before invoking it.

The private research audit found that an event input can contain later revisions or multiple report periods for one ex-date. Such groups remain quarantined until an independent source resolves the economics.
