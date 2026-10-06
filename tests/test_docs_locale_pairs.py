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
    (
        "concepts/afml-sizing-and-risk.en.md",
        "concepts/afml-sizing-and-risk.md",
    ),
    ("orchestration/README.md", "orchestration/README.zh-CN.md"),
    (
        "orchestration/e2-promotion-receipt.en.md",
        "orchestration/e2-promotion-receipt.md",
    ),
    (
        "orchestration/cashflow-publication.en.md",
        "orchestration/cashflow-publication.md",
    ),
    (
        "orchestration/publication-audit.en.md",
        "orchestration/publication-audit.md",
    ),
    (
        "orchestration/operations/README.en.md",
        "orchestration/operations/README.md",
    ),
    ("orchestration/development.en.md", "orchestration/development.md"),
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
    ("execution/README.en.md", "execution/README.md"),
    ("microstructure/README.en.md", "microstructure/README.md"),
    ("microstructure/data-boundary.en.md", "microstructure/data-boundary.md"),
    ("microstructure/development-guide.en.md", "microstructure/development-guide.md"),
    ("development/microstructure-rust.en.md", "development/microstructure-rust.md"),
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
    ("namespace-migration.en.md", "namespace-migration.md"),
    ("ownership-migration.en.md", "ownership-migration.md"),
    ("grid-support.en.md", "grid-support.md"),
    (
        "governance/accounting-execution-roadmap.en.md",
        "governance/accounting-execution-roadmap.md",
    ),
    (
        "migration/research-workspace-sunset.en.md",
        "migration/research-workspace-sunset.md",
    ),
    (
        "migration/market-research-boundary.en.md",
        "migration/market-research-boundary.md",
    ),
    ("alpha/concepts/model-selection.en-US.md", "alpha/concepts/model-selection.md"),
    ("alpha/concepts/matched-model-risk.en-US.md", "alpha/concepts/matched-model-risk.md"),
    ("alpha/concepts/afml-methodology.en-US.md", "alpha/concepts/afml-methodology.md"),
    (
        "alpha/concepts/framework-backends.en-US.md",
        "alpha/concepts/framework-backends.md",
    ),
    (
        "alpha/guides/research-template-design.en-US.md",
        "alpha/guides/research-template-design.md",
    ),
    ("alpha/namespace-migration.en-US.md", "alpha/namespace-migration.md"),
    ("alpha/operations/testing.en-US.md", "alpha/operations/testing.md"),
    ("alpha/README.md", "alpha/README.zh-CN.md"),
    ("alpha/concepts/model-landscape.en-US.md", "alpha/concepts/model-landscape.md"),
    ("alpha/concepts/factor-catalog.en-US.md", "alpha/concepts/factor-catalog.md"),
    ("alpha/concepts/factor-risk-model.en-US.md", "alpha/concepts/factor-risk-model.md"),
    ("alpha/concepts/signal-drift.en-US.md", "alpha/concepts/signal-drift.md"),
    ("alpha/concepts/factor-expression.en-US.md", "alpha/concepts/factor-expression.md"),
    (
        "alpha/concepts/feature-research-protocol.en-US.md",
        "alpha/concepts/feature-research-protocol.md",
    ),
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


def test_english_language_markers_are_registered_for_locale_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    docs_dir = root / "docs"
    hook = (docs_dir / "hooks" / "locale_navigation.py").read_text(encoding="utf-8")
    registered = set(re.findall(r'^\s+"([^\"]+\.md)",$', hook, re.MULTILINE))
    marked = {
        path.relative_to(docs_dir).as_posix()
        for path in docs_dir.rglob("*.md")
        if "superpowers/plans" not in path.as_posix()
        if "Language: English" in path.read_text(encoding="utf-8")
    }
    assert marked <= registered, sorted(marked - registered)


