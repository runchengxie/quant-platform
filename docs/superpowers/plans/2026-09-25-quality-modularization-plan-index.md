# Quant Platform Quality and Modularization Plan Index

This plan set executes the approved design in independently reviewable work packages. Each package produces its own testable PR from the latest `origin/main`, and later packages rebase by creating a fresh worktree after prior merges.

## Work packages

1. [Research contracts coverage and clock causality](2026-09-25-research-contracts-coverage.md)
2. [Portfolio feasibility diagnostics](2026-09-25-portfolio-feasibility-diagnostics.md)
3. [Execution simulation split](2026-09-25-execution-simulation-split.md)
4. [Eventstream training split](2026-09-25-eventstream-training-split.md)
5. [Output summary split](2026-09-25-output-summary-split.md)
6. [Configured Ruff and ty debt](2026-09-25-configured-static-quality-debt.md)
7. [Production promotion](2026-09-25-quant-platform-production-promotion.md)

## Execution order

- Run the contracts and portfolio feasibility packages first because they establish the causal and optimization invariants used by the later modules.
- Run each module split as its own PR. Apply its local Ruff and `ty` fixes with the split, then continue the complete configured static-debt cleanup by owning package.
- Make the complete configured `ty` surface blocking and remove the remaining Ruff exclusions only after every included path passes.
- Run full CI, dependency audit, maintainability checks, and release readiness against the merged `main` SHA.
- Promote only that exact `quant-platform` SHA and perform the import smoke test in its prepared release environment.

## Cross-package acceptance

- Every public import path remains compatible through the relevant module split.
- Existing artifact, optimizer, simulation, training, and output schemas remain stable unless a separately approved design provides a migration.
- `research_contracts` coverage measures the installed package and passes the 80% statement threshold.
- `ruff check .` covers former exclusions and reports no unexplained finding.
- `ty check --error-on-warning` passes the full `tool.ty.src.include` surface and CI runs the same blocking command.
- All required GitHub checks pass before merge or production promotion.
