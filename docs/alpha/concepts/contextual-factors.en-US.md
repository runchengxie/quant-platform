# Contextual research features

Language: English · [简体中文](contextual-factors.md)

`alpha_research.contextual` turns point-in-time (PIT) inputs into context states, company exposures, and `context × exposure` features. Data collection, revisions, publication times, and source vintages belong to `quant-market-data-platform`; this package does not fetch data or choose providers.

Existing rankers use these columns only when a research configuration explicitly selects them. The module adds no model type and does not change a default feature set.

## Context transforms

`ContextTransformSpec` defines one output column. Supported transforms are `level`, `change_1p`, `change_np`, `yoy`, `rolling_zscore`, `acceleration`, and `rolling_percentile`.

```python
from alpha_research import ContextTransformSpec, build_context_features

spec = ContextTransformSpec(
    series_id="rates.shibor_3m",
    transform="change_np",
    window=20,
    minimum_history=21,
    feature_name="ctx__shibor_3m_change20",
)
features = build_context_features(context_pit, [spec])
```

Before calling the builder, select the PIT revision. It requires at most one row per `series_id` and `period_end`; it does not choose which revision was visible. `yoy` is the arithmetic difference from the matching period one year earlier, not a percentage change. Missing history stays missing; it is not filled with zero.

## Company exposures

`ExposureSpec` combines an industry prior with optional financial modifiers. Modifiers are normalized within each `trade_date`, using `rank_pct` or `zscore_clip`. Missing modifiers and unknown industries require explicit policies. The result is clipped to the spec's bounds, which default to `[-1, 1]`.

```python
from alpha_research import ExposureSpec, FundamentalModifier, build_company_exposures

spec = ExposureSpec(
    name="rate_sensitivity",
    industry_prior_map={"Banks": 0.35, "Real estate": -0.80},
    fundamental_modifiers=(
        FundamentalModifier(
            field="leverage",
            direction=-1.0,
            weight=0.25,
            normalization="rank_pct",
            missing="ignore_modifier",
        ),
    ),
    unknown_industry="zero_prior",
    version="rate.v1",
)
exposures = build_company_exposures(stock_pit_frame, [spec])
```

The built-in industry priors cover rate, credit, industrial activity, energy input, and energy output sensitivities. They are versioned research assumptions at the industry level, not measured facts about each company. More detailed exposures need PIT-valid business mix or other evidence.

## Point-in-time joins and interactions

`attach_context_as_of` uses a backward as-of join. A context observation is visible no earlier than the later of `available_at` and `source_retrieved_at`. This prevents a historical page collected later from leaking into earlier stock rows. The join adds period, availability, retrieval, and age columns. Pass a limit through `series_age_limits` to null an over-age feature without dropping the stock row; `build_context_features` itself does not apply this freshness limit.

```python
from alpha_research import attach_context_as_of

stock_with_context = attach_context_as_of(
    stock_frame,
    context_features,
    feature_names=["ctx__shibor_3m_change20"],
    series_age_limits={"ctx__shibor_3m_change20": 10},
)
```

`build_context_interactions` matches exposure by `(trade_date, symbol, exposure_name)`; it does not fill a current exposure backward. The interaction is the context value multiplied by the matched company exposure. If either input is missing, the result remains missing.

```python
from alpha_research import ContextInteractionSpec, build_context_interactions

interaction = ContextInteractionSpec(
    context_feature="ctx__shibor_3m_change20",
    exposure_name="rate_sensitivity",
    output_name="ctx__shibor_3m_change20__x__rate_sensitivity",
)
feature_frame = build_context_interactions(
    stock_frame,
    context_features,
    exposures,
    [interaction],
)
```

## Reproducibility and research limits

`contextual_feature_set_id` returns a stable SHA-256 identity for the transform, exposure, and interaction specs. Mapping insertion order does not affect it; changes to windows, priors, versions, or interaction semantics do. Bump `ExposureSpec.version` when changing a prior or modifier assumption.

Before treating a feature as evidence, follow the research protocol for PIT universe and revision status, walk-forward evaluation, CPCV/PBO where applicable, ablation, final OOS, costs, turnover, and regime stability. A context value shared by all stocks describes the market regime; `context × exposure` is what creates cross-sectional differences. Evaluate those contributions separately.
