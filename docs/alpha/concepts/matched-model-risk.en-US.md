# Matched Model Comparison and Downside-Risk Evidence

Language: English · [简体中文](matched-model-risk.md)

These tools keep model comparison separate from portfolio accounting. They do not implement a trading strategy or certify that caller-supplied data meets point-in-time requirements.

## Chronological matched-model fitting

`alpha_research.matched_rank_models.fit_matched_rank_models` fits registered estimators on the same training rows and feature set. Training rows require `formation_date`, `symbol`, `label_end_date`, and a finite `target`; inference rows must all belong to the requested `decision_date` and contain the same features.

Every training formation date and label maturity date must be strictly earlier than the decision date. The function rejects immature rows rather than silently dropping them. Missing feature values are filled with training-column medians; an all-missing training column uses zero. Inference data uses those same training medians.

By default, numeric targets become percentile ranks within each formation date, using average ranks for ties. `target_transform="identity"` preserves numeric risk targets. Supported estimators are `ridge`, `ridge_scaled`, `random_forest_regressor`, `xgb_regressor`, and `xgb_ranker`. The pairwise ranker requires ranked targets and the `rank:pairwise` objective.

The returned receipt records row count, a hash of the actual training rows, the latest label maturity date, decision date, feature names, imputation medians, target semantics, and resolved model configurations. Matching hashes support controlled comparisons; they do not prove that source features were historically available. Scores are not calibrated expected returns or probabilities.

Callers remain responsible for point-in-time source validity, out-of-sample design, frozen experiment specifications, score-to-weight mapping, and trading-cost evaluation.

## Downside-risk targets and forecast gate

`alpha_research.downside_target.next_close_downside_target` enters at the next close and computes daily downside root-mean-square return over a fixed number of exchange sessions. Positive-return sessions remain in the denominator. Missing or non-positive prices make the target unavailable; the window is not extended and missing returns are not treated as zero. `trailing_downside_rms` provides the corresponding historical control through the decision close. Neither metric is annualized.

`alpha_research.forecast_skill_gate.forecast_skill_gate` compares caller-supplied out-of-fold model predictions and control predictions with mature outcomes. All included formations and labels must mature strictly before the decision date. The fixed heuristic requires at least eight formations, at least 20 matched finite observations per formation, positive mean formation-level MSE improvement, and improvement in at least 60% of formations. It cannot verify that predictions truly came from out-of-fold evaluation. Its Boolean result is neither a probability nor a significance test.

Compare learned risk weights with simple exposure controls. Lower volatility alone does not establish predictive skill. Ex-post volatility-matched comparisons are diagnostic, not executable rules. Portfolio-level evaluation still owns drawdown, time under water, recovery time, turnover, and net return.
