from __future__ import annotations

import re
import tomllib
from pathlib import Path

import portfolio_backtester
from portfolio_backtester import execution_sim

ROOT = Path(__file__).resolve().parents[1]
FACT_DOCS = (
    ROOT / "docs" / "concepts" / "cost-breakdown.zh-CN.md",
    ROOT / "docs" / "guides" / "execution-simulation.md",
    ROOT / "docs" / "reference" / "public-api.md",
)
STYLE_DOCS = (
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    *sorted(
        path
        for path in (ROOT / "docs").rglob("*.md")
        if "superpowers" not in path.relative_to(ROOT / "docs").parts
    ),
)
STYLE_PATTERNS = (
    re.compile(r"不是.{0,40}而是"),
    re.compile(r"并非.{0,40}而是"),
    re.compile(r"\*\*"),
    re.compile("\uff1b"),
    re.compile("\u2014\u2014"),
    re.compile("[\u201c\u201d]"),
)


def test_docs_use_concise_chinese_style() -> None:
    offenders: list[str] = []

    for path in STYLE_DOCS:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            for pattern in STYLE_PATTERNS:
                if pattern.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{line_number}:{pattern.pattern}")

    assert offenders == []


def test_testing_docs_match_script_modes() -> None:
    script = (ROOT / "scripts" / "dev" / "run_tests.sh").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "testing.zh-CN.md").read_text(encoding="utf-8")

    for mode in (
        "all",
        "fast",
        "unit",
        "coverage",
        "contracts-coverage",
        "lint",
        "format",
        "typecheck",
        "typecheck-release",
        "maintainability",
    ):
        assert f"`{mode}`" in docs
        assert mode in script


def test_coverage_mode_scans_project_sources_and_dependency_is_installed() -> None:
    script = (ROOT / "scripts" / "dev" / "run_tests.sh").read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev_dependencies = [
        *pyproject["project"]["optional-dependencies"]["dev"],
        *pyproject["dependency-groups"]["dev"],
    ]

    assert "--cov=packages --cov=scripts --cov=research_contracts" in script
    assert any(dependency.startswith("pytest-cov") for dependency in dev_dependencies)


def test_documentation_build_excludes_historical_archives() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "migration/legacy-materials/**" in config


def test_typecheck_script_registers_all_source_roots() -> None:
    script = (ROOT / "scripts" / "dev" / "run_tests.sh").read_text(encoding="utf-8")

    for source_root in (
        "packages/portfolio-backtester/src",
        "packages/orchestration/src",
        "packages/execution/src",
        "packages/alpha/src",
        "packages/microstructure/src",
    ):
        assert source_root in script
    assert 'search_path_args+=(--extra-search-path "$source_root")' in script


def test_ty_is_the_only_configured_type_checker() -> None:
    legacy_checker = "".join(("based", "py", "right"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    script = (ROOT / "scripts" / "dev" / "run_tests.sh").read_text(encoding="utf-8").lower()

    assert "[tool.ty.src]" in pyproject
    assert legacy_checker not in pyproject
    assert legacy_checker not in script


def test_docs_record_current_automation_status() -> None:
    docs = (ROOT / "docs" / "testing.zh-CN.md").read_text(encoding="utf-8")

    assert "`.github/workflows/ci.yml`" in docs
    assert "PR 和主分支推送时运行公开质量门禁" in docs
    assert "`.github/workflows/docs.yml`" in docs
    assert (ROOT / ".github" / "workflows" / "ci.yml").is_file()
    assert (ROOT / ".github" / "workflows" / "docs.yml").is_file()


def test_english_testing_guide_matches_current_scripts_and_ci() -> None:
    docs = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "dev" / "run_tests.sh").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "Language: English · [简体中文](testing.zh-CN.md)" in docs
    for mode in (
        "all",
        "fast",
        "unit",
        "coverage",
        "contracts-coverage",
        "lint",
        "format",
        "format-all",
        "typecheck",
        "typecheck-release",
        "maintainability",
    ):
        assert f"`{mode}`" in docs
        assert mode in script
    assert "Python 3.12 and 3.13" in docs
    assert "3.12" in ci and "3.13" in ci
    assert "TICKNET_REQUIRE_RUST=1" in docs
    assert "TICKNET_REQUIRE_RUST=1" in ci


def test_orchestration_configuration_docs_match_loader_and_tests() -> None:
    docs = (ROOT / "docs" / "orchestration" / "reference" / "configuration.md").read_text(
        encoding="utf-8"
    )
    implementation = (
        ROOT / "packages" / "orchestration" / "src" / "strategy_pipeline" / "config.py"
    ).read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "orchestration" / "test_config.py").read_text(encoding="utf-8")

    assert "Language: English · [简体中文](configuration.zh-CN.md)" in docs
    for behavior in (
        "def resolve_config(",
        "def deep_merge(",
        'EXTENDS_KEY = "extends"',
        "Circular extends detected",
        'source=f"package:{package}/{filename}"',
    ):
        assert behavior in implementation
    for behavior in (
        "test_resolve_config_supports_alias_and_relative_extends",
        "test_resolve_config_falls_back_to_filename_in_search_roots",
        "test_resolve_config_rejects_circular_extends",
        "test_resolve_config_accepts_an_injected_normalizer",
    ):
        assert behavior in tests


