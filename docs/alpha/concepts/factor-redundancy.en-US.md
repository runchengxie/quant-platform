# Same-date factor redundancy

[简体中文](factor-redundancy.zh-CN.md)

`alpha_research.factor_redundancy.factor_redundancy(scores, top_fraction=...,
min_cross_section=...)` compares numeric signals on a unique timestamp/symbol
MultiIndex named `date` and `symbol`. Supply at least two named factors,
`0 < top_fraction <= 0.5`, and an integer minimum cross-section of at least three.
It returns three DataFrames: `pairs`, `coverage`, and `rank`.

Pair statistics use the pair's complete common observations on each date:
Spearman rank correlation, same-side top/bottom Jaccard overlap and left-top to
right-bottom overlap. Tails take at least `ceil(n * top_fraction)` observations,
retaining all ties at the boundary and reporting actual tail sizes. Pair sample
sizes can differ; always inspect coverage before comparing dates or pairs.

The rank table uses the complete sample across ALL factors on that date. Its
participation ratio is `(sum eigenvalues)^2 / sum(eigenvalues^2)` of the Spearman
correlation matrix. Pairwise-deletion matrices are never used for that estimate.
Constant signals, insufficient common samples or a materially non-PSD matrix
produce explicit statuses and missing rank, without filling or repairing data.
Infinities, duplicate keys and malformed indexes fail. Dates are independent:
adding future observations cannot change an earlier date's result.

These diagnostics do not establish economic independence, joint tail safety,
leave-one-out value, net portfolio improvement or the effective number of
statistical search trials. Leave-one-out research requires actual refitting under
the frozen protocol and a record of additional outcome access. Supply universe,
PIT availability, feature definitions and baseline identity in the consuming
research receipt. The numerical mechanism does not certify them.
