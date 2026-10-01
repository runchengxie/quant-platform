# Market data consumption boundary

Language: English · [简体中文](README.zh-CN.md)

`quant-platform` does not include the `quant_market_data_platform` package and does not produce market data. Data ingestion, normalization, quality governance, versioning, and published assets are owned by [`quant-market-data-platform`](https://github.com/runchengxie/quant-market-data-platform).

The platform consumes data only through public artifacts, stable file formats, and research-layer inputs. It does not import Python modules from the data platform. Security identifier handling inside this repository is limited to portfolio backtest and orchestration input processing; the repository does not retain the former compatibility import path.