def test_namespace_and_ownership_docs_match_current_package_boundaries() -> None:
    root = Path(__file__).resolve().parents[1]
    namespace_english = (root / "docs/namespace-migration.en.md").read_text(encoding="utf-8")
    namespace_chinese = (root / "docs/namespace-migration.md").read_text(encoding="utf-8")
    ownership_english = (root / "docs/ownership-migration.en.md").read_text(encoding="utf-8")
    ownership_chinese = (root / "docs/ownership-migration.md").read_text(encoding="utf-8")
    distribution = (root / "pyproject.toml").read_text(encoding="utf-8")
    owner_module = (
        root / "packages/portfolio-backtester/src/portfolio_backtester/daily_watch20_oos.py"
    )
    owner_test = (root / "tests/test_daily_watch20_oos_owner.py").read_text(encoding="utf-8")

    assert '"portfolio_backtester"' in distribution
    assert '"alpha_research"' in distribution
    assert "只安装 `portfolio_backtester`" not in namespace_chinese
    assert "portfolio_backtester.*" in namespace_english + namespace_chinese
    assert "workspace 2.0" in namespace_english + namespace_chinese
    assert "portfolio_backtester.daily_watch20_oos" in ownership_english + ownership_chinese
    assert owner_module.is_file()
    assert "portfolio_daily_rows" in owner_test


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
    assert "grid-support.en.md" in index
    assert "reference/outputs/backtest-outputs.en.md" in index
    assert "guides/execution-simulation.md" not in index
    assert "microstructure/README.md" not in index
    assert "governance/accounting-execution-roadmap.md" not in index
    for page in (
        "governance/accounting-execution-roadmap.en.md",
        "migration/research-workspace-sunset.en.md",
        "migration/market-research-boundary.en.md",
    ):
        assert page in index


def test_governance_docs_match_current_implementation_and_ownership() -> None:
    root = Path(__file__).resolve().parents[1]
    docs = root / "docs"
    roadmap = (docs / "governance/accounting-execution-roadmap.en.md").read_text(
        encoding="utf-8"
    )
    _assert_roadmap_backend_contract(root, roadmap)
    _assert_roadmap_cost_contract(root, roadmap)
    _assert_roadmap_market_rule_contract(root, roadmap)
    _assert_roadmap_capacity_and_metadata_contract(root, roadmap)
    _assert_migration_boundary_matches_distribution(root, docs)


def _assert_roadmap_backend_contract(root: Path, roadmap: str) -> None:
    source_root = root / "packages/portfolio-backtester/src/portfolio_backtester"
    native = (source_root / "backends/native.py").read_text(encoding="utf-8")
    api = (source_root / "api.py").read_text(encoding="utf-8")
    ledger = (source_root / "execution_sim/results.py").read_text(encoding="utf-8")
    lifecycle = (source_root / "execution_contracts.py").read_text(encoding="utf-8")

    assert "ledger: bool = False" in native
    assert "ledger: bool = False" in api
    for state in (
        "created",
        "submitted",
        "accepted",
        "partial",
        "filled",
        "cancelled",
        "expired",
        "rejected",
    ):
        assert f'"{state}"' in lifecycle
        assert f"`{state}`" in roadmap
    for field in (
        "targets",
        "orders",
        "fills",
        "daily_positions",
        "daily_cash",
        "daily_nav",
        "cost_breakdown",
        "turnover_breakdown",
    ):
        assert field in ledger
        assert f"`{field}`" in roadmap


def _assert_roadmap_cost_contract(root: Path, roadmap: str) -> None:
    source_root = root / "packages/portfolio-backtester/src/portfolio_backtester"
    costs = (source_root / "types.py").read_text(encoding="utf-8")
    fees = (source_root / "_execution_models.py").read_text(encoding="utf-8")
    for component in (
        "commission",
        "stamp_tax",
        "transfer_fee",
        "spread_cost",
        "temporary_impact",
        "permanent_impact",
        "opportunity_cost",
        "financing_cost",
    ):
        assert component in costs
        assert component in roadmap
    assert "notional_cost_breakdown" in fees


def _assert_roadmap_market_rule_contract(root: Path, roadmap: str) -> None:
    market_rules = (
        root / "packages/portfolio-backtester/src/portfolio_backtester/execution_sim/config.py"
    ).read_text(encoding="utf-8")
    for rule in (
        "round_lot",
        "enforce_t1",
        "enforce_price_limits",
        "enforce_listing_status",
        "limit_up_col",
        "limit_down_col",
        "listing_status_col",
    ):
        assert rule in market_rules
        assert f"`{rule}`" in roadmap
    for timestamp in (
        "signal_time",
        "decision_time",
        "order_time",
        "fill_time",
        "valuation_time",
    ):
        assert timestamp in roadmap


