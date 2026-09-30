# 市场数据消费边界

`quant-platform` 不包含 `market_data_platform` 兼容副本，也不承担市场数据生产。数据接入、规范化、质量治理、版本和已发布资产由 [`quant-market-data-platform`](https://github.com/runchengxie/quant-market-data-platform) 唯一维护。

平台仅通过公开产物、稳定文件格式和研究层输入消费数据。不直接导入数据平台的 Python 模块。平台自己的证券标识处理属于组合回测与编排输入处理，不保留旧兼容导入路径。
