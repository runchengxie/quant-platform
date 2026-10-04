# Public microstructure framework

Language: English · [简体中文](README.md)

The `ticknet` package provides event-stream representations, dataset interfaces, model components, deterministic training utilities, and a synthetic market simulator.

Real L2 data, proprietary labels, research universes, experiment results, model-promotion decisions, and production configuration stay in private research systems. They are not included in this public package.

Python is the default simulator backend. The optional Rust extension adds order-book matching, batch replay, and event ordering; it must be built and installed separately. See the [Rust kernel guide](../development/microstructure-rust.en.md) for setup, differential tests, and synthetic benchmarks.

Public tests use deterministic or synthetic inputs. Downstream projects provide their own versioned data manifests and labels.

```python
from ticknet.eventstream.model import ModelConfig, build_eventstream_model
from ticknet.eventstream.dataset import L2WindowDataset
from ticknet.simulator.matching import MatchingEngine
```
