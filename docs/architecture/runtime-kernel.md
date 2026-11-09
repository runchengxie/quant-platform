# Runtime and execution kernel boundaries

Language: English · [简体中文](runtime-kernel.zh-CN.md)

Platform 0.2.0 supports Python 3.12 and 3.13 with Engine Core 0.2.0 and SDK 0.3.0 at merged revision `51ab1e8cb2267d938a0681b81f2419d504ed91cc`. Core and SDK use the same exact VCS pin; no PyPI publication is required. Engine owns minute execution, paper accounts, reservations, execution planning and deterministic matching/replay/impact. Compatibility modules expose the identical Core objects; the pending adapter preserves Platform's full sparse validation and actual optimizer result. OSQP, statistical risk, research calibration, `pool_sleeves`, daily backtests and model training remain Platform responsibilities. Aliases stay for at least two minor-release cycles and until all recorded supported consumers migrate.

The optional native distribution belongs only to Engine; select `backend="rust"` explicitly after installing its wheel. There is no silent fallback. Native impact raises `NotImplementedError` before mutation because per-fill execution evidence is unavailable. Generator and `sqrt_law` remain Platform consumers; synthetic diagnostic slopes are not a calibrated market law. Account raw schema 2 and `execution-state.v2` identify the relocated owner. Older checkpoints require the full original pinned Platform/Runtime/Go/dependency environment; never convert or rebind them.

[Account events](../contracts/paper-account-events.md) · [Pending reservations](../contracts/pending-allocation.md)
