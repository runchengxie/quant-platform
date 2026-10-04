from __future__ import annotations

import re
import subprocess
import sys
from html.parser import HTMLParser
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
    ("corporate-action-ledger.en.md", "corporate-action-ledger.md"),
    ("concepts/factor-attribution.en.md", "concepts/factor-attribution.md"),
    ("orchestration/README.md", "orchestration/README.zh-CN.md"),
    ("orchestration/control-plane.md", "orchestration/control-plane.zh-CN.md"),
    ("orchestration/evaluation.md", "orchestration/evaluation.zh-CN.md"),
    ("orchestration/output-artifacts.en.md", "orchestration/output-artifacts.md"),
    ("orchestration/integrating-an-owner.en.md", "orchestration/integrating-an-owner.md"),
    ("orchestration/targets.en.md", "orchestration/targets.md"),
    ("orchestration/output-orchestration.en.md", "orchestration/output-orchestration.md"),
    ("orchestration/output-summary.en.md", "orchestration/output-summary.md"),
    ("orchestration/evidence-protocol-cli.en.md", "orchestration/evidence-protocol-cli.md"),
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
    ("dated-execution-fees.md", "dated-execution-fees.zh-CN.md"),
    (
        "concepts/style-factor-portfolio-weighting.en.md",
        "concepts/style-factor-portfolio-weighting.md",
    ),
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


def test_english_documentation_index_links_to_english_guides() -> None:
    root = Path(__file__).resolve().parents[1]
    index = (root / "docs" / "README.md").read_text(encoding="utf-8")

    assert "guides/execution-simulation.en.md" in index
    assert "reference/outputs/backtest-outputs.en.md" in index
    assert "guides/execution-simulation.md" not in index
    assert "microstructure/README.md" not in index
    assert "governance/accounting-execution-roadmap.md" not in index


def test_factor_attribution_docs_keep_schema_ids_and_scope_aligned() -> None:
    root = Path(__file__).resolve().parents[1]
    english = (root / "docs/concepts/factor-attribution.en.md").read_text(encoding="utf-8")
    chinese = (root / "docs/concepts/factor-attribution.md").read_text(encoding="utf-8")
    source = (
        root / "packages/portfolio-backtester/src/portfolio_backtester/factor_attribution.py"
    ).read_text(encoding="utf-8")

    for schema in ("factor_return_attribution.v1", "factor_risk_attribution.v1"):
        assert schema in source
        assert schema in english
        assert schema in chinese
    for helper in ("attribute_factor_return()", "attribute_factor_risk()"):
        assert helper in english
        assert helper in chinese
    assert "positive semidefinite" in english
    assert "半正定" in chinese
    assert "They do not estimate those inputs." in english
    assert "不负责估计这些输入" in chinese
    assert "do not calculate Brinson allocation or selection effects" in english
    assert "不计算 Brinson 配置或选股归因" in chinese


def test_dated_execution_fee_translation_matches_public_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    english = (root / "docs/dated-execution-fees.md").read_text(encoding="utf-8")
    chinese = (root / "docs/dated-execution-fees.zh-CN.md").read_text(encoding="utf-8")
    implementation = (
        root / "packages/portfolio-backtester/src/portfolio_backtester/dated_fees.py"
    ).read_text(encoding="utf-8")

    for contract in (
        "DatedFeeSchedule",
        "DatedTradeFeeModel",
        "FeeQuoteContext",
        "FeeSchedulePeriod",
        "cumulative_group_notional",
        "fee_group_id",
        "simulate_execution_adjusted_nav",
    ):
        assert contract in english
        assert contract in chinese
    for limitation in ("no built-in market tariff", "fails closed", "not a claim"):
        assert limitation in english
    for limitation in ("不内置市场费率", "不会回退", "不代表完整模拟"):
        assert limitation in chinese
    assert "class DatedTradeFeeModel" in implementation
    assert "class DatedFeeSchedule" in implementation


