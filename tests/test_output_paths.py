from alpha_research import cpcv
from alpha_research.paths import resolve_output_path

from quant_execution_engine.paths import outputs_dir


def test_execution_outputs_prefer_specific_override(monkeypatch, tmp_path):
    monkeypatch.setenv("QEXEC_OUTPUTS_DIR", str(tmp_path / "execution"))
    monkeypatch.setenv("QUANT_PLATFORM_OUTPUT_ROOT", str(tmp_path / "owner"))
    monkeypatch.setenv("DATA_PLATFORM_ROOT", str(tmp_path / "data"))

    assert outputs_dir() == (tmp_path / "execution").resolve()


def test_execution_outputs_use_data_root_without_checkout_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("QEXEC_OUTPUTS_DIR", raising=False)
    monkeypatch.delenv("QUANT_PLATFORM_OUTPUT_ROOT", raising=False)
    monkeypatch.setenv("DATA_PLATFORM_ROOT", str(tmp_path / "data"))

    assert outputs_dir() == (tmp_path / "data" / "quant-platform" / "execution").resolve()


def test_alpha_default_reports_use_owner_root(monkeypatch, tmp_path):
    monkeypatch.setenv("ALPHA_RESEARCH_OUTPUT_ROOT", str(tmp_path / "research"))

    assert (
        cpcv._default_out_dir(None)
        == (tmp_path / "research" / "reports" / "cpcv_default").resolve()
    )


def test_alpha_explicit_relative_output_keeps_cli_compatibility(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALPHA_RESEARCH_OUTPUT_ROOT", str(tmp_path / "research"))

    assert (
        resolve_output_path("reports/custom", default_relative="reports/default")
        == (tmp_path / "reports" / "custom").resolve()
    )
