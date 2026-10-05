# Alpha testing and quality checks

Language: English · [简体中文](testing.md)

This page documents the Alpha module's test-script entry point and coverage. It lives in `quant-platform`. The repository-wide test entry point is described in the [repository testing guide](../../testing.md).

## Install development dependencies

```bash
uv sync --locked --all-groups
```

## Shared entry point

```bash
scripts/alpha-research/dev/run_tests.sh <mode> [args...]
```

| Mode | Actual scope |
| --- | --- |
| `all` | Full `pytest` suite |
| `fast` | Compatibility alias for `all` |
| `unit` | Compatibility alias for `all` |
| `coverage` | Full test suite and coverage report for Alpha Python source |
| `lint` | Ruff checks |
| `format` | Ruff formatting check |
| `format-all` | Compatibility alias for `format` |
| `typecheck` | Configured `ty` scope |
| `typecheck-release` | Compatibility alias for `typecheck` |
| `maintainability` | Maintainability metrics and current budget |

Both `fast` and `unit` run the full test suite.

## Common commands

```bash
scripts/alpha-research/dev/run_tests.sh all
scripts/alpha-research/dev/run_tests.sh coverage
scripts/alpha-research/dev/run_tests.sh lint
scripts/alpha-research/dev/run_tests.sh format
scripts/alpha-research/dev/run_tests.sh typecheck
scripts/alpha-research/dev/run_tests.sh typecheck-release
scripts/alpha-research/dev/run_tests.sh maintainability
```

Coverage uses `pytest-cov` and currently has no minimum threshold. Python coverage reports do not include the Rust extension.

## Dependency security checks

The public root CI runs `pip-audit` against locked dependencies. See the [repository testing guide](../../testing.md) for the equivalent local check.

Examples of targeted tests:

```bash
uv run --extra dev python -m pytest tests/test_signal_artifact.py -q
uv run --extra dev python -m pytest tests/test_cpcv.py -q
```

## Research-backend test scope

`tests/test_research_backends.py` covers framework-neutral interfaces, `NativeDatasetBackend`, `NativeTrainerBackend`, `NullExperimentRecorder`, and the constraint that artifact metadata does not carry runtime model objects.

Qlib is not installed by the standard `dev` dependencies. After installing the `qlib` extra, run the deterministic training and prediction tests for `QlibTrainerBackend` in `tests/test_backends_qlib.py`. See [Research backends and Qlib status](../concepts/framework-backends.en-US.md) for its support conditions and validation requirements.

## Checks before pushing

In a managed `research-workspace` checkout, the shared top-level `pre-push` hook runs this repository's import checks, Ruff, formatting, `ty`, and full test suite according to the workspace manifest.

A standalone clone does not inherit the shared hook. Before pushing, run `lint`, `format`, `typecheck`, `all`, and `maintainability` from the commands above.

`typecheck-release` and `typecheck` use the same `ty` configuration. Both add five source roots to prevent false positives from internal relative imports caused by the project layout. `[tool.ty.src]` now includes the former release-check scope; the migration did not narrow type-check coverage.

## Test priorities

Tests should protect:

- Feature datasets and feature evidence
- Model training and evaluation
- Walk-forward, CPCV, and PBO
- Signal artifact fields and metadata
- Model-specific target-position rules
- Package imports and cross-repository dependency boundaries
- Maintainability metrics

Add a regression test before fixing a defect. New behavior should cover the normal path and at least one error or boundary path.

## Automation status

The public root GitHub Actions workflow runs repository-wide Ruff, formatting, strict `ty`, pytest, and dependency vulnerability checks on pull requests and pushes to the default branch. The local full quality gate and public CI use offline tests with locally constructed data. This script provides a shared entry point for coverage, type, and maintainability checks. The standard `dev` dependencies do not include Qlib; install the optional `qlib` extra to validate that backend separately. Tests for the real-data platform's minute-source directory run separately with the `market-data` extra.
