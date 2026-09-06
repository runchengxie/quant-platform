# quant-platform

`quant-platform` 是公开的通用量化平台，提供可以被多条策略共同使用的研究、回测和组合工具。

这里关注通用能力，不保存某一条策略的专有规则和真实研究数据。

策略假设、专有特征和晋升证据属于私有研究层，由 `quant-research` 维护。

## 这里提供什么

- 数据集和研究产物的通用接口
- 回测、组合构造、风险分析和执行模拟
- 公开的研究契约和发布工具
- 可复现的测试、示例和质量检查

## 这里不放什么

- 数据供应商接入、凭证和原始数据
- 某条策略的选股规则、特征、标签和模型参数
- 私有实验结果、生产配置和部署密钥

市场数据由独立的 [`market-data-platform`](https://github.com/runchengxie/market-data-platform) 负责生产和发布。
策略研究由 [`quant-research`](https://github.com/runchengxie/quant-research) 负责。
两者的详细边界见[迁移说明](docs/migration/research-workspace-sunset.md)。

## 新人阅读路径

1. 阅读[文档入口](docs/README.md)，了解目录和推荐顺序。
2. 阅读[回测入口](docs/guides/entry-points.md)，运行一个最小示例。
3. 根据任务查看[概念文档](docs/concepts/)或对应的专题目录。
4. 运行[测试和质量检查](docs/testing.md)。

如果你要研究现金流策略，请先从 `quant-research` 开始。这里可以承载抽象后的组合、风险和发布能力，
不负责保存现金流策略本身。

## 当前状态

本仓库处于从 `research-workspace` 和旧平台子模块迁移的阶段。当前版本已经提供一部分公开回测和组合能力，
完整迁移范围、兼容期规则和回滚信息见[迁移说明](docs/migration/research-workspace-sunset.md)。

## 开发规范

并行开发时，每项改动都使用独立 worktree、功能分支和 PR。测试、依赖、发布和文档维护规则见
[`AGENTS.md`](AGENTS.md) 和 [`docs/README.md`](docs/README.md)。

本仓库采用 Apache License 2.0，详见 [LICENSE](LICENSE)。许可证只适用于本仓库中的原始公开框架内容。