def _assert_roadmap_capacity_and_metadata_contract(root: Path, roadmap: str) -> None:
    source_root = root / "packages/portfolio-backtester/src/portfolio_backtester"
    capacity_report = (source_root / "_capacity_report_config.py").read_text(encoding="utf-8")
    run_metadata = (source_root / "_run_metadata.py").read_text(encoding="utf-8")
    metrics = (source_root / "_metrics_period.py").read_text(encoding="utf-8")
    for key in (
        "break_even_capacity",
        "fill_rate_95_capacity",
        "alpha_retention_90_capacity",
        "sharpe_retention_90_capacity",
        "marginal_return_per_unit_capital",
        "marginal_sharpe_retention_per_unit_capital",
        "by_symbol",
        "by_liquidity",
        "by_industry",
    ):
        assert key in capacity_report or key in (
            source_root / "_capacity_concentration.py"
        ).read_text(encoding="utf-8")
        assert f"`{key}`" in roadmap
    for key in (
        "repo_commit",
        "config_hash",
        "input_data_hash",
        "universe_fingerprint",
        "calendar_window",
        "fee_schedule_version",
        "slippage_calibration_version",
        "dependency_versions",
        "random_seed",
        "run_timestamp",
    ):
        assert key in run_metadata
        assert f"`{key}`" in roadmap
    assert "yearly_compounded_returns" in metrics

    tested_contracts = (
        "tests/test_ledger_stage2_contract.py",
        "tests/test_cost_breakdown.py",
        "tests/test_execution_sim_market_rules.py",
        "tests/test_capacity_report_phase5.py",
        "tests/test_run_metadata_phase6.py",
    )
    for test_path in tested_contracts:
        assert (root / test_path).is_file()
        assert f"{test_path}" in roadmap


def _assert_migration_boundary_matches_distribution(root: Path, docs: Path) -> None:
    for filename in (
        "migration/research-workspace-sunset.en.md",
        "migration/market-research-boundary.en.md",
    ):
        assert (docs / filename).is_file()
    boundary = (docs / "migration/research-workspace-sunset.en.md").read_text(
        encoding="utf-8"
    )
    assert "market_data_platform`" in boundary
    assert "quant-market-data-platform" in boundary
    distribution = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "market_data_platform" not in distribution


def test_microstructure_guides_link_to_the_rust_page_in_the_same_locale() -> None:
    root = Path(__file__).resolve().parents[1]
    english_pages = (
        root / "docs/microstructure/README.en.md",
        root / "docs/microstructure/development-guide.en.md",
    )
    chinese_pages = (
        root / "docs/microstructure/README.md",
        root / "docs/microstructure/development-guide.md",
    )

    for page in english_pages:
        assert "../development/microstructure-rust.en.md" in page.read_text(encoding="utf-8")
    for page in chinese_pages:
        assert "../development/microstructure-rust.md" in page.read_text(encoding="utf-8")


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

    navigation, html_languages = _read_rendered_locale_pages(site_dir)
    _assert_home_and_core_navigation(navigation)
    _assert_retired_notice_navigation(navigation)
    _assert_execution_navigation(navigation)
    _assert_alpha_navigation(navigation)
    _assert_grid_support_navigation(navigation)
    _assert_migration_navigation(navigation)
    _assert_governance_navigation(navigation)
    _assert_rendered_html_languages(html_languages)


