# 分级研究协议

语言：简体中文 · [English canonical](research-protocols.en-US.md)

> status: active
> owner: quant-market-research
> audience: human and agent
> last_verified: 2026-10-05
> source_of_truth: yes
> superseded_by: n/a

`alpha_research.research_protocols` 为探索、候选和发布定义证据门槛。检查器验证提交的清单、引用文件、哈希和部分字段，不会独立证明研究无偏、可复现或具有经济价值。命令参数见[研究协议 CLI 参考](../../orchestration/evidence-protocol-cli.en.md)。

## 三个级别

| 级别 | 必需证据 | 清理策略 |
| --- | --- | --- |
| `exploratory` | 已发布数据契约、可复现运行记录、试验台账 | 不要求事件窗口清理，允许 fallback。 |
| `candidate` | 探索证据，加上特征证据、弱模型基线、前推验证、最终样本外、CPCV、成本／换手／容量、暴露筛查和负控制 | 清单需声明 `event_window` 模式、覆盖率至少 95%，且未使用 fallback。 |
| `release` | 候选证据，加上 DSR、PBO 或说明原因的 `insufficient_evidence`、场景回测、候选冻结、paper／shadow 证据、仓位回执、策略风险报告和操作员审批 | 清单需声明 `event_window` 模式、覆盖率至少 99%，且未使用 fallback。 |

覆盖率是检查器读取并核对的清单值，检查器不会自行计算事件窗口或覆盖率。PBO 使用 `insufficient_evidence` 时必须填写非空原因。

## 初始化和检查清单

```bash
strategy-pipeline research-protocol \
  --level candidate \
  --init-manifest artifacts/reports/candidate_protocol.yml
```

每项证据可以包含以下字段：

```yaml
status: missing
path: null
sha256: null
notes: Evidence description
```

只填写 `status: pass` 不够。对文件类证据，检查器按清单所在目录解析 `path`，确认文件存在并核对 SHA-256。操作员审批还需填写 `approved_by` 和 `approved_at`。用 `--manifest` 检查清单，默认 strict 模式在报告不通过时返回非零退出码。报告默认写入 `research_protocol_report.json`，也可用 `--output` 指定路径。

如果交接门会读取报告，应将它写在对应运行目录中：

```bash
strategy-pipeline research-protocol \
  --level release \
  --manifest artifacts/reports/release_protocol.yml \
  --output artifacts/runs/example/research_protocol_report.json
```

## 生成仓位与风险证据

运行目录需包含 `backtest_net.csv`（字段 `period_end`、`net_return`）、`backtest_gross.csv`（字段 `period_end`、`gross_return`）、`backtest_turnover.csv`（字段 `period_end`、`turnover`），以及 `positions_current_live.csv` 或 `positions_current.csv`（含 `symbol` 或 `ticker` 字段和 `weight`）：

```bash
strategy-pipeline afml-evidence \
  --run-dir artifacts/runs/example \
  --target-sharpe 1.0 \
  --evaluation-years 2 \
  --bootstrap-samples 2000 \
  --manifest artifacts/reports/release_protocol.yml \
  --manifest-output artifacts/reports/release_protocol.with_afml.yml
```

命令生成 `sizing_receipt.json`、`strategy_risk_report.json` 和 `afml_evidence_fragment.json`。配置 `--hrp-returns` 后，还会生成 `hrp_weights.csv` 和 `hrp_receipt.json`。收益矩阵第一列为日期，后面至少有两列时间同步的收益序列。命令可以将生成证据合并进协议清单。不指定 `--manifest-output` 时会覆盖输入清单。

## 在 pipeline 运行后自动生成

配置后，pipeline 可在运行产物写完后生成相同的 sidecar：

```yaml
research_protocol:
  generate_afml_evidence: true
  target_sharpe: 1.0
  evaluation_years: 2.0
  bootstrap_samples: 2000
  random_state: 7
  hrp_returns: artifacts/reports/sleeve_returns.csv
  require_release_report: true
```

`generate_afml_evidence` 默认关闭，`hrp_returns` 为可选项。`require_release_report` 会让运维／导出交接门要求运行目录中存在通过检查的 `research_protocol_report.json`，不会改变持仓、权重或订单。

协议报告用于判断研究证据能否进入交接流程。通过协议不代表可以省略对研究方法和结果的人工复核。
