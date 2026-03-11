"""Model training utilities for baseline and random forest."""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .config import MODELS_DIR, RANDOM_STATE, TARGET_COL


FEATURES_NUM = [
    "Year",
    "athletes",
    "entries",
    "medals",
    "medal_points",
    "female_ratio",
    "male_ratio",
    "medals_lag_1",
    "medals_lag_2",
    "medals_roll_3",
    "points_lag_1",
    "entries_lag_1",
    "athletes_lag_1",
    "female_ratio_lag_1",
]
FEATURES_CAT = ["NOC", "Sport"]
MODEL_FEATURES = FEATURES_CAT + FEATURES_NUM


class LastValueBaselineRegressor:
    """Baseline using last observed medals as next-edition prediction."""

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.fitted_ = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if "medals" not in X.columns:
            raise ValueError("Baseline requires 'medals' column.")
        return X["medals"].to_numpy(dtype=float)


@dataclass
class TrainResult:
    model_name: str
    estimator: object


def _build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
            ("num", "passthrough", FEATURES_NUM),
        ]
    )


def train_baseline(df: pd.DataFrame) -> TrainResult:
    X = df[MODEL_FEATURES]
    y = df[TARGET_COL]
    baseline = LastValueBaselineRegressor().fit(X, y)
    return TrainResult(model_name="baseline_last_value", estimator=baseline)


def train_random_forest(df: pd.DataFrame) -> TrainResult:
    X = df[MODEL_FEATURES]
    y = df[TARGET_COL]

    rf = Pipeline(
        steps=[
            ("preprocessor", _build_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=120,
                    max_depth=12,
                    min_samples_leaf=3,
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )
    rf.fit(X, y)
    return TrainResult(model_name="random_forest", estimator=rf)


def save_model(train_result: TrainResult) -> str:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MODELS_DIR / f"{train_result.model_name}.pkl"
    joblib.dump(train_result.estimator, out_path)
    return str(out_path)


def extract_feature_importance(rf_pipeline: Pipeline) -> pd.DataFrame:
    """Extract feature importances from fitted RF pipeline."""
    pre = rf_pipeline.named_steps["preprocessor"]
    model = rf_pipeline.named_steps["model"]

    cat_features = pre.named_transformers_["cat"].get_feature_names_out(FEATURES_CAT).tolist()
    num_features = FEATURES_NUM
    all_features = cat_features + num_features
    importances = model.feature_importances_

    return (
        pd.DataFrame({"feature": all_features, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
