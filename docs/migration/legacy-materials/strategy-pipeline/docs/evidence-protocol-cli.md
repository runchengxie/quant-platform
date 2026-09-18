# 证据与协议 CLI

公共 `strategy-pipeline` 提供两个通用命令入口：`afml-evidence` 用于生成运行证据，
`research-protocol` 用于初始化或评估研究协议 manifest。

```bash
strategy-pipeline research-protocol --level exploratory --init-manifest protocol.yml
strategy-pipeline afml-evidence --run-dir artifacts/runs/example
```

具体证据计算由 `portfolio-backtester` 提供，协议检查由 `alpha-research` 提供。公共仓库只负责
参数解析、文件读写和命令编排。
