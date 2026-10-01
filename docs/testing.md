# Testing and quality checks

Language: English · [简体中文](testing.zh-CN.md)

This page documents local test entry points, public CI, and the actual scope of each check in `quant-platform`.

## Install development dependencies

```bash
uv sync --locked --all-groups
```

The project uses Python 3.12, with dependency versions pinned by `uv.lock`.

The repository's `research-contracts` package is a local path dependency. If tests still read an older installed copy after changing that package, reinstall it:

```bash
uv sync --locked --all-groups --reinstall-package research-contracts
```

Run the full test suite and public-release checks in a clean task worktree. A primary checkout's `.env.local`, `out/`, `state/`, and other worktrees are local environment state and can interfere with release-boundary checks.

## Verify installation boundaries

Use an isolated worktree to test the base environment so development dependencies cannot mask missing runtime dependencies:

```bash
uv sync --locked --no-default-groups
.venv/bin/python scripts/check_minimal_install.py
uv run --locked --no-default-groups --group test pytest -q tests/test_backtest_backends.py tests/test_backtest_bundle.py tests/test_optimizer_backends.py tests/test_execution_sim.py
uv sync --locked --no-default-groups --extra ml
uv run --locked --no-default-groups --extra ml --group test pytest -q tests/alpha/test_modeling.py tests/alpha/test_feature_engineering_short_series.py
```

CI runs these two installation modes on Python 3.12 and 3.13. The base environment checks that XGBoost, scikit-learn, `pandas-ta`, and their dedicated Numba, llvmlite, and NCCL dependencies are absent, then exercises actual backtesting and result bundles. The machine-learning environment tests model fitting and feature computation. A separate microstructure CI job installs `microstructure` and runs training-metric computation to verify its scikit-learn dependency. The full development environment also runs the complete test suite.

## Unified test entry point

```bash
scripts/dev/run_tests.sh <mode> [args...]
```

| Mode | Actual scope |
|---|---|
| `all` | Full pytest suite |
| `fast` | Compatibility alias for `all` |
| `unit` | Compatibility alias for `all` |
| `coverage` | Full suite with coverage reporting for Python sources under `packages/`, `scripts/`, and `research_contracts` |
| `contracts-coverage` | Runs `tests/contracts` and requires at least 80% coverage for installed `research-contracts` sources |
| `lint` | Ruff code checks |
| `format` | Ruff format checks |
| `format-all` | Compatibility alias for `format` |
| `typecheck` | Configured `ty` source scope |
| `typecheck-release` | Compatibility alias for `typecheck` |
| `maintainability` | Maintainability metrics against the current budget |

`fast` and `unit` do not reduce the test scope.

## Common commands

```bash
scripts/dev/run_tests.sh all
scripts/dev/run_tests.sh coverage
scripts/dev/run_tests.sh all tests/test_execution_contracts.py
scripts/dev/run_tests.sh all tests/test_backtest_backends.py
scripts/dev/run_tests.sh all -k position_backtest
scripts/dev/run_tests.sh lint
scripts/dev/run_tests.sh format
scripts/dev/run_tests.sh typecheck
scripts/dev/run_tests.sh typecheck-release
scripts/dev/run_tests.sh maintainability
```

The `coverage` mode requires `pytest-cov`. It generates a report without imposing a repository-wide minimum. `contracts-coverage` separately enforces an 80% floor for installed `research-contracts`. Python coverage reports exclude the Rust extension.

## Dependency security checks

Public CI uses `pip-audit` to check locked dependencies for known vulnerabilities. Run the same check locally with:

```bash
uvx --from pip-audit pip-audit --strict -r <(uv export --locked --all-groups --extra dev --extra microstructure --format requirements-txt --no-hashes --no-emit-project --no-emit-local --no-emit-package quant-platform --no-emit-package research-contracts --no-emit-package research-code-quality)
```

Current CI does not run Bandit or unused-dependency scanning. Before adding either gate, define the source and dependency scope it will scan.

## Pre-push checks

In a checkout with workspace governance, the shared top-level `pre-push` hook runs this repository's import checks, Ruff lint, formatting, `ty`, and the full test suite according to the workspace manifest.

A standalone clone does not inherit the shared hook. Before pushing, run the `lint`, `format`, `typecheck`, `all`, and `maintainability` modes listed above.

Public-release boundary checks use a clean export directory:

```bash
bash scripts/public_release/build_clean_export.sh \
  --revision HEAD \
  --destination /tmp/quant-platform-public-export
```

Do not treat local runtime outputs in a primary checkout as evidence of a clean public export.

## GitHub Actions status

`.github/workflows/ci.yml` runs public quality gates on pull requests and pushes to the main branch. `.github/workflows/docs.yml` builds MkDocs separately and publishes the online documentation. Local commands and the shared workspace `pre-push` hook provide feedback before remote checks.

Pull requests and main-branch pushes run repository-wide Ruff lint and formatting, strict type checks, the full pytest suite, and `pip-audit`. The Rust job builds the optional wheel separately and runs microstructure tests with `TICKNET_REQUIRE_RUST=1`. The documentation workflow uses strict MkDocs mode and checks links. The local `maintainability` mode checks the maintainability budget.

## Type-check scope

`scripts/dev/run_tests.sh typecheck` and `typecheck-release` use the configured `[tool.ty.src]` scope in `pyproject.toml` and enable `--error-on-warning`. The current scope includes `portfolio-backtester`, orchestration, execution, alpha, microstructure, and `scripts/`. CI runs the same strict check without passing a narrower path list.

Only two optional-dependency imports retain file-level exceptions: the Qlib backend requires the `qlib` extra, and the Rich renderer falls back to plain text when Rich is absent. Other diagnostics in configured source files fail the check.

## Test coverage priorities

The current suite primarily covers:

- Top-K portfolio construction and return calculations
- `BacktestSpec` serialization and consistency with historical entry points
- Position replay and exit rules
- Costs, slippage, and trading constraints
- Execution-capacity simulation
- Position contracts and strategy configuration
- A-share board-lot constraints
- Benchmarks, capacity, exposures, and reports
- Liquidity proxies, buffers, and turnover limits
- Framework-neutral order states, duplicate events, and out-of-order event reduction
- Normalized backend results and fixed reference scenarios
- Package imports and cross-repository dependency isolation
- Maintainability metric scripts

When adding a public entry point or changing an output contract, add behavioral tests, fixed reference cases, and import tests.
