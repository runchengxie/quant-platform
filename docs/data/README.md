# Public market-data capability

`market_data_platform` in `quant-platform` contains reusable dataset contracts,
market/provider boundary helpers, published-asset metadata types, and
deterministic file/ordering utilities.

Provider adapters, credentials, raw datasets, local data roots, and production
manifests remain in the private research repository or deployment environment.
The public package must remain usable with synthetic fixtures and without
provider credentials.
