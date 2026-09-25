# 执行接口

`quant_execution_engine` 提供公开的执行领域能力，包括目标文件标准化、类型化订单和组合模型、线缆编解码器、与券商无关的能力契约，以及确定性的模拟执行。

公开包不提供命令行入口。生产券商适配器及其命令由私有运行环境提供。

具体券商 SDK 适配器、凭证、实盘配置、审计存储和生产运行时由 `quant-research` 等私有环境负责。

迁移期间会暂时保留兼容命名空间，直到工作区完成从旧执行仓库的迁移。

## 输出路径

执行审计、状态和证据默认写入用户状态目录下的
`quant-platform/execution`。部署环境可以设置 `DATA_PLATFORM_ROOT`，此时路径为
`$DATA_PLATFORM_ROOT/quant-platform/execution`。也可以使用
`QUANT_PLATFORM_OUTPUT_ROOT` 指定平台输出根目录，或使用更具体的
`QEXEC_OUTPUTS_DIR` 指定一次运行的目录。

优先级从高到低为 `QEXEC_OUTPUTS_DIR`、`QUANT_PLATFORM_OUTPUT_ROOT`、
`DATA_PLATFORM_ROOT` 和 XDG 用户状态目录。显式传给状态存储或报告 API 的路径仍然有效。
这些默认值不会在 Git 工作树内创建 `outputs` 目录。
