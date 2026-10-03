from __future__ import annotations

from pathlib import Path

PAIRS = (
    ("../README.md", "../README.zh-CN.md"),
    ("README.md", "README.zh-CN.md"),
    ("LANGUAGE_POLICY.md", "LANGUAGE_POLICY.zh-CN.md"),
    ("concepts/platform-overview.md", "concepts/platform-overview.zh-CN.md"),
    ("getting-started/installation.md", "getting-started/installation.zh-CN.md"),
    ("getting-started/first-backtest.md", "getting-started/first-backtest.zh-CN.md"),
    ("getting-started/understanding-results.md", "getting-started/understanding-results.zh-CN.md"),
    ("reference/glossary.md", "reference/glossary.zh-CN.md"),
    ("guides/entry-points.md", "guides/entry-points.zh-CN.md"),
    ("guides/point-in-time-data.en.md", "guides/point-in-time-data.md"),
    ("guides/sequenced-execution.en.md", "guides/sequenced-execution.md"),
    ("guides/incumbent-requalification.en.md", "guides/incumbent-requalification.md"),
    (
        "guides/incumbent-requalification-oos-controls.en.md",
        "guides/incumbent-requalification-oos-controls.md",
    ),
    ("guides/promotion-sidecar.en.md", "guides/promotion-sidecar.md"),
    ("guides/sleeve-portfolio.en.md", "guides/sleeve-portfolio.md"),
    ("guides/diagnostic-close-replay.en.md", "guides/diagnostic-close-replay.md"),
    ("reference/public-api.md", "reference/public-api.zh-CN.md"),
    ("reference/allocation-reference.md", "reference/allocation-reference.zh-CN.md"),
    ("concepts/backtest-configuration.md", "concepts/backtest-configuration.zh-CN.md"),
    ("concepts/backtest-spec.md", "concepts/backtest-spec.zh-CN.md"),
    (
        "concepts/differential-backtesting.en.md",
        "concepts/differential-backtesting.md",
    ),
    (
        "concepts/portfolio-optimization-backends.en.md",
        "concepts/portfolio-optimization-backends.md",
    ),
    ("concepts/backend-architecture.en.md", "concepts/backend-architecture.md"),
    ("orchestration/README.md", "orchestration/README.zh-CN.md"),
    ("orchestration/control-plane.md", "orchestration/control-plane.zh-CN.md"),
    ("orchestration/evaluation.md", "orchestration/evaluation.zh-CN.md"),
    ("orchestration/output-artifacts.en.md", "orchestration/output-artifacts.md"),
    ("orchestration/integrating-an-owner.en.md", "orchestration/integrating-an-owner.md"),
    ("orchestration/targets.en.md", "orchestration/targets.md"),
    ("orchestration/output-orchestration.en.md", "orchestration/output-orchestration.md"),
    ("orchestration/output-summary.en.md", "orchestration/output-summary.md"),
    (
        "orchestration/operations/quality-gates.en.md",
        "orchestration/operations/quality-gates.md",
    ),
    ("orchestration/reference/README.md", "orchestration/reference/README.zh-CN.md"),
    (
        "orchestration/reference/runtime-helpers.en.md",
        "orchestration/reference/runtime-helpers.md",
    ),
    ("data/README.md", "data/README.zh-CN.md"),
    ("concepts/execution-costs.md", "concepts/execution-costs.zh-CN.md"),
    ("concepts/cost-breakdown.md", "concepts/cost-breakdown.zh-CN.md"),
    ("reference/outputs/positions.md", "reference/outputs/positions.zh-CN.md"),
    (
        "reference/outputs/backtest-outputs.en.md",
        "reference/outputs/backtest-outputs.md",
    ),
    ("testing.md", "testing.zh-CN.md"),
    ("alpha/concepts/model-selection.en-US.md", "alpha/concepts/model-selection.md"),
    ("alpha/concepts/model-landscape.en-US.md", "alpha/concepts/model-landscape.md"),
    ("alpha/concepts/factor-catalog.en-US.md", "alpha/concepts/factor-catalog.md"),
    ("alpha/concepts/factor-risk-model.en-US.md", "alpha/concepts/factor-risk-model.md"),
    ("alpha/concepts/signal-drift.en-US.md", "alpha/concepts/signal-drift.md"),
    ("alpha/concepts/factor-expression.en-US.md", "alpha/concepts/factor-expression.md"),
    (
        "orchestration/reference/configuration.md",
        "orchestration/reference/configuration.zh-CN.md",
    ),
    (
        "orchestration/reference/cli-helpers.md",
        "orchestration/reference/cli-helpers.zh-CN.md",
    ),
)


def test_english_is_the_default_and_locale_pages_have_distinct_routes() -> None:
    root = Path(__file__).resolve().parents[1]
    config = (root / "mkdocs.yml").read_text(encoding="utf-8")
    assert "  language: en" in config
    assert "  - English:" in config
    assert "  - 简体中文:" in config

    for english_path, chinese_path in PAIRS:
        english = (root / "docs" / english_path).resolve()
        chinese = (root / "docs" / chinese_path).resolve()
        assert english.is_file(), english_path
        assert chinese.is_file(), chinese_path
        english_text = english.read_text(encoding="utf-8")
        chinese_text = chinese.read_text(encoding="utf-8")
        assert chinese_path.split("/")[-1] in english_text
        assert english_path.split("/")[-1] in chinese_text
        if "docs" in english.parts:
            assert "Language: English" in english_text
            assert "语言：简体中文" in chinese_text


def test_locale_migration_status_is_linked_from_documentation_home() -> None:
    root = Path(__file__).resolve().parents[1]
    status = root / "docs" / "LANGUAGE_MIGRATION_STATUS.md"
    index = (root / "docs" / "README.md").read_text(encoding="utf-8")
    assert status.is_file()
    assert "LANGUAGE_MIGRATION_STATUS.md" in index