def _read_rendered_locale_pages(site_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    rendered_pages = {
        "English home": site_dir / "index.html",
        "Chinese home": site_dir / "README.zh-CN/index.html",
        "English orchestration": site_dir / "orchestration/index.html",
        "Chinese orchestration": site_dir / "orchestration/README.zh-CN/index.html",
        "English": site_dir / "concepts/backtest-configuration/index.html",
        "Chinese": site_dir / "concepts/backtest-configuration.zh-CN/index.html",
        "English portfolio sizing": site_dir / "concepts/afml-sizing-and-risk.en/index.html",
        "Chinese portfolio sizing": site_dir / "concepts/afml-sizing-and-risk/index.html",
        "English overfitting controls": site_dir
        / "alpha/concepts/overfitting-controls.en-US/index.html",
        "Chinese overfitting controls": site_dir / "alpha/concepts/overfitting-controls/index.html",
        "English research protocols": site_dir
        / "alpha/concepts/research-protocols.en-US/index.html",
        "Chinese research protocols": site_dir / "alpha/concepts/research-protocols/index.html",
        "English feature research": site_dir
        / "alpha/concepts/feature-research-protocol.en-US/index.html",
        "English matched model risk": site_dir
        / "alpha/concepts/matched-model-risk.en-US/index.html",
        "Chinese matched model risk": site_dir / "alpha/concepts/matched-model-risk/index.html",
        "English alpha overview": site_dir / "alpha/index.html",
        "Chinese feature research": site_dir
        / "alpha/concepts/feature-research-protocol/index.html",
        "Chinese alpha overview": site_dir / "alpha/README.zh-CN/index.html",
        "English grid support": site_dir / "grid-support.en/index.html",
        "Chinese grid support": site_dir / "grid-support/index.html",
        "English namespace migration": site_dir / "namespace-migration.en/index.html",
        "Chinese namespace migration": site_dir / "namespace-migration/index.html",
        "English ownership migration": site_dir / "ownership-migration.en/index.html",
        "Chinese ownership migration": site_dir / "ownership-migration/index.html",
        "English accounting roadmap": site_dir
        / "governance/accounting-execution-roadmap.en/index.html",
        "Chinese accounting roadmap": site_dir
        / "governance/accounting-execution-roadmap/index.html",
        "English workspace boundary": site_dir
        / "migration/research-workspace-sunset.en/index.html",
        "Chinese workspace boundary": site_dir / "migration/research-workspace-sunset/index.html",
        "English market research boundary": site_dir
        / "migration/market-research-boundary.en/index.html",
        "Chinese market research boundary": site_dir
        / "migration/market-research-boundary/index.html",
        "Chinese dated fees": site_dir / "dated-execution-fees.zh-CN/index.html",
        "English retired notice": site_dir
        / "concepts/style-factor-portfolio-weighting.en/index.html",
        "Chinese retired notice": site_dir / "concepts/style-factor-portfolio-weighting/index.html",
        "English execution": site_dir / "execution/README.en/index.html",
        "Chinese execution": site_dir / "execution/index.html",
        "English microstructure": site_dir / "microstructure/README.en/index.html",
        "Chinese microstructure": site_dir / "microstructure/index.html",
        "English data boundary": site_dir / "microstructure/data-boundary.en/index.html",
        "Chinese data boundary": site_dir / "microstructure/data-boundary/index.html",
        "English microstructure development": site_dir
        / "microstructure/development-guide.en/index.html",
        "Chinese microstructure development": site_dir
        / "microstructure/development-guide/index.html",
        "English Rust kernel": site_dir / "development/microstructure-rust.en/index.html",
        "Chinese Rust kernel": site_dir / "development/microstructure-rust/index.html",
    }
    navigation: dict[str, str] = {}
    html_languages: dict[str, str] = {}
    for locale, path in rendered_pages.items():
        rendered = path.read_text(encoding="utf-8")
        parser = _PrimaryNavigationText()
        parser.feed(rendered)
        navigation[locale] = " ".join(parser.text)
        match = re.search(r'<html lang="([^"]+)"', rendered)
        assert match is not None, locale
        html_languages[locale] = match.group(1)
    return navigation, html_languages


def _assert_home_and_core_navigation(navigation: dict[str, str]) -> None:
    assert "Installation and environments" in navigation["English"]
    assert "安装与环境" not in navigation["English"]
    assert "Dated execution fees" in navigation["English"]
    assert "USD price ledger" in navigation["English"]
    assert not re.search(r"[\u3400-\u9fff]", navigation["English"])
    for locale in ("English home", "English orchestration", "English"):
        assert not re.search(r"[\u3400-\u9fff]", navigation[locale])
        assert "Chinese originals" not in navigation[locale]
        assert "\n English \n" not in navigation[locale]
        assert "简体中文" not in navigation[locale]
    for locale in ("Chinese home", "Chinese orchestration", "Chinese"):
        assert "Chinese originals" not in navigation[locale]
        assert "Getting started" not in navigation[locale]
        assert "\n English \n" not in navigation[locale]
    assert "安装与环境" in navigation["Chinese"]
    assert "Installation and environments" not in navigation["Chinese"]
    assert "Dated execution fees" not in navigation["Chinese"]
    assert "分期执行费率" in navigation["Chinese dated fees"]
    assert "USD price ledger" not in navigation["Chinese"]
    assert "Style Replica（中文参考）" in navigation["Chinese"]
    assert "Style Replica (Chinese reference)" not in navigation["Chinese"]


def _assert_rendered_html_languages(html_languages: dict[str, str]) -> None:
    for locale in (
        "English home",
        "English orchestration",
        "English",
        "English portfolio sizing",
        "English overfitting controls",
        "English research protocols",
        "English feature research",
        "English matched model risk",
        "English alpha overview",
        "English grid support",
        "English namespace migration",
        "English ownership migration",
        "English accounting roadmap",
        "English workspace boundary",
        "English market research boundary",
        "English retired notice",
        "English execution",
        "English microstructure",
        "English data boundary",
        "English microstructure development",
        "English Rust kernel",
    ):
        assert html_languages[locale] == "en"
    for locale in (
        "Chinese home",
        "Chinese orchestration",
        "Chinese",
        "Chinese portfolio sizing",
        "Chinese overfitting controls",
        "Chinese research protocols",
        "Chinese feature research",
        "Chinese matched model risk",
        "Chinese alpha overview",
        "Chinese grid support",
        "Chinese namespace migration",
        "Chinese ownership migration",
        "Chinese accounting roadmap",
        "Chinese workspace boundary",
        "Chinese market research boundary",
        "Chinese dated fees",
        "Chinese retired notice",
        "Chinese execution",
        "Chinese microstructure",
        "Chinese data boundary",
        "Chinese microstructure development",
        "Chinese Rust kernel",
    ):
        assert html_languages[locale] == "zh"


def _assert_retired_notice_navigation(navigation: dict[str, str]) -> None:
    assert "Retired style-factor backtest slice" in navigation["English retired notice"]
    assert not re.search(r"[\u3400-\u9fff]", navigation["English retired notice"])
    assert "已退出公开发布的风格因子回测片段" in navigation["Chinese retired notice"]
    assert "Retired style-factor backtest slice" not in navigation["Chinese retired notice"]


def _assert_execution_navigation(navigation: dict[str, str]) -> None:
    for locale in (
        "English execution",
        "English microstructure",
        "English data boundary",
        "English microstructure development",
        "English Rust kernel",
    ):
        assert not re.search(r"[\u3400-\u9fff]", navigation[locale])
        assert "Execution domain" in navigation[locale]
    for locale in (
        "Chinese execution",
        "Chinese microstructure",
        "Chinese data boundary",
        "Chinese microstructure development",
        "Chinese Rust kernel",
    ):
        assert "执行概览" in navigation[locale]
        assert "Execution domain" not in navigation[locale]


def _assert_alpha_navigation(navigation: dict[str, str]) -> None:
    for locale in (
        "English overfitting controls",
        "English research protocols",
        "English feature research",
    ):
        assert not re.search(r"[\u3400-\u9fff]", navigation[locale])
        assert "Getting started" in navigation[locale]
        assert "Research protocols" in navigation[locale]
        assert "简体中文" not in navigation[locale]
    for locale in (
        "Chinese overfitting controls",
        "Chinese research protocols",
        "Chinese feature research",
        "Chinese matched model risk",
    ):
        assert "新人入门" in navigation[locale]
        assert "研究协议" in navigation[locale]
        assert "Getting started" not in navigation[locale]
    assert "Matched model and risk tools" in navigation["English matched model risk"]
    assert not re.search(r"[\u3400-\u9fff]", navigation["English matched model risk"])
    assert "匹配模型风险" in navigation["Chinese matched model risk"]
    assert "Matched model and risk tools" not in navigation["Chinese matched model risk"]


def _assert_grid_support_navigation(navigation: dict[str, str]) -> None:
    english = navigation["English grid support"]
    chinese = navigation["Chinese grid support"]
    assert "Grid support helpers" in english
    assert not re.search(r"[\u3400-\u9fff]", english)
    assert "网格回测辅助函数" in chinese
    assert "Grid support helpers" not in chinese


def _assert_migration_navigation(navigation: dict[str, str]) -> None:
    for locale in ("English namespace migration", "English ownership migration"):
        assert not re.search(r"[\u3400-\u9fff]", navigation[locale])
        assert "Portfolio namespace migration" in navigation[locale]
        assert "DailyWatch20 ownership" in navigation[locale]
        assert "命名空间迁移" not in navigation[locale]
        assert "归属迁移" not in navigation[locale]
    for locale in ("Chinese namespace migration", "Chinese ownership migration"):
        assert "命名空间迁移" in navigation[locale]
        assert "归属迁移" in navigation[locale]
        assert "Portfolio namespace migration" not in navigation[locale]
        assert "DailyWatch20 ownership" not in navigation[locale]


def _assert_governance_navigation(navigation: dict[str, str]) -> None:
    for locale in (
        "English accounting roadmap",
        "English workspace boundary",
        "English market research boundary",
    ):
        assert "Accounting and execution roadmap" in navigation[locale]
        assert "Research workspace migration boundary" in navigation[locale]
        assert "quant-market-research boundary" in navigation[locale]
        assert not re.search(r"[\u3400-\u9fff]", navigation[locale])
    for locale in (
        "Chinese accounting roadmap",
        "Chinese workspace boundary",
        "Chinese market research boundary",
    ):
        assert "治理与迁移" in navigation[locale]
        assert "会计与执行路线图" in navigation[locale]
        assert "历史迁移边界" in navigation[locale]
        assert "quant-market-research 边界" in navigation[locale]
        assert "Accounting and execution roadmap" not in navigation[locale]
