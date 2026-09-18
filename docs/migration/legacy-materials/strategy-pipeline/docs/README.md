# 文档

> status: active
> owner: strategy-pipeline
> audience: human and agent
> last_verified: 2026-09-06
> source_of_truth: yes
> superseded_by: n/a

本公共仓库说明通用控制面和评估编排，不包含具体策略实现。

- [控制面 API](control-plane.md)：contract、runner、publication 和 handoff。
- [晋级回执](e2-promotion-receipt.md)：为已完成的研究检查生成带 lineage 哈希的回执。
- [owner 接入指南](integrating-an-owner.md)：adapter 形状和依赖边界。
- [评估编排](evaluation.md)：评估指标、组合回放和结果产物之间的通用连接方式。
- [运行摘要](output-summary.md)：把运行上下文和产物引用整理成结构化摘要。
- [运行产物](output-artifacts.md)：写入数据集、信号、回测和诊断产物。
- [运行输出编排](output-orchestration.md)：按固定顺序调用产物、证据、摘要和元数据写入器。
- [质量闸门](operations/quality-gates.md)：统一处理运行质量和 release protocol 交接条件。
- [运行时辅助能力](reference/runtime-helpers.md)：日志、配置哈希和日期切分辅助函数。
- [配置解析](reference/configuration.md)：通用 YAML、`extends` 和别名解析。
- [证据与协议 CLI](evidence-protocol-cli.md)：生成研究证据和评估 protocol manifest。
- [CLI 辅助函数](reference/cli-helpers.md)：参数拼接、数值格式化和进度条辅助函数。
- [目标文件导出](targets.md)：将通用 holdings JSON 转换为执行侧可读取的 `targets.json`。

策略思想、研究协议、provider 配置、凭证和私有运行手册应放在使用方仓库。

编码代理默认读取本页、一个相关分类 README 和目标页面，不递归读取全部 Markdown。
