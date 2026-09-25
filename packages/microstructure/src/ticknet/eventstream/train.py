"""Compatibility facade for the eventstream training API."""

from __future__ import annotations

from ticknet.eventstream.checkpoints import _atomic_json as _atomic_json
from ticknet.eventstream.checkpoints import _atomic_torch_save as _atomic_torch_save
from ticknet.eventstream.checkpoints import (
    _checkpoint_matches_experiment as _checkpoint_matches_experiment,
)
from ticknet.eventstream.checkpoints import _checkpoint_paths as _checkpoint_paths
from ticknet.eventstream.checkpoints import _environment as _environment
from ticknet.eventstream.checkpoints import _experiment_signature as _experiment_signature
from ticknet.eventstream.checkpoints import _json_safe as _json_safe
from ticknet.eventstream.checkpoints import _load_checkpoint as _load_checkpoint
from ticknet.eventstream.checkpoints import (
    _warm_start_from_checkpoint as _warm_start_from_checkpoint,
)
from ticknet.eventstream.cli import main as main
from ticknet.eventstream.data_loading import _resolve_days as _resolve_days
from ticknet.eventstream.data_loading import _window_dataset_kwargs as _window_dataset_kwargs
from ticknet.eventstream.data_loading import list_packed_days as list_packed_days
from ticknet.eventstream.data_loading import make_dataloaders as make_dataloaders
from ticknet.eventstream.data_loading import make_monitor_dataloaders as make_monitor_dataloaders
from ticknet.eventstream.evaluation import _empty_metrics as _empty_metrics
from ticknet.eventstream.evaluation import _spearman as _spearman
from ticknet.eventstream.evaluation import evaluate_rank_ic as evaluate_rank_ic
from ticknet.eventstream.training import train as train
from ticknet.eventstream.training_config import EventstreamConfig as EventstreamConfig

if __name__ == "__main__":
    main()
