"""Optional fitted composition backends. Models never select their own time split."""

from __future__ import annotations

import hashlib
import pickle

import numpy as np
import pandas as pd

from .factor_composition_spec import FactorCompositionSpec


def fit_predict(
    train: pd.DataFrame,
    target: pd.Series | None,
    predict: pd.DataFrame,
    spec: FactorCompositionSpec,
):
    """Return predictions, linear coefficients (if defined), and fit state identity."""
    if spec.method == "pca":
        from sklearn.decomposition import PCA

        model = PCA(n_components=spec.n_components, svd_solver="full")
        model.fit(train)
        components = model.components_.copy()
        for component in components:
            if component[np.argmax(np.abs(component))] < 0:
                component *= -1
        coefficients = components.mean(axis=0)
        scores = (predict.to_numpy() - model.mean_) @ coefficients
        state = {"components": components.tolist(), "mean": model.mean_.tolist()}
    else:
        if target is None:
            raise ValueError("supervised model requires target")
        if spec.method == "ridge":
            from sklearn.linear_model import Ridge

            model = Ridge(alpha=spec.regularization, solver="svd")
        elif spec.method == "pls":
            from sklearn.cross_decomposition import PLSRegression

            model = PLSRegression(n_components=spec.n_components, scale=False)
        else:
            try:
                from lightgbm import LGBMRegressor
            except ImportError as exc:
                raise ImportError(
                    "lightgbm composition requires quant-platform[composition-ml]"
                ) from exc
            # Deliberately bounded defaults; hyperparameter search is Research-owned.
            model = LGBMRegressor(
                n_estimators=50,
                num_leaves=7,
                max_depth=3,
                min_child_samples=5,
                learning_rate=0.05,
                reg_lambda=spec.regularization,
                n_jobs=1,
                random_state=0,
                deterministic=True,
                force_col_wise=True,
                verbosity=-1,
            )
        model.fit(train, target)
        scores = np.asarray(model.predict(predict)).reshape(-1)
        coefficients = (
            np.asarray(model.coef_).reshape(-1)
            if spec.method != "lightgbm"
            else np.full(train.shape[1], np.nan)
        )
        state = model
    digest = hashlib.sha256(pickle.dumps(state, protocol=5)).hexdigest()
    return scores, coefficients, digest
