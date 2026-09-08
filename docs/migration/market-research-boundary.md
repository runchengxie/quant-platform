# Market-research boundary

`market-research` owns study-specific market evidence, including long-horizon
style-factor behavior and the six-market ETF proxy allocation experiment.

`quant-platform` remains responsible for generic backtesting, portfolio
accounting, risk, cost, execution simulation, and research artifact contracts.
It must not encode study-specific policies such as an 18-year window, target
market weights, ETF proxy choices, or factor promotion rules.

The portfolio-backtester style-factor slice remains excluded from the public
release while source licensing is unresolved. No code is copied into
`market-research` from that slice.
