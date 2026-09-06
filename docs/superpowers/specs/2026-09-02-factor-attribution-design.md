# 因子归因设计

## 目标

增加与框架无关的主动收益和主动风险归因原语，可以消费平台风险模型，并在后续为 Dashboard 提供证据。

## 设计

Return attribution decomposes net active return into factor contributions, a residual specific term, and explicit transaction-cost drag. Risk attribution decomposes active variance into per-factor variance contributions plus independent specific variance.

The module accepts weights, benchmark weights, exposures, factor returns/covariance, and specific risk as plain pandas objects. It does not estimate the risk model, choose a benchmark, or implement Brinson allocation/selection attribution.

## 不在本次范围内

- no proprietary RQPAttr dependency;
- no blending of Brinson and multifactor attribution semantics;
- no estimation of factor covariance/specific risk;
- no Dashboard-side recomputation.
