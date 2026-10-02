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
    "guides/point-in-time-data.md",
    "guides/sequenced-execution.md",
    "concepts/backtest-configuration.md",
    "concepts/backtest-spec.md",
    "concepts/canonical-backtest-bundle.en.md",
    "concepts/execution-costs.md",
    "concepts/cost-breakdown.md",
    "concepts/lean-differential-spike-2026-09.md",
    "alpha/concepts/style-replica.en.md",
    "orchestration/README.md",
    "orchestration/control-plane.md",
    "orchestration/evaluation.md",
    "orchestration/reference/README.md",
    "orchestration/reference/cli-helpers.md",
    "orchestration/reference/configuration.md",
    "reference/public-api.md",
    "reference/allocation-reference.md",
    "data/README.md",
    "reference/outputs/positions.md",
    "testing.md",
}

CHINESE_TITLES = {
    "Guides (Chinese originals; translation in progress)": "指南（中文原文）",
    "Core concepts": "核心概念",
    "Alpha and research (Chinese originals; translation in progress)": "Alpha 与研究（中文原文）",
    "Execution and microstructure (Chinese originals; translation in progress)": (
        "执行与微观结构（中文原文）"
    ),
    "Orchestration": "编排",
    "Chinese originals (translation in progress)": "中文原文",
    "References": "参考资料",
    "Development": "开发",
    "Governance and migration (Chinese originals; translation in progress)": (
        "治理与迁移（中文原文）"
    ),
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
                selected.append(section)
        elif item.is_link:
            selected.append(item)
    return selected


def on_page_context(context, page, config, nav):
    chinese = page.file.src_uri not in ENGLISH_PAGES
    items = _for_locale(nav.items, chinese)
    # The two language headings add no information once the other language is hidden.
    flattened = []
    for item in items:
        if item.is_section and item.title in {"English", "简体中文"}:
            flattened.extend(item.children)
        else:
            flattened.append(item)
    pages = [p for p in nav.pages if (p.file.src_uri not in ENGLISH_PAGES) == chinese]
    context["nav"] = Navigation(flattened, pages)
    return context
