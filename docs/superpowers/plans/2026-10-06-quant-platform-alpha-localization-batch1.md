# Quant Platform Alpha Localization Batch 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add accurate English canonical guides for the three active Alpha/research topics currently available only in Chinese.

**Architecture:** Preserve the existing Chinese source URLs and add paired `.en-US.md` pages. Register English pages with the locale hook and English MkDocs navigation, link each Chinese page to its English counterpart, and update the localization status and Alpha index. No research behavior or machine-readable identifiers change.

**Tech Stack:** Markdown, MkDocs Material, Python documentation contract tests, pytest.

**Spec:** `docs/LANGUAGE_MIGRATION_STATUS.md`; source pages and implementations listed per task.

## Global Constraints

- Canonical copy is in English; Chinese pages remain faithful companions.
- Verify claims against implementation, configuration, CLI, tests, and project structure.
- Keep API names, parameters, identifiers, and code examples unchanged.
- Do not imply production readiness or results not demonstrated by code and tests.

## Review Focus

- Locale routing must show only the selected language in the sidebar while preserving both page URLs.
- The fundamental forecast page must distinguish predicted accounting targets from stock-return prediction.
- Formation-universe filtering must preserve full historical windows while recomputing cross-sectional transforms on the filtered formation universe.
- Context transforms and exposures must preserve point-in-time availability and remain explicit research assumptions.

### Task 1: Add English canonical pages and contract coverage

**Files:**
- Create: `docs/alpha/concepts/contextual-factors.en-US.md`
- Create: `docs/alpha/concepts/fundamental-state-forecasting.en-US.md`
- Create: `docs/alpha/concepts/style-factor-cross-sections.en-US.md`
- Modify: `docs/alpha/concepts/contextual-factors.md`
- Modify: `docs/alpha/concepts/fundamental-state-forecasting.md`
- Modify: `docs/alpha/concepts/style-factor-cross-sections.md`
- Modify: `tests/alpha/test_documentation_entrypoints.py`

- [x] Add a focused contract test asserting each English page exists, declares `Language: English`, links to its Chinese page, is registered in locale navigation, and preserves its key public API names.
- [x] Run the focused test and confirm it fails because the English pages and locale registrations are absent.
- [x] Write concise English canonicals from the Chinese sources, verifying every claim against `packages/alpha/src/alpha_research/` and the relevant tests.
- [x] Add reciprocal language links to the Chinese pages.
- [x] Run the focused contract test and confirm it passes.

### Task 2: Integrate locale navigation and reader entry points

**Files:**
- Modify: `mkdocs.yml`
- Modify: `docs/hooks/locale_navigation.py`
- Modify: `docs/alpha/README.md`
- Modify: `docs/alpha/README.zh-CN.md`
- Modify: `docs/LANGUAGE_MIGRATION_STATUS.md`

- [x] Add the English pages under the matching English navigation section and register them in `ENGLISH_PAGES`.
- [x] Replace the Alpha index statement that these topics are Chinese-only with links to the English canonicals and Chinese companions.
- [x] Update localization status to remove these three pages from the active translation queue.
- [x] Run locale-navigation tests and a strict MkDocs build; confirm both locale sidebars contain only their selected pages.

### Task 3: Validate and commit

**Files:** all files listed above.

- [x] Run `uv sync --locked --all-groups`.
- [x] Run `uv run ruff check .`.
- [x] Run `uv run pytest`.
- [x] Run `uv run --only-group docs mkdocs build --strict` and `uv run --only-group docs python project_tools/check_locale_navigation.py`.
- [x] Review the rendered English pages and diff for factual parity, broken links, and accidental Chinese prose.
- [ ] Commit the verified batch.
