# Factor Catalog

Language: English · [简体中文](factor-catalog.md)

The factor catalog registers reusable factors as versioned research assets. This avoids treating a Python function name as the factor's identity.

Each `FactorSpec` records:

- A stable factor ID and explicit version
- Owner and frequency
- Declared dependencies
- Point-in-time (`PIT`) semantics
- Formation-universe semantics
- Preprocessing steps
- SHA-256 digest of the implementation
- Optional description

`FactorEvidenceSummary` stores dated evidence summaries, not raw research outputs. Current fields include IC, rank IC, ICIR, turnover, neutralized rank IC, decay horizon, observation count, and lifecycle status: `research`, `candidate`, `production`, or `retired`.

A factor may have multiple versions. Evidence must refer to a specific `(factor_id, version)`. The catalog rejects duplicate evidence for the same factor version and date.

The design follows factor lifecycle and productization ideas discussed by RQFactor, while keeping PIT semantics and evidence ownership in this platform. Alphalens Reloaded could later support differential report checks, but it is not the standard factor-identity catalog.
