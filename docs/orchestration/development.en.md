# Development and publication checks

Language: English · [简体中文](development.md)

## Repository checks

Run the checks defined for the current repository from its root:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
```

The orchestration control-plane tests are under `tests/orchestration/control_plane/`. They use synthetic owners and publishers; they do not require private modules, credentials, production services, or strategy data.

## Clean-root publication audit

The clean-root export instructions recorded in the earlier publication audit are not currently reproducible from this checkout. The exporter expects `docs/public-surface-manifest.json`, while the reviewed manifest is at `docs/orchestration/public-surface-manifest.json`. That manifest also names 41 paths out of 50 that are absent from the current repository layout. Do not treat the old export result as a current release check or run the old commands as if they passed.

The historical [publication audit](publication-audit.md) records the evidence and its scope. Before publishing a clean-root package, reconcile the manifest with the current code and tests, update the exporter and its tests, then rerun the clean-tree and full-history audits. This page does not authorize changing repository visibility.
