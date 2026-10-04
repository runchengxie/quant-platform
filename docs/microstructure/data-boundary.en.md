# TickNet data boundary

Language: English · [简体中文](data-boundary.md)

Generic market-data ingestion, normalization, quality checks, versioning, and publication belong to `quant-market-data-platform`. The current `ticknet` package does not connect directly to that project's providers or published assets. Downstream research projects supply versioned data manifests and labels.

## Ownership

`quant-market-data-platform` owns provider integrations, raw landing, canonical schemas, general-purpose data-quality checks, provenance, and published assets.

`ticknet` owns model-specific event-stream packing and loading, window construction, feature representations, labels, leakage checks, training splits, tensor materialization, training, replay, and evaluation.

```text
quant-market-data-platform
  provider -> ingest -> raw -> standardize -> canonical -> quality/provenance -> published assets

downstream research project
  versioned inputs and labels -> ticknet datasets/windows -> train/evaluate
```

Cross-project handoff is managed by downstream projects. Reusable market-data cleaning belongs in `quant-market-data-platform`; transformations used only for model inputs belong in `ticknet`. This ownership boundary does not imply that this repository already implements a QMD adapter or a particular published-file contract.

## Enforced boundary

The current implementation includes dataset, packing, and loading code under `ticknet.eventstream`. It does not contain the former documentation's `canonical_adapter`, `nextday.snapshot_features`, or `nextday.snapshot_io` modules. `tests/test_microstructure_data_boundary.py` checks that TickNet source and runtime dependencies do not directly import or depend on `quant_market_data_platform`, `tushare`, or `rqdatac`. A future schema-only distribution should be reviewed separately before adding it as a dependency.
