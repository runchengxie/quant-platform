# 开发与发布检查

语言：简体中文 · [English](development.en.md)

## 仓库检查

在仓库根目录运行当前项目规定的检查：

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
```

编排控制平面测试位于 `tests/orchestration/control_plane/`。测试使用合成 owner 和 publisher，不需要私有模块、凭证、生产服务或策略数据。

## Clean-root 发布审计

早期发布审计中记录的 clean-root 导出步骤目前无法从此检出版本复现。导出脚本读取 `docs/public-surface-manifest.json`，而经过审阅的 manifest 位于 `docs/orchestration/public-surface-manifest.json`。该 manifest 列出的 50 个路径中，有 41 个在当前仓库布局中不存在。不要把旧导出结果当作当前发布检查，也不要把旧命令当作已通过的检查运行。

历史[发布审计](publication-audit.md)记录了当时的证据和适用范围。发布 clean-root 包之前，需要先按当前代码和测试校准 manifest，更新导出脚本及其测试，然后重新运行 clean-tree 和完整 Git 历史审计。本页不授权更改仓库可见性。
