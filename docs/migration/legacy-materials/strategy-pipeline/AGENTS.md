# Agent 指南

## 迁移通知

`research-workspace` 处于 sunset 过渡期。新的策略编排和现金流运行流程进入 `quant-research`，可复用的编排 contract 进入 `quant-platform`。本仓库只维护历史复现和兼容迁移。

## 仓库定位

本仓库提供公开的通用控制面，负责 run 编排、artifact reference、receipt、publication
和下游 handoff。

策略思想、研究协议、特征和模型实现、组合规则、provider client、凭证以及私有数据
都属于使用方仓库，不能加入这里。

## 开发规则

- 公共 API 使用 `strategy_pipeline` namespace。
- 新能力优先通过 contract、protocol 和注入式 adapter 表达。
- 测试使用 synthetic fixture，不依赖私有仓库、网络服务、凭证或本地数据。
- runner 不应把 owner 异常细节写入公共 receipt。
- 修改公共 surface 后，必须同步检查导出清单和 clean-room 流程。

## 常用检查

```bash
uv run --with pytest pytest
uv run ruff check src tests scripts
python scripts/dev/public_surface_export.py --output /tmp/strategy-pipeline-public
```

导出目录应能独立安装，运行 `python scripts/dev/public_readiness.py --strict`，并通过
`PYTHONPATH=src python -m pytest tests/control_plane -q`。

## 提交边界

提交前确认没有策略名称、研究结论、provider 配置、凭证、私有路径或专有数据进入
公共仓库。需要引入 owner-specific 行为时，应在使用方仓库实现 adapter。