def test_cli_helpers_docs_match_public_helpers_and_behavior_tests() -> None:
    docs = (ROOT / "docs" / "orchestration" / "reference" / "cli-helpers.md").read_text(
        encoding="utf-8"
    )
    implementation = (
        ROOT / "packages" / "orchestration" / "src" / "strategy_pipeline" / "cli_helpers.py"
    ).read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "orchestration" / "test_cli_helpers.py").read_text(encoding="utf-8")

    assert "Language: English · [简体中文](cli-helpers.zh-CN.md)" in docs
    for helper in (
        "format_bytes",
        "render_pct_bar",
        "coerce_float",
        "append_arg",
        "append_repeat_args",
        "append_bool_switch",
        "append_passthrough",
    ):
        assert f"`{helper}(" in docs
        assert f'"{helper}"' in implementation
    assert "def test_cli_value_formatters" in tests
    assert "def test_cli_argument_helpers" in tests


def test_docs_distinguish_current_backends_from_history_and_plans() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs" / "concepts" / "backend-architecture.md").read_text(
        encoding="utf-8"
    )
    docs = "\n".join((readme, agents, architecture))

    assert "registry 只包含 `native.position_replay`" in docs
    assert "Qlib 与 LEAN 的历史候选没有进入 `main`" in docs
    assert "LEAN 只" in docs and "架构参考" in docs
    assert "no-adoption" in docs
    assert "Backtrader" in docs and "规划" in docs
    assert "vn.py" in docs and "范围外" in docs


def test_public_api_docs_cover_root_exports_and_execution_sim_surface() -> None:
    public_api_docs = FACT_DOCS[2].read_text(encoding="utf-8")
    execution_docs = FACT_DOCS[1].read_text(encoding="utf-8")

    for name in portfolio_backtester.__all__:
        assert f"`{name}`" in public_api_docs
    for name in execution_sim.__all__:
        assert f"`{name}`" in execution_docs


def test_docs_record_current_cost_and_position_limitations() -> None:
    cost_docs = FACT_DOCS[0].read_text(encoding="utf-8")
    execution_cost_docs = (ROOT / "docs" / "concepts" / "execution-costs.zh-CN.md").read_text(
        encoding="utf-8"
    )
    positions_docs = (ROOT / "docs" / "reference" / "outputs" / "positions.zh-CN.md").read_text(
        encoding="utf-8"
    )

    assert "内置滑点会进入 `fee_cost`" in cost_docs
    assert "buy_slippage_bps` 与 `sell_slippage_bps` 设为 0" in cost_docs
    english_cost_docs = (ROOT / "docs" / "concepts" / "cost-breakdown.md").read_text(
        encoding="utf-8"
    )
    assert "temporary_impact" in english_cost_docs
    assert "from_components" in english_cost_docs
    assert "买卖各 10 个基点" in execution_cost_docs
    english_execution_cost_docs = (ROOT / "docs" / "concepts" / "execution-costs.md").read_text(
        encoding="utf-8"
    )
    assert "DetailedTradeFeeModel" in english_execution_cost_docs
    assert "does not calculate live quotes" in english_execution_cost_docs
    assert "`long_only=False` 不会启用空头回放" in positions_docs
    english_positions_docs = (ROOT / "docs" / "reference" / "outputs" / "positions.md").read_text(
        encoding="utf-8"
    )
    assert "research.artifact-envelope.v2" in english_positions_docs
    assert "does not enable short replay" in english_positions_docs


def test_docs_record_public_private_boundary_and_index_new_pages() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese_readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert "private research layer" in readme
    assert "私有研究层" in chinese_readme
    assert "策略研究假设、专有特征和晋升规则属于私有研究层" in agents
    assert "guides/execution-simulation.md" in index
    assert "concepts/afml-sizing-and-risk.md" in index


def test_backtest_output_docs_point_to_current_pipeline_owner() -> None:
    outputs = (ROOT / "docs" / "reference" / "outputs" / "backtest-outputs.md").read_text(
        encoding="utf-8"
    )
    interpretation = (ROOT / "docs" / "concepts" / "backtest-interpretation.md").read_text(
        encoding="utf-8"
    )
    assert "../../orchestration/output-summary.md" in outputs
    assert "../../reference/public-api.md" in outputs
    assert "../orchestration/output-summary.md" in interpretation
    assert "../reference/public-api.md" in interpretation
