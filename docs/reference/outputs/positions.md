# Position output contract

Language: English · [简体中文](positions.zh-CN.md)

This page describes the stable fields, validation behavior, and downstream use of `positions_by_rebalance.csv`. The contract and writer are implemented in [`contracts.py`](https://github.com/runchengxie/quant-platform/blob/main/packages/portfolio-backtester/src/portfolio_backtester/contracts.py) and [`positions_artifact.py`](https://github.com/runchengxie/quant-platform/blob/main/packages/portfolio-backtester/src/portfolio_backtester/positions_artifact.py); behavior is covered by [contract tests](https://github.com/runchengxie/quant-platform/blob/main/tests/test_contracts.py) and [artifact tests](https://github.com/runchengxie/quant-platform/blob/main/tests/test_positions_artifact.py).

## Canonical file and contract

The canonical file name is:

```text
positions_by_rebalance.csv
```

Its contract name is `portfolio_backtester.positions_by_rebalance`, schema version `1`.

## Required fields

| Field | Validation | Meaning |
| --- | --- | --- |
| `rebalance_date` | Must parse as a date | Rebalance date for the target positions |
| `symbol` | Must be non-empty after string conversion | Security identifier |
| `weight` | Must be convertible to numeric | Target weight |

Dates in `YYYYMMDD`, `YYYY-MM-DD`, and other pandas-parseable formats are accepted. Use `YYYYMMDD` for consistent cross-system exchange.

## Common optional fields

| Field | Meaning |
| --- | --- |
| `entry_date` | Planned entry date |
| `side` | Position direction, such as `long` |
| `signal` | Score used when constructing positions |
| `rank` | Security rank in that rebalance's candidate set |

Specialized portfolio constructors may add fields such as sleeve, theme, industry, or model version. Readers should preserve unknown columns and depend only on agreed fields.

## Example

```csv
rebalance_date,entry_date,symbol,weight,side,signal,rank
20260102,20260105,000001.SZ,0.40,long,1.25,1
20260102,20260105,600000.SH,0.35,long,1.10,2
20260102,20260105,000002.SZ,0.25,long,0.98,3
```

## Validation scope

`validate_positions_by_rebalance_frame` checks:

- Whether the three required columns exist
- Whether `rebalance_date` parses as a date
- Whether `symbol` is non-empty
- Whether `weight` can be converted to numeric

The contract does not automatically check:

- Duplicate symbols on the same date
- Whether weights sum to 1 for each rebalance
- Negative weights
- Whether `side` contains only allowed values
- Whether `entry_date` is after the rebalance date
- Whether symbols match a specific market format

These rules depend on portfolio type and caller requirements. Add stricter checks in the position-producing module and cover them with tests when needed.

Use the validation helpers as follows:

```python
from portfolio_backtester import (
    assert_positions_by_rebalance_frame,
    validate_positions_by_rebalance_frame,
)

issues = validate_positions_by_rebalance_frame(positions)
assert_positions_by_rebalance_frame(positions)
```

`validate_positions_by_rebalance_frame` returns a list of issues. `assert_positions_by_rebalance_frame` raises `ValueError` when the frame is invalid.

## Writing the artifact and envelope v2

`write_positions_by_rebalance_artifact` writes `positions_by_rebalance.csv` and the companion `positions_by_rebalance.meta.json`. Under its `artifact_envelope` key, the metadata carries a `research.artifact-envelope.v2` envelope whose `content_sha256` is the SHA-256 of the written CSV.

```python
from portfolio_backtester import write_positions_by_rebalance_artifact

csv_path, meta_path = write_positions_by_rebalance_artifact(
    positions,
    output_dir,
    run_id="run-20260818",
    configuration={"top_k": 20, "weighting": "equal"},
    lineage=[("signals.parquet", signals_sha256)],
)
```

`run_id` is required. `configuration` and `lineage` are optional; they are used for `configuration_sha256` and the envelope lineage, respectively. The envelope is an additional metadata field alongside `artifact_type`, `schema_version`, file name, row count, and required-column list.

## How position replay uses the frame

`run_position_backtest` first applies the base contract validation and then:

- Converts `symbol` to string and `weight` to numeric
- If a `side` column is present, keeps rows whose value is `long` (case-insensitive)
- Keeps only positive weights
- Aggregates duplicate symbols within a rebalance date by summing their weights
- Renormalizes the remaining weights by default
- Allows under-invested weights to remain as cash when `preserve_gross_exposure=True`

`PositionBacktestConfig` still contains `long_only`, but `long_only=False` does not enable short replay. Normalization still keeps only `side=long` and positive weights; the flag is recorded in the result summary. Use a score-driven entry point that supports long-short construction when that is required. Changing this behavior requires coordinated implementation, test, and contract updates.

Holding periods come from a separate `periods` table, which must contain at least `rebalance_date`, `entry_date`, and `exit_date`. The `entry_date` in the positions file is primarily descriptive and for interchange; replay uses the `periods` table.

## Missing prices

If an entry or exit price cannot be resolved under the configured price and exit policies, the affected position is removed from that period. By default, the remaining weights are renormalized.

This changes the number of securities included in the replay. Inspect the period outputs for:

- `missing_price_count`
- `position_count`
- `gross_exposure`
- `cash_weight`

To retain uninvested cash, configure:

```python
PositionBacktestConfig(preserve_gross_exposure=True)
```

## Other file names

`positions_current.csv`, `trades_by_rebalance.csv`, and `latest.json` may be produced by higher-level orchestration or publication flows. They are not stable output contracts of this package.

Public integrations should prefer `positions_by_rebalance.csv` and the contract validation helpers. Higher-level projects may define their own snapshots, trade deltas, and convenience pointers, but should document their fields and update rules separately.

## Compatibility guidance

- Adding optional fields is usually backward-compatible.
- Removing or renaming required fields breaks the contract.
- Changing date meaning, weight meaning, or duplicate-row handling requires a contract-version update.
- Keep column names stable when writing files.
- Record the model version and parameters used to generate positions.
- Document impacts on downstream readers in the pull request.
