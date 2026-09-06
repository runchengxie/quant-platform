from strategy_pipeline.identity import DEFAULT_TARGET_SOURCE, PROJECT_DISTRIBUTION_NAME


def test_public_identity_matches_distribution_and_target_contract() -> None:
    assert PROJECT_DISTRIBUTION_NAME == "strategy-pipeline"
    assert DEFAULT_TARGET_SOURCE == "strategy-pipeline"
