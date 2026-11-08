"""Retrospective, matched-horizon marginal risk diagnostics, never certification.

The caller supplies forecast means and risk in explicit horizon units. Outcomes
are not filled or annualized. Cross-sectional rows and overlapping windows do
not establish independent observations. This module does not estimate a model,
read PIT data, authenticate provenance, or change existing aligned-risk defaults.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import cast

import numpy as np
import pandas as pd

_KEYS = ["symbol", "target_start", "target_end", "unit"]
_FORECAST_COLUMNS = {*_KEYS, "forecast_at", "available_at", "forecast_mean", "liquidity", "regime"}
_OUTCOME_COLUMNS = {*_KEYS, "realized", "available_at", "observation_start", "observation_end"}


@dataclass(frozen=True)
class RiskCalibrationReport:
    rows: pd.DataFrame
    outcomes: pd.DataFrame
    summary: pd.DataFrame
    cohorts: pd.DataFrame
    rank_diagnostics: pd.DataFrame
    as_of: pd.Timestamp
    minimum_observations: int
    sample_status: str
    input_digest: str
    independence_status: str = "unverified"
    effective_independent_observations: None = None
    prediction_intervals: pd.DataFrame | None = None
    exposure_comparison: pd.DataFrame | None = None
    real_calibration: str = "unavailable"
    certified: bool = False
    provenance_status: str = "caller_asserted"
    tail_semantics: str = (
        "absolute residual strictly exceeds two forecast sigmas; no Gaussian claim"
    )


def _clock(value, name):
    try:
        clock = pd.Timestamp(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} requires a timezone-aware timestamp") from exc
    if pd.isna(clock) or clock.tzinfo is None:
        raise ValueError(f"{name} requires a timezone-aware timestamp")
    return clock.tz_convert("UTC")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _unit(value):
    if not _text(value):
        return False
    if value in {"return_fraction", "return_bps"}:
        return True
    return any(
        value.startswith(prefix) and _text(value[len(prefix) :])
        for prefix in ("price_change:", "factor:")
    )


def _number(value, name):
    if value is None or pd.isna(value):
        return np.nan
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} requires finite numeric evidence")
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} requires finite numeric evidence") from exc
    if not np.isfinite(number):
        raise ValueError(f"{name} requires finite numeric evidence")
    return number


def _frame(frame, *, forecast):
    required = _FORECAST_COLUMNS if forecast else _OUTCOME_COLUMNS
    if not required <= set(frame.columns) or not frame.columns.is_unique:
        raise ValueError("missing or duplicate risk evidence columns")
    result = frame.copy(deep=True).reset_index(drop=True)
    if not result.symbol.map(_text).all() or not result.unit.map(_unit).all():
        raise ValueError("explicit symbol and supported horizon unit required")
    clocks = ["target_start", "target_end", "available_at"]
    clocks += ["forecast_at"] if forecast else ["observation_start", "observation_end"]
    for column in clocks:
        result[column] = pd.to_datetime([_clock(v, column) for v in result[column]], utc=True)
    if (result.target_start >= result.target_end).any():
        raise ValueError("positive target interval required")
    key = [*_KEYS, "forecast_at"] if forecast else _KEYS
    if result.duplicated(key).any():
        raise ValueError("duplicate economic risk evidence key")
    return result


def _forecasts(frame):
    reserved = {
        "horizon_ns",
        "issues",
        "paired",
        "predicted_variance",
        "matched_realized",
        "residual",
        "squared_residual",
        "exposure_status",
        "interval_status",
        "interval_covered",
    }
    if reserved & set(frame.columns):
        raise ValueError("forecast contains reserved audit output columns")
    result = _frame(frame, forecast=True)
    if not result.liquidity.map(_text).all() or not result.regime.map(_text).all():
        raise ValueError("explicit liquidity/regime cohort required; use unknown when unavailable")
    for column in ["forecast_mean", "forecast_variance", "forecast_volatility"]:
        values = result[column] if column in result else [None] * len(result)
        result[column] = [_number(v, column) for v in values]
    both = result.forecast_variance.notna() & result.forecast_volatility.notna()
    if both.any():
        raise ValueError("supply only one risk measure per forecast")
    if (result[["forecast_variance", "forecast_volatility"]] < 0).any().any():
        raise ValueError("nonnegative forecast risk required")
    return result


def _outcomes(frame):
    result = _frame(frame, forecast=False)
    result["realized"] = [_number(v, "realized") for v in result.realized]
    if (result.observation_start >= result.observation_end).any():
        raise ValueError("positive observation interval required")
    if (result.available_at < result.observation_end).any():
        raise ValueError("outcome availability precedes observation completion")
    return result


def _forecast_issues(row, as_of):
    checks = [
        (row.forecast_at > as_of, "forecast_after_as_of"),
        (row.available_at > row.forecast_at, "forecast_unavailable_at_decision"),
        (row.forecast_at > row.target_start, "decision_after_target_start"),
        (row.target_end > as_of, "target_incomplete"),
        (pd.isna(row.forecast_mean), "missing_forecast_mean"),
        (
            pd.isna(row.forecast_variance) and pd.isna(row.forecast_volatility),
            "missing_forecast_risk",
        ),
    ]
    return [issue for failed, issue in checks if failed]


def _outcome_issues(row, as_of):
    checks = [
        (row.available_at > as_of, "outcome_unavailable"),
        (row.observation_end < row.target_end, "stale_outcome"),
        (
            row.observation_start != row.target_start or row.observation_end > row.target_end,
            "observation_horizon_mismatch",
        ),
        (pd.isna(row.realized), "missing_realized"),
    ]
    return [issue for failed, issue in checks if failed]


def _key(row):
    return tuple(getattr(row, name) for name in _KEYS)


def _pair_rows(forecasts, outcomes, as_of):
    lookup = {_key(row): row for row in outcomes.itertuples()}
    starts = set(zip(outcomes.symbol, outcomes.target_start, strict=True))
    records, counts = [], dict.fromkeys(lookup, 0)
    for row in forecasts.itertuples(index=False):
        outcome = lookup.get(_key(row))
        issues = _forecast_issues(row, as_of)
        if outcome is None:
            issues.append(
                "incompatible_outcome"
                if (row.symbol, row.target_start) in starts
                else "missing_outcome"
            )
        else:
            counts[_key(row)] += 1
            issues.extend(_outcome_issues(outcome, as_of))
        records.append(
            _comparison(row, outcome, issues, dict(zip(forecasts.columns, row, strict=True)))
        )
    columns = [
        *forecasts.columns,
        "horizon_ns",
        "issues",
        "paired",
        "predicted_variance",
        "matched_realized",
        "residual",
        "squared_residual",
    ]
    rows = pd.DataFrame(records, columns=columns)
    retained = outcomes.copy(deep=True)
    retained["matched_forecasts"] = [counts[_key(r)] for r in outcomes.itertuples()]
    retained["match_status"] = ["matched" if n else "unmatched" for n in retained.matched_forecasts]
    retained["issues"] = [tuple(_outcome_issues(r, as_of)) for r in outcomes.itertuples()]
    return rows, retained


def _comparison(row, outcome, issues, original):
    variance = row.forecast_variance
    if pd.isna(variance) and pd.notna(row.forecast_volatility):
        variance = row.forecast_volatility * row.forecast_volatility
        if variance == 0 and row.forecast_volatility > 0:
            raise ValueError("representable positive variance required; rescale units explicitly")
    residual = outcome.realized - row.forecast_mean if not issues else np.nan
    squared = residual * residual
    if squared == 0 and residual != 0:
        raise ValueError(
            "representable positive squared residual required; rescale units explicitly"
        )
    if not all(pd.isna(v) or np.isfinite(v) for v in [variance, residual, squared]):
        raise ValueError("finite risk calculations required; rescale declared units explicitly")
    return original | {
        "horizon_ns": (row.target_end - row.target_start).value,
        "issues": tuple(issues),
        "paired": not issues,
        "predicted_variance": variance,
        "matched_realized": outcome.realized if outcome is not None else np.nan,
        "residual": residual,
        "squared_residual": squared,
    }


def _interval_counts(paired):
    intervals = paired[["target_start", "target_end"]].drop_duplicates()
    end, nonoverlap = None, 0
    # Earliest-finish greedy scheduling gives the maximum disjoint interval set.
    # Treat [start, end) as half-open. This count does not prove independence.
    for row in intervals.sort_values(["target_end", "target_start"]).itertuples():
        if end is None or row.target_start >= end:
            nonoverlap += 1
            end = row.target_end
    return len(intervals), nonoverlap


def _sample_status(distinct, nonoverlap, minimum):
    if distinct < minimum:
        return "insufficient_target_intervals"
    if nonoverlap < minimum:
        return "insufficient_nonoverlapping_intervals"
    return "descriptive_only_independence_unverified"


def _statistics(frame, minimum):
    paired = frame.loc[frame.paired.astype(bool)]
    tails = paired.loc[paired.predicted_variance > 0]
    n, nt = len(paired), len(tails)
    predicted = _finite_mean(paired.predicted_variance) if n else None
    realized = _finite_mean(paired.squared_residual) if n else None
    count = (
        int((tails.residual.abs() > 2 * np.sqrt(tails.predicted_variance)).sum()) if nt else None
    )
    distinct, nonoverlap = _interval_counts(paired)
    ratio = realized / predicted if predicted is not None and predicted > 0 else None
    if ratio == 0 and realized is not None and realized > 0:
        raise ValueError("representable positive variance ratio required; rescale units explicitly")
    if ratio is not None and not np.isfinite(ratio):
        raise ValueError("finite variance ratio required; rescale declared units explicitly")
    return {
        "exposure_observations": int((frame.exposure_status == "descriptive").sum()),
        **_interval_statistics(frame),
        "forecasts": len(frame),
        "paired_observations": n,
        "coverage": n / len(frame) if len(frame) else None,
        "predicted_variance": predicted,
        "realized_squared_residual": realized,
        "variance_ratio": ratio,
        "tail_observations": nt,
        "two_sigma_exceedances": count,
        "two_sigma_rate": count / nt if count is not None and nt else None,
        "zero_variance_nonzero_residuals": int(
            ((paired.predicted_variance == 0) & (paired.residual != 0)).sum()
        ),
        "distinct_target_intervals": distinct,
        "nonoverlapping_target_intervals": nonoverlap,
        "sample_status": _sample_status(distinct, nonoverlap, minimum),
    }


def _summaries(rows, minimum, *, cohorts=False):
    keys = ["unit", "horizon_ns"] + (["liquidity", "regime"] if cohorts else [])
    records = []
    for key, group in rows.groupby(keys, sort=True, dropna=False):
        records.append(dict(zip(keys, key, strict=True)) | _statistics(group, minimum))
    if not records:
        records.append(dict.fromkeys(keys) | _statistics(rows, minimum))
    return pd.DataFrame(records)


def _matrix(value, labels):
    try:
        matrix = np.asarray(value, dtype=float)
    except (ValueError, TypeError) as exc:
        raise ValueError("finite square covariance evidence required") from exc
    if matrix.shape != (len(labels), len(labels)) or not np.isfinite(matrix).all():
        raise ValueError("finite square covariance evidence required")
    tolerance = np.finfo(float).eps * len(labels) * np.abs(matrix).max() * 10
    if not np.allclose(matrix, matrix.T, rtol=1e-10, atol=tolerance):
        raise ValueError("symmetric covariance evidence required")
    if (
        np.linalg.eigvalsh(matrix).min()
        < -np.finfo(float).eps * len(labels) * np.abs(matrix).max() * 10
    ):
        raise ValueError("positive semidefinite covariance evidence required")
    return int(np.linalg.matrix_rank(matrix))


def _rank(row, as_of):
    base = {name: getattr(row, name) for name in [*_KEYS, "forecast_at"]}
    record = base | {
        "raw_rank": None,
        "shrunk_rank": None,
        "dimension": None,
        "status": "unavailable",
        "source": None,
    }
    raw = getattr(row, "raw_covariance", None)
    if raw is None or (np.isscalar(raw) and pd.isna(raw)):
        return record
    labels = getattr(row, "covariance_labels", None)
    source = getattr(row, "covariance_source", None)
    if (
        not isinstance(labels, (tuple, list))
        or not labels
        or not all(map(_text, labels))
        or len(set(labels)) != len(labels)
        or not _text(source)
    ):
        raise ValueError("covariance labels and source evidence required")
    if getattr(row, "covariance_unit", None) != f"{row.unit}^2":
        raise ValueError("covariance unit mismatch")
    available = _clock(getattr(row, "covariance_available_at", None), "covariance_available_at")
    record.update(source=source, dimension=len(labels))
    if available > min(row.forecast_at, as_of) or row.forecast_at > as_of:
        record["status"] = "unavailable_at_decision"
        return record
    raw_rank = _matrix(raw, labels)
    shrunk = getattr(row, "shrunk_covariance", None)
    shrunk_rank = (
        None
        if shrunk is None or (np.isscalar(shrunk) and pd.isna(shrunk))
        else _matrix(shrunk, labels)
    )
    return record | {
        "raw_rank": raw_rank,
        "shrunk_rank": shrunk_rank,
        "status": "raw_rank_deficient" if raw_rank < len(labels) else "descriptive_matrix_rank",
    }


def audit_risk_calibration(
    forecasts: pd.DataFrame,
    outcomes: pd.DataFrame,
    *,
    as_of,
    minimum_observations: int = 20,
) -> RiskCalibrationReport:
    """Audit explicit means/risk versus matched, completed observed outcomes.

    Summaries are separate for each exact unit and elapsed target duration.
    Forecast counts include unavailable/missing rows; risk and realized moments
    use the same paired denominator. Sigma exceedances use positive-variance
    pairs only. The minimum applies to distinct and nonoverlapping intervals in
    every comparable group, never nominal cross-sectional rows. No interval
    count establishes independence or supplies statistical uncertainty.
    """
    if type(minimum_observations) is not int or minimum_observations <= 0:
        raise ValueError("minimum_observations must be a positive integer")
    clock = _clock(as_of, "as_of")
    f, o = _forecasts(forecasts), _outcomes(outcomes)
    rows, retained = _pair_rows(f, o, clock)
    exposure, intervals = _optional_tables(f, o, clock)
    rows["exposure_status"] = exposure.status
    rows["interval_status"] = intervals.status
    rows["interval_covered"] = intervals.covered
    summary = _summaries(rows, minimum_observations)
    statuses = summary.sample_status.tolist()
    status = next((s for s in statuses if s.startswith("insufficient")), statuses[0])
    digest = hashlib.sha256(
        (
            cast(
                str,
                forecasts.to_json(
                    orient="records", date_format="iso", date_unit="ns", default_handler=str
                ),
            )
            + cast(
                str,
                outcomes.to_json(
                    orient="records", date_format="iso", date_unit="ns", default_handler=str
                ),
            )
        ).encode()
    ).hexdigest()
    ranks = pd.DataFrame(
        [_rank(row, clock) for row in f.itertuples(index=False)],
        columns=[*_KEYS, "forecast_at", "raw_rank", "shrunk_rank", "dimension", "status", "source"],
    )
    return RiskCalibrationReport(
        rows,
        retained,
        summary,
        _summaries(rows, minimum_observations, cohorts=True),
        ranks,
        clock,
        minimum_observations,
        status,
        digest,
        prediction_intervals=intervals
        if "prediction_lower" in f or "prediction_upper" in f
        else None,
        exposure_comparison=exposure if "target_exposure" in f or "actual_exposure" in o else None,
    )


def _optional_clock(row, name):
    value = getattr(row, name, None)
    return None if value is None or pd.isna(value) else _clock(value, name)


def _decision_supported(row, as_of):
    return row.available_at <= row.forecast_at <= min(row.target_start, as_of)


def _exposure_status(forecast, outcome, as_of):
    if outcome is None:
        return "missing_exposure"
    names = ["exposure_unit", "exposure_source"]
    if not all(_text(getattr(row, name, None)) for row in [forecast, outcome] for name in names):
        return "missing_exposure_evidence"
    if forecast.exposure_unit != outcome.exposure_unit:
        return "unit_mismatch"
    target_at = _optional_clock(forecast, "exposure_available_at")
    actual_at = _optional_clock(outcome, "exposure_available_at")
    observed = _optional_clock(outcome, "exposure_observed_at")
    if any(v is None for v in [target_at, actual_at, observed]):
        return "missing_exposure_evidence"
    if not _decision_supported(forecast, as_of) or target_at > min(forecast.forecast_at, as_of):
        return "target_exposure_unavailable"
    if not forecast.target_start <= observed <= forecast.target_end:
        return "exposure_outside_horizon"
    if actual_at > as_of or actual_at < observed:
        return "actual_exposure_unavailable"
    return "descriptive"


def _exposure(forecast, outcome, as_of):
    target = _number(getattr(forecast, "target_exposure", None), "target_exposure")
    actual = _number(getattr(outcome, "actual_exposure", None), "actual_exposure")
    record = {name: getattr(forecast, name) for name in [*_KEYS, "forecast_at"]} | {
        "target_exposure": target,
        "actual_exposure": actual,
        "exposure_unit": getattr(forecast, "exposure_unit", None),
        "status": "missing_exposure",
        "signed_gap": None,
        "absolute_gap": None,
        "target_source": getattr(forecast, "exposure_source", None),
        "actual_source": getattr(outcome, "exposure_source", None),
        "target_available_at": getattr(forecast, "exposure_available_at", None),
        "actual_available_at": getattr(outcome, "exposure_available_at", None),
        "actual_observed_at": getattr(outcome, "exposure_observed_at", None),
    }
    if pd.isna(target) or pd.isna(actual):
        return record
    status = _exposure_status(forecast, outcome, as_of)
    gap = actual - target if status == "descriptive" else None
    if gap is not None and not np.isfinite(gap):
        raise ValueError("finite exposure gap required")
    return record | {
        "status": status,
        "signed_gap": gap,
        "absolute_gap": abs(gap) if gap is not None else None,
    }


def _bound_status(forecast, outcome, as_of):
    if not _text(getattr(forecast, "prediction_source", None)):
        return "missing_bound_evidence"
    available = _optional_clock(forecast, "prediction_available_at")
    if available is None:
        return "missing_bound_evidence"
    if getattr(forecast, "prediction_unit", None) != forecast.unit:
        return "unit_mismatch"
    if not _decision_supported(forecast, as_of) or available > min(forecast.forecast_at, as_of):
        return "bounds_unavailable"
    if outcome is None:
        return "missing_outcome"
    issues = _outcome_issues(outcome, as_of)
    if forecast.target_end > as_of:
        return "target_incomplete"
    return issues[0] if issues else "descriptive"


def _bounds(forecast, outcome, as_of):
    lower = _number(getattr(forecast, "prediction_lower", None), "prediction_lower bound")
    upper = _number(getattr(forecast, "prediction_upper", None), "prediction_upper bound")
    nominal = _number(getattr(forecast, "prediction_nominal_level", None), "nominal level")
    if pd.notna(nominal) and not 0 < nominal < 1:
        raise ValueError("nominal prediction level must lie strictly between zero and one")
    if pd.notna(lower) and pd.notna(upper) and lower > upper:
        raise ValueError("prediction bounds must be ordered")
    record = {name: getattr(forecast, name) for name in [*_KEYS, "forecast_at"]} | {
        "lower": lower,
        "upper": upper,
        "nominal_level": nominal,
        "status": "missing_bounds",
        "covered": None,
        "source": getattr(forecast, "prediction_source", None),
        "available_at": getattr(forecast, "prediction_available_at", None),
        "bound_unit": getattr(forecast, "prediction_unit", None),
    }
    if pd.isna(lower) or pd.isna(upper):
        return record
    status = _bound_status(forecast, outcome, as_of)
    covered = bool(lower <= outcome.realized <= upper) if status == "descriptive" else None
    return record | {"status": status, "covered": covered}


def _optional_tables(forecasts, outcomes, as_of):
    lookup = {_key(row): row for row in outcomes.itertuples()}
    exposure, intervals = [], []
    for row in forecasts.itertuples(index=False):
        outcome = lookup.get(_key(row))
        exposure.append(_exposure(row, outcome, as_of))
        intervals.append(_bounds(row, outcome, as_of))
    # Empty contracts still expose the same table columns for downstream counts.
    exposure_columns = [
        *_KEYS,
        "forecast_at",
        "target_exposure",
        "actual_exposure",
        "exposure_unit",
        "status",
        "signed_gap",
        "absolute_gap",
        "target_source",
        "actual_source",
        "target_available_at",
        "actual_available_at",
        "actual_observed_at",
    ]
    interval_columns = [
        *_KEYS,
        "forecast_at",
        "lower",
        "upper",
        "nominal_level",
        "status",
        "covered",
        "source",
        "available_at",
        "bound_unit",
    ]
    return pd.DataFrame(exposure, columns=exposure_columns), pd.DataFrame(
        intervals, columns=interval_columns
    )


def _interval_statistics(frame):
    supported = frame.loc[frame.interval_status == "descriptive"]
    n = len(supported)
    covered = int(supported.interval_covered.sum()) if n else None
    return {
        "interval_observations": n,
        "interval_covered": covered,
        "interval_coverage": covered / n if covered is not None and n else None,
    }


def _finite_mean(values):
    # Scale nonnegative moments before averaging, avoiding both sum overflow
    # and premature underflow from dividing tiny observations by the count.
    array = values.to_numpy(dtype=float)
    scale = float(np.max(array))
    result = float(np.mean(array / scale) * scale) if scale else 0.0
    if result == 0 and scale > 0:
        raise ValueError("representable positive risk mean required; rescale units explicitly")
    if not np.isfinite(result):
        raise ValueError("finite risk mean required; rescale declared units explicitly")
    return result
