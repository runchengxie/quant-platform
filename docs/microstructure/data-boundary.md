# TickNet 数据边界

语言：简体中文 · [English](data-boundary.en.md)

通用市场数据接入、标准化、质量治理、版本和发布由 `quant-market-data-platform` 负责。当前 `ticknet` 包没有直接连接该项目的 provider 或发布资产，下游研究项目负责提供版本化的数据 manifest 和标签。

## Owner 分工

`quant-market-data-platform` 负责：

- provider API 接入、raw landing、字段标准化和 canonical schema。
- 重复、缺失、乱序、异常值等通用质量检查。
- 数据版本、provenance、质量 receipt 和 published asset。

本仓库的 `ticknet` 负责：

- 提供 eventstream 数据打包、加载和数据集接口。
- 模型专属的盘口归一化、window 切分和特征 embedding。
- horizon label、leakage 检查、训练与验证切分。
- tensor materialization、模型训练、replay 和评估。

## 依赖方向

```text
quant-market-data-platform
  provider API -> ingest -> raw -> standardize -> canonical -> quality/provenance -> published asset

downstream research project
  published asset -> downstream-owned input/manifest -> model window/features/labels -> train/evaluate
```

跨仓数据交接由下游项目管理。可复用的通用清洗规则属于 `quant-market-data-platform`，只服务于模型输入的归一化、窗口、特征和标签逻辑属于 `ticknet`。本仓尚未实现 QMD adapter 或特定发布文件契约。

当前可在 `ticknet.eventstream` 找到数据集、打包和加载代码，但没有上述旧文档提到的 `canonical_adapter`、`nextday.snapshot_features` 或 `nextday.snapshot_io` 模块。`tests/test_microstructure_data_boundary.py` 检查 TickNet 源码和项目运行时依赖不直接引入 `quant_market_data_platform`、`tushare` 或 `rqdatac`。若将来增加独立 schema 包，应单独评审其职责和依赖。
