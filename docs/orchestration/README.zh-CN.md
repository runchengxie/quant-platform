# 任务编排

语言：简体中文 · [English](README.md)

`strategy_pipeline` 提供可复用的运行控制、产物发布、质量门禁、回执和 owner 交接契约。
策略专用逻辑、私有数据供应商和生产调度不属于这个公开包。

当前仓库继续提供 `strategy_pipeline` Python 命名空间和 `strategy-pipeline` CLI。它们是兼容名称，不代表仓库仍依赖旧的 `strategy-pipeline` 项目。

## 中文文档

- [控制平面 API](control-plane.zh-CN.md) 和 [评估流程](evaluation.zh-CN.md)
- [E2 晋升回执](e2-promotion-receipt.md) · [English](e2-promotion-receipt.en.md)
- [运行产物](output-artifacts.md)、[输出编排](output-orchestration.md)和[运行摘要](output-summary.md)
- [负责人接入](integrating-an-owner.md)、[目标导出](targets.md)和[证据与协议 CLI](evidence-protocol-cli.md)
- [运维概览](operations/README.md)、[质量门禁](operations/quality-gates.md)
- [开发与发布检查](development.md)
- [参考资料](reference/README.zh-CN.md)，包括 [CLI 辅助函数](reference/cli-helpers.zh-CN.md)、[配置解析](reference/configuration.zh-CN.md)和[运行时辅助函数](reference/runtime-helpers.md)

## 尚无英文版本

- [现金流发布指南](cashflow-publication.md)
- [发布审计](publication-audit.md)

其他页面的英文版本请从对应页面顶部切换。整体翻译进度见[本地化状态](../LANGUAGE_MIGRATION_STATUS.md)。
