# Synthetic capacity sensitivity

Run `python scripts/benchmarks/capacity_pressure.py --output <new-data-directory>`
with the locked development environment. Output belongs outside source control.
The runner uses the canonical minute execution API without changing defaults.
It writes every input, generated order, fill, daily NAV and holding row, per-table
SHA-256 digests, and a result table. Every scenario executes twice to check determinism.

The 20 cases comprise two capital conventions, each with a baseline, one-factor
changes and a stressed corner. Capital is CNY 0.1/1/10 million, participation
1/5/10%, latency 0/1/3 elapsed minutes, and symmetric fees 0/10/30 bp.
Prices and liquidity remain synthetic and identical. Twenty symbols rotate allocations over five entry sessions followed by
two explicit zero-target T+1 unwind sessions (4,620 bars per case); terminal inventory remains visible
if liquidation does not complete. No case is selected for best return.

`capital_normalized_target` uses weights equal to CNY 50,000 divided by initial
capital; this fixes initial desired shares across capital cases. It is **not a
fixed order quantity experiment**: subsequent target sizing uses current NAV and
marks, and generated orders can change with fees and execution. `scaled_weight`
keeps 50% weights across capital cases. Compare generated order hashes and
side-specific quantities before interpreting a capital comparison. Idle cash in
the normalized schedule is not a capacity measurement.

Fill rates divide filled shares by generated parent desired shares, separately
for buys and sells. They do not divide by released slices or hypothetical broker
requests. Unfilled CNY values use each parent's sizing reference price, not a
terminal or execution price. Full order status/reason rows preserve expiry and
cash-or-participation ambiguity; the API does not isolate cash rejection counts.
NAV/P&L use terminal marks and require valid marking; remaining inventory is not
assumed sold. The fixture includes final-day observations for all twenty symbols.

The separate fixed-fill cost control freezes baseline quantities and prices and
subtracts proportional fees from baseline zero-fee P&L. It is conditional
accounting, with no rematching, affordability, tax or minimum-commission model.
Its monotonic fee result does not imply monotonic returns in the target schedule
runs, where sizing and fills can change. It is not another capacity curve.

These are public mechanism tests using historical-bar VWAP proxies. They do not
estimate live capacity, order-book queue position, impact, or real strategy returns.
