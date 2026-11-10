# Provider C 消费层契约

[English](provider-c-consumer.md)

Platform 0.3.0 将日频和分期金融计算委托给已合并 Engine `ad0895f1c2015eb31bd364b40741b0f7cd6e0048`（Core、SDK 均为 0.3.0）。目标构建、研究统计、数据方日历查询与发布仍由 Platform 负责。归一化语义不同的历史交易会计函数保留各自的 Core 对象身份。

实施顺序为：保留原公开流程基准，验证缺失 adapter 的失败，固定两个已合并提供方，用别名替换内核，恢复原研究统计，再验证公开完整输出、Python 3.12/3.13 普通安装及配对文档。[测试来源记录](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-c-test-provenance.json) 明确 Engine 是内核测试的权威所有者。Platform 保留测试用于公开接口集成，而非另一套金融实现。

接口兼容修订为 `to_canonical_result(result, *, artifact_root: Path | None = None)`。单参数调用保守转换中立证据。显式 root 的原始完整转换验证相对 URI、摘要、媒体类型、schema 和支持的 dtype，不执行序列化代码。表结构完整、估值完整和 canonical 可表示性互相独立。取得原表不能把缺失估值或应收权益变成已支持的现金或收益，详见[日频消费层](../backtest/engine-daily.zh-CN.md)。

验收逐字段比较原 native/sequenced/position/top-k 的收益、分期、研究摘要及八表，不放宽 dtype。同时包括独立手算基准、序列化身份、真实 native/Rust 执行和不完整证据的发布拒绝。历史直接接口的统计保留旧公式及限制。

外部 cohort 必须逐一报告。直接兼容 seam 不等于 Runtime 任务执行成功，源码 pin 不等于完整可执行环境恢复。深度学习信号验收仍固定 Platform/contracts `282afca4c4ca210d46eed096a943972662fede99`。市场 synthetic-chain 准入保留历史多仓 pin。microcap 诊断依赖 Runtime。完整历史 Runtime/Go/Python 恢复仍属 Tasks 16–17。所有兼容别名至少保留两个次版本，并持续保留至全部受支持消费者迁移。本波次不迁移生产环境、券商连接或检查点。
