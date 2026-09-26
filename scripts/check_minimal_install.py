"""Check the installed base distribution without optional machine learning packages."""

from importlib.metadata import distributions


def main() -> None:
    forbidden = {"xgboost", "scikit-learn", "pandas-ta", "numba", "llvmlite"}
    installed = {dist.metadata["Name"].lower().replace("_", "-") for dist in distributions()}
    unexpected = installed & forbidden
    unexpected.update(name for name in installed if name.startswith("nvidia-nccl-"))
    if unexpected:
        raise RuntimeError(f"Unexpected optional dependencies: {sorted(unexpected)}")

    import alpha_research

    import portfolio_backtester
    from portfolio_backtester.backends import NativePositionReplayBackend

    assert portfolio_backtester.PositionBacktestConfig
    assert alpha_research.FactorExpression
    assert NativePositionReplayBackend
    print("Base imports work without machine learning dependencies")


if __name__ == "__main__":
    main()
