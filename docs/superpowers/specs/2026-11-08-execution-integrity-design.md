# Execution integrity exploration

Provide reusable public analysis for three explicit evidence boundaries: Decimal
fill-prefix reconciliation across two backends; pooling long-only strategy sleeves
into a single execution account; and reporting cash versus residual marked wealth.
Existing public matchers and account ledgers continue to own execution and cash.

Fill-prefix balances reconstruct cash and raw shares from recorded fills grouped
at identical UTC nanosecond clocks. Decimal inputs, unique explicit fill identities,
finite values, nonnegative fees and integer shares are mandatory. This is not an
upstream intrafill account snapshot or a queue model. Report the first divergent
clock, preserve all mismatches, and separately compare authoritative daily ledgers.
Matched synthetic zero-spread clocks may agree; IOC and multi-bar continuation
must be an explicit expected difference, never normalized away.

Pool complete sleeve target snapshots only when schedules and decision clocks
agree. Fractions are fixed externally before outcomes; aggregate target weights
must remain long-only with total <=1. Execute the pool through exactly one minute
owner and one impact state. Compare with isolated accounts of identical total
capital. Do not attribute pooled fills or performance to sleeves, model independent
broker accounts, or promise fairness between strategies.

Exit wealth reports cash, residual quantities, marked value and mark clocks. Full
cash-realized wealth exists only with zero residual inventory and no receivables;
missing held marks produce unknown valuation, never a zero holding or invented
sale. Actual liquidation still requires existing owner execution.

Approaches: multiple new matchers risk inconsistent capacity; a jointly stepped
multi-account venue is larger than required for an initial experiment; one pooled
account provides a bounded shared-capacity baseline now. Independent accounts
remain separate counterfactuals, not a valid joint market simulation.
