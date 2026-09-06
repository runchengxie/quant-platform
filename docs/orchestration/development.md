# 开发与发布检查

## 本地测试

运行完整测试和静态检查：

```bash
uv run --with pytest pytest
uv run ruff check src tests scripts
```

公共包的测试位于 `tests/control_plane`。测试使用 synthetic owner 和 publisher，
不需要私有模块、凭证、网络服务或策略数据。

## Clean-room 检查

导出经过审阅的公共 surface：

```bash
python scripts/dev/public_surface_export.py --output /tmp/strategy-pipeline-public
cd /tmp/strategy-pipeline-public
python scripts/dev/public_readiness.py --strict
PYTHONPATH=src python -m pytest tests/control_plane -q
```

导出目录应能独立安装和运行。发布前还应检查导出结果的 Git 历史、依赖来源、许可证、
CI 配置和敏感信息扫描结果。
