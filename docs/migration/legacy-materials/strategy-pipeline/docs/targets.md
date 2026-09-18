# 目标文件导出

公共 pipeline 提供 `export-targets`，负责把 owner 生成的 holdings JSON 转换为标准
`quant-execution-engine.targets/v2` 目标文件。它只处理文件格式、市场后缀和基本数值校验，
不读取策略配置，不加载数据 provider，也不连接券商。

输入可以是 holdings 数组，也可以是包含 `holdings` 数组的对象：

```json
{
  "run_id": "run-20260905",
  "as_of": "2026-09-05",
  "holdings": [
    {"symbol": "600000.SH", "weight": 0.6},
    {"symbol": "000001.SZ", "weight": 0.3}
  ]
}
```

运行命令：

```bash
strategy-pipeline export-targets \
  --holdings artifacts/holdings.json \
  --out artifacts/targets.json
```

命令同时生成 `targets.json.lineage.json`。导出器只接受多头、非负且总和不超过 1 的权重，
并拒绝重复的标准化证券标识。`.SH`、`.SZ`、`.BJ`、`.XSHG` 和 `.XSHE` 后缀会转换为
`market: CN`。目标文件交给 `quant-execution-engine` 做 dry-run、模拟盘或实盘门禁。
