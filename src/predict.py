"""Inference helpers for JO 2028 medal projections."""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

from .model import MODEL_FEATURES


def load_model(path: str):
    return joblib.load(path)


def predict_next_edition(model, feature_frame: pd.DataFrame, source_year: int | None = None) -> pd.DataFrame:
    """Predict next edition medals using only latest available year rows."""
    infer_df = feature_frame.copy()
    if source_year is None:
        source_year = int(infer_df["Year"].max())

    infer_df = infer_df[infer_df["Year"] == source_year].copy()
    preds = model.predict(infer_df[MODEL_FEATURES])
    infer_df["predicted_medals_next_edition"] = np.clip(preds, 0, None)
    return infer_df
