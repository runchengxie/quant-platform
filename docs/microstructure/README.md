# Public microstructure framework

This package contains reusable event-stream representations, dataset interfaces,
model building blocks, deterministic training utilities, and synthetic market
simulator mechanics.

It deliberately does not contain real L2 data, proprietary labels, research
universes, experiment results, promoted-model decisions, or production
configuration. Those remain in the private research repository.

The public namespace is preserved as `ticknet` during migration:

```python
from ticknet.eventstream.model import ModelConfig, build_eventstream_model
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.simulator.matching import MatchingEngine
```

Public tests use deterministic or synthetic inputs only. A downstream research
project may provide its own versioned data manifest and labels through these
interfaces.
