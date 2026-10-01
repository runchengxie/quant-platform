# Execution Allocation Reference Data

Language: English · [简体中文](allocation-reference.zh-CN.md)

`portfolio_backtester.allocation_reference` reads execution-side prices and round-lot sizes, then safely joins them to portfolio-selection results.

## Input format

Reference files may use CSV, TXT, JSON, JSONL, or Parquet and must include:

- `symbol`
- `price`
- `round_lot`
- `price_date`

Every row must have the same `price_date`. `price` and `round_lot` must be positive, `round_lot` must be an integer, and `symbol` values must be unique. If `order_book_id` is absent, the module uses `symbol` as its default.

## Usage

```python
from portfolio_backtester.allocation_reference import (
    join_allocation_reference,
    load_allocation_reference,
)

reference = load_allocation_reference("reference.csv")
ready = join_allocation_reference(selection, reference)
```

The join preserves the selection order. It fails if a selected security has no price or round-lot data, preventing the execution layer from generating incomplete quantities.

Position filtering is provided by `portfolio_backtester.allocation_selection`. It selects the latest saved holdings snapshot before a specified date, then filters by direction and rank to produce Top-N positions. It does not read strategy configuration or runtime directories.

Text-table and CSV rendering for allocation results is provided by `portfolio_backtester.allocation_rendering`. Text tables align columns using English and Chinese character widths; CSV output preserves the DataFrame column order.

## Responsibility boundary

This module reads, validates, and joins reference assets required for execution. It does not generate market prices, choose securities, or send orders. The caller supplies the data source and snapshot date and records them in the run artifacts.
