# Legacy technical and portfolio mechanisms

The technical panel and portfolio helpers migrated from the owner's public
`a-share-factor-core` commit `f68b602ecded17a3f18482d198e88f088d3c7529`.
The new modules are `alpha_research.technical.legacy_features` and
`portfolio_backtester.legacy_rotation`; they require no adjacent source checkout.
Install `quant-platform[ml]` for the optional `ta` technical-indicator dependency.

Technical computation preserves historical forward-fill/zero-fill, column order,
rolling definitions and short-input behavior. Consumers must enforce sufficient
history; a filled zero does not establish a valid feature observation. The
feature function is split into two sequential helpers to meet the existing
function-length gate without changing calculation order.

Portfolio API revision `legacy_rotation.v2` preserves equal-weight cash under
binding caps, diagonal shrinkage and standard optimization. Two inherited defects
are explicitly corrected: a zero/negative cap retains all cash even with a
covariance matrix, and covariance rows/columns are aligned to expected-return
labels. Missing labels raise instead of silently optimizing the wrong assets.
These edge cases are intentional semantic differences from the frozen source.
Do not call a migration parity comparison exact for those cases.

Synthetic reference comparisons cover complete feature panels, shrinkage and
standard optimized allocations. These are implementation checks, not evidence of
predictive value or achievable investment performance.
