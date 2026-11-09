# TickNet data boundary

Language: English · [简体中文](data-boundary.md)

Platform 0.2.0 supports Python 3.12 and 3.13 with Engine Core 0.2.0 and SDK 0.3.0 at merged revision `51ab1e8cb2267d938a0681b81f2419d504ed91cc`. Core and SDK use the same exact VCS pin; no PyPI publication is required. Engine owns minute execution, paper accounts, reservations, execution planning and deterministic matching/replay/impact. Compatibility modules expose the identical Core objects; the pending adapter preserves Platform's full sparse validation and actual optimizer result. OSQP, statistical risk, research calibration, `pool_sleeves`, daily backtests and model training remain Platform responsibilities. Aliases stay for at least two minor-release cycles and until all recorded supported consumers migrate.

The optional native distribution belongs only to Engine; select `backend="rust"` explicitly after installing its wheel. There is no silent fallback. Native impact raises `NotImplementedError` before mutation because per-fill execution evidence is unavailable. Generator and `sqrt_law` remain Platform consumers; synthetic diagnostic slopes are not a calibrated market law. Account raw schema 2 and `execution-state.v2` identify the relocated owner. Older checkpoints require the full original pinned Platform/Runtime/Go/dependency environment; never convert or rebind them.


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
