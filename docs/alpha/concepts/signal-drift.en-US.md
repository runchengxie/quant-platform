# Signal Distribution Drift

Language: English · [简体中文](signal-drift.md)

`alpha_research.signal_drift` provides framework-neutral diagnostics for comparing a frozen research/reference signal population with a later paper or live signal population.

The report includes:

- PSI using bins derived from reference quantiles
- The empirical two-sample Kolmogorov–Smirnov statistic
- Mean change measured in reference-standard-deviation units
- The ratio of current to reference standard deviation
- Finite observation counts for both populations
- An explicit flag for a constant reference population

The module reports metrics; it does not turn them into a strategy lifecycle verdict. Thresholds, failure conditions, research claims, and stop/continue decisions remain with the workspace's evidence and decision-governance layer.

Evidently may be evaluated later as an optional comparison or monitoring backend. Any adapter should normalize results to the platform drift contract and must not make Evidently's project model a cross-repository dependency.
