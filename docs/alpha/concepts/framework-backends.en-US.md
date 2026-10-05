# Research backends and Qlib status

Language: English · [简体中文](framework-backends.md)

`alpha_research.backends` separates dataset construction, model training, and experiment recording behind stable interfaces. Callers organize the workflow through these interfaces. Artifacts contain ordinary Python metadata and workspace-defined file contracts.

## Current implementation

| Interface | Current implementation | Purpose |
| --- | --- | --- |
| `DatasetBackend` | `NativeDatasetBackend` / `QlibDatasetBackend` | Build a `ResearchDataset` from the existing modeling state; the Qlib adapter reuses cross-sectional normalization preprocessing |
| `TrainerBackend` | `NativeTrainerBackend` / `QlibTrainerBackend` | Train, predict, and calculate feature importance; the Qlib adapter uses `XGBModel` |
| `ExperimentRecorder` | `NullExperimentRecorder` | Return a serializable receipt without connecting to an external experiment service |

The Qlib adapter governed by ADR-0005 lives in `alpha_research.backends.qlib`. Install `pyqlib` separately through the `qlib` extra. Without it, the native path remains importable and can pass the standard gates. Qlib objects are not written to cross-repository artifacts.

## Conditions for Qlib support

The Qlib adapter implements the initial training and preprocessing pipeline. It is not yet a fully supported backend. Full support requires all of the following:

- The native path remains importable and passes all standard gates when Qlib is not installed.
- `DataHandler` and `Dataset` mappings preserve deterministic semantics for raw, inference, and learning data views.
- Tests cover point-in-time universes, time boundaries, processor fit windows, and leakage protection.
- Training, prediction, feature importance, and experiment recording have a reproducible difference report against the native baseline.
- Standard artifacts do not serialize Qlib runtime objects.

Do not describe Qlib as a fully supported backend until these conditions are met.

## Current validation command

```bash
uv run --locked --extra dev python -m pytest tests/test_research_backends.py -q
```

This test covers the current interfaces and native implementation. The standard `dev` gate does not validate the Qlib runtime.
