# Signal Artifact Contract

[简体中文](signal-artifacts.md)

`signals.parquet` is the standard scored-signal artifact passed from alpha research to backtesting or orchestration. Its metadata file is `signals.meta.json`. The contract is `alpha_research.signals`, version `1`.

## Required columns

| Column | Contract |
| --- | --- |
| `signal_date` | String in `YYYYMMDD` format. |
| `symbol` | Non-empty security identifier. |
| `raw_pred` | Numeric raw prediction score. |
| `signal_eval` | Numeric score used for evaluation. |
| `signal_backtest` | Numeric score used for backtesting. |
| `signal_direction` | Numeric direction value. |
| `rank` | Integer rank. If absent from the input frame, the builder ranks `signal_backtest` within each date, descending, with stable input order for ties. |
| `model_version` | Model version identifier. |
| `feature_set_id` | Feature-set identifier. |
| `eligible_for_backtest` | Boolean backtest-eligibility flag. |
| `eligible_for_live` | Boolean research-artifact eligibility flag; it does not authorize execution. |

The builder accepts common source aliases for date and score columns, normalizes the required fields, and preserves other input columns. The validator checks required columns, date format, non-empty symbols, numeric scores and direction, integer rank, and boolean eligibility fields.

## Read and write

```python
from pathlib import Path

from alpha_research.signal_artifact import (
    read_signal_artifact,
    write_signal_artifact,
)

signal_path = Path("artifacts/run/signals.parquet")
signals, summary = write_signal_artifact(scored, signal_path)
restored = read_signal_artifact(signal_path)
```

`write_signal_artifact` writes the Parquet file and metadata containing the contract, schema version, summary, caller metadata, and a `research.artifact-envelope.v2` envelope with producer, run, configuration, content-hash, and optional lineage information. `read_signal_artifact` validates by default; pass `validate=False` only when the caller deliberately handles validation.

## Ownership boundary

`eligible_for_live` records a research artifact's eligibility flag only. Execution approval, account constraints, and order authorization remain responsibilities of the orchestration and execution layers.

When field names, types, or meanings change, update `alpha_research.signal_artifact`, its contract tests, caller adapters, and this documentation together.
