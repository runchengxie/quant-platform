# E2 promotion receipt

Language: English · [简体中文](e2-promotion-receipt.md)

`strategy_pipeline.e2_promotion_receipt` validates an explicit receipt specification and returns a JSON-ready record. It pins declared configuration, contract, manifest, and source-artifact files by SHA-256. It does not decide whether a strategy should be promoted or infer research findings from the inputs.

## Receipt contents

The output uses schema version `strategy_promotion_evidence.v2` and carries the caller-provided `strategy_id`, `profile_id`, `review_id`, `generated_at`, `status`, `research_window`, `checks`, and `limitations`, together with validated lineage. The receipt status must be one of `passed`, `failed`, `pending`, `diagnostic`, or `superseded`. The caller supplies check results; the writer requires a non-empty `checks` object but does not calculate or reinterpret those results.

Lineage identifies a `producer_repository` and repository commit SHAs. Each SHA must be 40 lowercase hexadecimal characters, and the producer must appear in the repository map. The writer hashes these declared files:

- `lineage.config` under `workspace_root`
- `lineage.current_contract` and each item in `lineage.data_manifests` under `data_platform_root`
- Each `lineage.source_artifacts` item under the root selected by its `location` (`workspace` or `data_platform`)

Every file path must be relative to its selected root, remain inside that root after resolution, and refer to an existing file. `source_artifacts` must be a non-empty list; `data_manifests` may be empty. `research_window` must provide non-empty `configured_start_date` and `end_date` strings. The writer checks that they are present but does not parse or validate date semantics.

## Python API

The function returns the materialized mapping and does not write it to disk:

```python
from pathlib import Path

from strategy_pipeline.e2_promotion_receipt import materialize_promotion_receipt

receipt = materialize_promotion_receipt(
    spec,
    workspace_root=Path("/path/to/workspace"),
    data_platform_root=Path("/path/to/data-platform"),
)
```

Both roots are required for the canonical A-share lineage. Prepare the check results and receipt status in `spec` before calling the writer.

## Command line

The standard-library CLI reads a JSON specification and writes the materialized receipt to the requested output path:

```bash
python -m strategy_pipeline.e2_promotion_receipt \
  --spec receipt-spec.json \
  --workspace-root /path/to/workspace \
  --data-platform-root /path/to/data-platform \
  --output promotion-receipt.json
```

The CLI creates parent directories for the output. If the output file already exists, it is overwritten. The command writes a local JSON file; it does not publish the receipt or upload any files.
