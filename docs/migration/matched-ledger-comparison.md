# Matched synthetic ledger comparison

[简体中文](matched-ledger-comparison.zh-CN.md)

The maintained Python execution simulator and the independent Rust engine produce matching order statuses, fill notionals and daily financial balances for the two-session synthetic case below. Quantities are inferred from Python notionals using the declared fixture prices. This establishes a narrow compatibility example. Real caller migration still requires its own input and financial-rule checks.

`scripts/benchmarks/compare_engine_ledgers.py` runs both backends. Python constructs orders from target weights through `simulate_execution_adjusted_nav`. Rust receives explicit market-order quantities through the independent SDK and uses NautilusTrader for execution and accounting. The script only converts their evidence into comparable fields.

## Shared assumptions

The account starts with CNY 10,000 and holds one synthetic instrument, AAA. Both paths use raw prices and a buy lot of 100 shares, with T+1 enabled. The first target weight is 10%, followed by a zero target the next day.

Python uses one daily price for both execution and valuation. The Rust request therefore declares zero-spread quotes at the opening and valuation timestamps, at the same daily price. Quotes and daily capacity are deliberately large enough to fill both orders completely. These quotes are synthetic inputs created for this experiment. The tool does not derive executable quotes from historical OHLCV bars.

Both sides charge 10 bps commission with no minimum. Stamp duty, transfer fees and slippage are zero. Python receives a `DetailedTradeFeeModel` with those exact settings. Its flat `transaction_cost_bps` remains zero because that option also changes target sizing to reserve estimated costs. The explicit fee model keeps the initial requested notional at CNY 1,000, matching the Rust request for 100 shares.

| Event | Quantity and price | Commission | Cash | Position value | NAV |
| --- | --- | --- | --- | --- | --- |
| 2025-01-02 buy and valuation | Buy 100 at 10 | 1 | 8,999 | 1,000 | 9,999 |
| 2025-01-03 sell and valuation | Sell 100 at 12 | 1.2 | 10,197.8 | 0 | 10,197.8 |

## What the comparison checks

The report compares each order's symbol, side, date, inferred filled quantity and final status. For fills, it compares Python's fixture-assumed prices and inferred quantities against actual engine prices and quantities, alongside commission. Daily rows compare cash, inferred held quantity, position value, commission and NAV. The report retains each backend's original evidence alongside the normalized tables.

The legacy evidence records filled notional and provides no independent fill-price field or share ledger in this case. Because this fixture has one instrument and a declared single price per day, the normalizer divides that notional by the fixture price to infer quantity, then accumulates signed fill quantities for daily holdings. The report's `python_derived_fields` records these assumptions. This conversion is specific to the fixture. It does not establish a general adapter for multi-price fills or corporate actions.

Numeric comparison uses a fixed absolute tolerance of `0.00000001` to allow Python floating-point arithmetic at the boundary. Decimal engine values stay decimal during comparison. Dates, statuses and row counts must match exactly. The command exits with status 1 if any normalized field differs.

One regression case deliberately changes only the first Rust valuation quote from 10 to 11. First-day position value and NAV rise by 100 while final NAV remains 10,197.8. The comparison reports both daily differences. This demonstrates why matching final returns alone provides insufficient migration evidence.

## Reproduce

Install the locked platform development environment and select an immutable engine executable. Verify its digest against the selected build record before passing it to the tool.

```sh
uv sync --locked --all-groups
uv run --locked python scripts/benchmarks/compare_engine_ledgers.py \
  --engine-executable /releases/engine/quant-backtest-engine \
  --engine-sha256 <verified-executable-sha256> \
  --engine-source-revision <full-engine-source-revision> \
  > /data/quant-platform/tasks/ledger-comparison.json
```

The output directory must already exist outside the source repository. The SDK checks executable bytes before running. A source revision records build provenance separately from the executable digest.

The `engine-sessions` CI job builds the provider pinned in `.github/workflows/ci.yml` and runs `tests/test_engine_ledger_comparison.py` against that real binary. Local integration tests use `SESSION_ENGINE_BINARY` and `SESSION_ENGINE_SHA256`. Without those variables, the two real-engine tests are skipped and the Python/comparison regressions still run.

## Scope of the evidence

The fixture compares financial values by session date. Python's date-level audit fields and the Rust request's explicit intraday timestamps remain different. This experiment does not validate intraday clock parity or point-in-time input availability.

Both orders fill completely. T+1 is enabled, but no same-day sale is attempted. Partial fills, order persistence, corporate actions and dated tax rules need separate cases. Daily notional capacity and displayed quote liquidity remain different models even though neither constraint binds here.

Callers with target weights and OHLCV bars still need a declared conversion policy and data-availability audit before using a quote-driven engine. Keep their Python workflow until those requirements pass the [removal gates](portfolio-boundaries.md#final-removal-gates).
