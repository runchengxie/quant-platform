"""Keep each MkDocs sidebar in the language of the current page.

This is a navigation-only transition. Existing page URLs and the search index
remain unchanged while Chinese originals are translated selectively.
"""

from __future__ import annotations

from copy import copy

from mkdocs.structure.nav import Navigation

ENGLISH_PAGES = {
    "README.md",
    "LANGUAGE_MIGRATION_STATUS.md",
    "LANGUAGE_POLICY.md",
    "concepts/platform-overview.md",
    "getting-started/installation.md",
    "getting-started/first-backtest.md",
    "getting-started/understanding-results.md",
    "reference/glossary.md",
    "guides/entry-points.md",
    "guides/execution-simulation.en.md",
    "guides/point-in-time-data.en.md",
    "guides/sequenced-execution.en.md",
    "guides/incumbent-requalification.en.md",
    "guides/incumbent-requalification-oos-controls.en.md",
    "guides/promotion-sidecar.en.md",
    "guides/sleeve-portfolio.en.md",
    "guides/diagnostic-close-replay.en.md",
    "reference/outputs/backtest-outputs.en.md",
    "concepts/backtest-configuration.md",
    "concepts/backtest-spec.md",
    "concepts/canonical-backtest-bundle.en.md",
    "concepts/backtest-interpretation.en.md",
    "concepts/execution-costs.md",
    "concepts/cost-breakdown.md",
    "concepts/differential-backtesting.en.md",
    "concepts/portfolio-optimization-backends.en.md",
    "concepts/backend-architecture.en.md",
    "concepts/turnover.en-US.md",
    "concepts/benchmark-ladder.en-US.md",
    "concepts/lean-differential-spike-2026-09.md",
    "concepts/factor-attribution.en.md",
    "corporate-action-ledger.en.md",
    "dated-execution-fees.md",
    "concepts/style-factor-portfolio-weighting.en.md",
    "reference/usd-price-ledger.md",
    "alpha/concepts/style-replica.en.md",
    "alpha/concepts/model-selection.en-US.md",
    "alpha/concepts/model-landscape.en-US.md",
    "alpha/concepts/factor-catalog.en-US.md",
    "alpha/concepts/factor-risk-model.en-US.md",
    "alpha/concepts/signal-drift.en-US.md",
    "alpha/concepts/factor-expression.en-US.md",
    "orchestration/README.md",
    "orchestration/control-plane.md",
    "orchestration/evaluation.md",
    "orchestration/output-artifacts.en.md",
    "orchestration/operations/quality-gates.en.md",
    "orchestration/integrating-an-owner.en.md",
    "orchestration/targets.en.md",
    "orchestration/output-orchestration.en.md",
    "orchestration/output-summary.en.md",
    "orchestration/evidence-protocol-cli.en.md",
    "orchestration/reference/README.md",
    "orchestration/reference/cli-helpers.md",
    "orchestration/reference/configuration.md",
    "orchestration/reference/runtime-helpers.en.md",
    "reference/public-api.md",
    "reference/allocation-reference.md",
    "data/README.md",
    "reference/outputs/positions.md",
    "testing.md",
}

CHINESE_TITLES = {
    "Guides (Chinese originals; translation in progress)": "指南",
    "Core concepts": "核心概念",
    "Alpha and research (Chinese originals; translation in progress)": "Alpha 与研究",
    "Execution and microstructure (Chinese originals; translation in progress)": (
        "执行与微观结构"
    ),
    "Orchestration": "编排",
    "Chinese originals (translation in progress)": "中文原文",
    "References": "参考资料",
    "Development": "开发",
    "Governance and migration (Chinese originals; translation in progress)": (
        "治理与迁移"
    ),
}

ENGLISH_TITLES = {
    "其他风险与研究主题": "Additional research topics",
    "Governance and migration (Chinese originals; translation in progress)": (
        "Governance and migration"
    ),
}

LOCALE_SECTION_TITLES = {
    "English",
    "简体中文",
    "Chinese originals (translation in progress)",
    "中文原文",
}


def _for_locale(items, chinese):
    selected = []
    for item in items:
        if item.is_page:
            src = item.file.src_uri
            if (src not in ENGLISH_PAGES) == chinese:
                selected.append(item)
        elif item.is_section:
            children = _for_locale(item.children, chinese)
            if children:
                section = copy(item)
                section.children = children
                if chinese:
                    section.title = CHINESE_TITLES.get(section.title, section.title)
                else:
                    section.title = ENGLISH_TITLES.get(section.title, section.title)
                if section.title in LOCALE_SECTION_TITLES:
                    selected.extend(section.children)
                else:
                    selected.append(section)
        elif item.is_link:
            selected.append(item)
    return selected


def on_page_context(context, page, config, nav):
    chinese = page.file.src_uri not in ENGLISH_PAGES
    items = _for_locale(nav.items, chinese)
    pages = [p for p in nav.pages if (p.file.src_uri not in ENGLISH_PAGES) == chinese]
    context["nav"] = Navigation(items, pages)
    return context
