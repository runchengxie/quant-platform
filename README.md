# quant-platform

`quant-platform` 是公开的量化研究与投资组合基础平台。

它提供可复用的回测、组合、执行模拟、风险分析和研究产物接口，供研究项目调用。策略假设、专有特征、真实策略输入和晋升证据属于 `quant-research` 等研究仓库，本仓库不保存这些内容。

## 适合谁使用

- 想运行示例回测的研究者
- 需要复用组合、风险或产物接口的开发者
- 需要了解公开量化基础能力边界的维护者

## 快速开始

安装开发依赖并运行检查：

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
```

运行一个公开示例：

```bash
uv run portfolio-style-factor \
  --input examples/synthetic-style-factor.csv \
  --output /tmp/style-factor-report.json \
  --signal size \
  --quantiles 2
```

## 去哪里找详细说明

- [文档总览](docs/README.md)
- [开发约定](AGENTS.md)
- [回测与组合说明](docs/concepts/backtest-spec.md)
- [研究产物与公开接口](docs/reference/public-api.md)
- [迁移与边界说明](docs/migration/research-workspace-sunset.md)

文档中的技术说明以当前代码和测试为准。README 只保留项目定位、使用入口和导航，具体接口、架构、兼容性和迁移记录请查看 `docs/`。

## 仓库边界

`quant-platform` 负责通用能力，例如回测、组合构造、风险和成本、执行模拟，以及可复用的研究产物契约。

以下内容由其他仓库负责：

- `market-data-platform`：数据采集、清洗、质量检查、版本和发布
- `quant-research`：策略、特征、机器学习、实验和研究结论
- `market-intel`：报告、看板和研究结果交付

研究项目通过已发布的数据资产和版本化产物与本仓库协作。`quant-platform` 不接入数据供应商，不保存真实策略输入，也不承载专有策略逻辑。

## 许可证

本仓库采用 Apache License 2.0。许可范围仅包括本仓库中的公开框架代码，不包含私有策略、专有数据、凭证和第三方依赖。

详见 [LICENSE](LICENSE)。