def test_retired_style_factor_slice_is_not_described_as_a_current_api() -> None:
    root = Path(__file__).resolve().parents[1]
    english_notice = (root / "docs/concepts/style-factor-portfolio-weighting.en.md").read_text(
        encoding="utf-8"
    )
    chinese_notice = (root / "docs/concepts/style-factor-portfolio-weighting.md").read_text(
        encoding="utf-8"
    )
    english_api = (root / "docs/reference/public-api.md").read_text(encoding="utf-8")
    chinese_api = (root / "docs/reference/public-api.zh-CN.md").read_text(encoding="utf-8")
    package = (
        root / "packages/portfolio-backtester/src/portfolio_backtester/__init__.py"
    ).read_text(encoding="utf-8")

    for retired in (
        "available_factor_names",
        "get_rebalance_dates",
        "build_factor_returns",
        "build_quantile_portfolio_returns",
        "compute_factor_correlations",
        "compute_summary",
        "compute_yearly_breakdown",
    ):
        assert retired not in english_api
        assert retired not in chinese_api
        assert f'"{retired}"' not in package
    for notice, phrase in (
        (english_notice, "not supported by the current"),
        (english_notice, "license and historical authorization"),
        (chinese_notice, "不能视为当前受支持的"),
        (chinese_notice, "许可证和历史授权尚未确认"),
    ):
        assert phrase in notice
    assert "62d4a254409cd3111fc90083a892308fa598c98c" in english_notice
    assert "62d4a254409cd3111fc90083a892308fa598c98c" in chinese_notice


class _PrimaryNavigationText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._nav_states: list[bool | None] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "nav":
            return
        classes = dict(attrs).get("class") or ""
        class_names = classes.split()
        if not self._nav_states:
            self._nav_states.append("md-nav--primary" in class_names)
        else:
            parent_is_primary = all(state is True for state in self._nav_states)
            include = parent_is_primary and "md-nav--secondary" not in class_names
            self._nav_states.append(include)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self._nav_states:
            self._nav_states.pop()

    def handle_data(self, data: str) -> None:
        if self._nav_states and self._nav_states[-1] is True:
            self.text.append(data.strip())


def test_rendered_sidebar_matches_the_current_page_locale(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    site_dir = tmp_path / "site"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str(site_dir),
        ],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    rendered_pages = {
        "English": site_dir / "concepts/backtest-configuration/index.html",
        "Chinese": site_dir / "concepts/backtest-configuration.zh-CN/index.html",
        "Chinese dated fees": site_dir / "dated-execution-fees.zh-CN/index.html",
        "English retired notice": site_dir
        / "concepts/style-factor-portfolio-weighting.en/index.html",
        "Chinese retired notice": site_dir / "concepts/style-factor-portfolio-weighting/index.html",
    }
    navigation: dict[str, str] = {}
    for locale, path in rendered_pages.items():
        parser = _PrimaryNavigationText()
        parser.feed(path.read_text(encoding="utf-8"))
        navigation[locale] = " ".join(parser.text)

    assert "Installation and environments" in navigation["English"]
    assert "安装与环境" not in navigation["English"]
    assert "Dated execution fees" in navigation["English"]
    assert "USD price ledger" in navigation["English"]
    assert not re.search(r"[\u3400-\u9fff]", navigation["English"])
    assert "安装与环境" in navigation["Chinese"]
    assert "Installation and environments" not in navigation["Chinese"]
    assert "Dated execution fees" not in navigation["Chinese"]
    assert "分期执行费率" in navigation["Chinese dated fees"]
    assert "USD price ledger" not in navigation["Chinese"]
    assert "Style Replica（中文参考）" in navigation["Chinese"]
    assert "Style Replica (Chinese reference)" not in navigation["Chinese"]
    assert "Retired style-factor backtest slice" in navigation["English retired notice"]
    assert not re.search(r"[\u3400-\u9fff]", navigation["English retired notice"])
    assert "已退出公开发布的风格因子回测片段" in navigation["Chinese retired notice"]
    assert "Retired style-factor backtest slice" not in navigation["Chinese retired notice"]
