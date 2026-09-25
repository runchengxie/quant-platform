from __future__ import annotations

import ticknet.eventstream.data_loading as data_loading
import ticknet.eventstream.train as train_module
from ticknet.eventstream.train import EventstreamConfig, list_packed_days


def test_list_packed_days_sorts_and_filters_requested_range(tmp_path, monkeypatch):
    for day in (20210105, 20210103, 20210104):
        (tmp_path / f"index_{day}.npz").touch()
    monkeypatch.setattr(data_loading, "day_is_packed", lambda day, root: day != 20210104)

    days = list_packed_days(20210103, 20210105, tmp_path)

    assert days == [20210103, 20210105]


def test_checkpoint_signature_matches_only_same_experiment():
    config = EventstreamConfig(days=(20210104,))
    signature = train_module._experiment_signature(config, "fingerprint")
    checkpoint = {"experiment": signature}

    assert train_module._checkpoint_matches_experiment(checkpoint, signature)
    assert not train_module._checkpoint_matches_experiment(
        checkpoint,
        {**signature, "dataset_fingerprint": "different"},
    )
    assert not train_module._checkpoint_matches_experiment({}, signature)


def test_train_compatibility_entrypoints_are_importable():
    assert callable(train_module.train)
    assert callable(train_module.main)
    assert train_module.EventstreamConfig is EventstreamConfig
    assert train_module.list_packed_days is list_packed_days


def test_training_cli_help_keeps_current_options(capsys):
    import pytest

    with pytest.raises(SystemExit) as result:
        train_module.main(["--help"])

    assert result.value.code == 0
    output = capsys.readouterr().out
    assert "--day-supervision-mode" in output
    assert "--evaluate-test" in output
