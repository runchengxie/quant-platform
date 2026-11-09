# 分钟执行情景 {#provider-a-compatibility}

语言：简体中文 · [English](minute-execution.en.md)

本页相关的分钟执行与基础证据实现已由 Engine 0.1.0 提供。请参阅[当前中文文档](https://runchengxie.github.io/quant-backtest-engine/guides/minute-execution.zh-CN/)。Platform 0.1.0 保留原有导入路径，直接导出同一个 Engine 对象。

统计风险、通用组合优化以及尚未迁移的集成仍由 Platform 维护。目标页面标明了当前支持范围。

[迁移前文档及历史证据](https://github.com/runchengxie/quant-platform/blob/7a618bddd8fdeee5dbe37fe5b54a9698e0de5355/docs/guides/minute-execution.md)保留原始语义。

历史 v2 检查点只能在原来固定的完整发布环境中恢复，包括 Runtime/Go 可执行文件、Python 依赖和原始来源绑定。新提供方会拒绝 v2。不能修改版本字段来恢复，也不能仅安装旧 Platform wheel 就宣称完成恢复。

<a id="_1"></a>
<a id="_2"></a>
<a id="_3"></a>
