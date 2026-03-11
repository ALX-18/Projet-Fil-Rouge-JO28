"""Evaluation utilities with strict temporal validation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .config import METRICS_DIR, TARGET_COL
from .model import MODEL_FEATURES, TrainResult


def temporal_split(df: pd.DataFrame, valid_year: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train on years < valid_year, validate on year == valid_year."""
    max_year = int(df["Year"].max())
    valid_year = valid_year if valid_year is not None else max_year

    train_df = df[df["Year"] < valid_year].copy()
    valid_df = df[df["Year"] == valid_year].copy()

    if train_df.empty or valid_df.empty:
        raise ValueError("Temporal split failed. Check year coverage in supervised data.")

    return train_df, valid_df


def evaluate(train_result: TrainResult, valid_df: pd.DataFrame) -> dict:
    X_valid = valid_df[MODEL_FEATURES]
    y_valid = valid_df[TARGET_COL]
    preds = np.clip(train_result.estimator.predict(X_valid), 0, None)

    mae = mean_absolute_error(y_valid, preds)
    rmse = float(np.sqrt(mean_squared_error(y_valid, preds)))

    return {
        "model": train_result.model_name,
        "mae": round(float(mae), 4),
        "rmse": round(rmse, 4),
        "n_samples": int(len(valid_df)),
        "valid_year": int(valid_df["Year"].iloc[0]),
    }


def temporal_backtest(df: pd.DataFrame, trainer, test_years: list[int]) -> pd.DataFrame:
    """Run strict backtest across multiple years with rolling train window."""
    rows: list[dict] = []
    for year in sorted(test_years):
        train_df = df[df["Year"] < year]
        valid_df = df[df["Year"] == year]
        if train_df.empty or valid_df.empty:
            continue

        trained = trainer(train_df)
        metrics = evaluate(trained, valid_df)
        rows.append(metrics)

    if not rows:
        return pd.DataFrame(columns=["model", "mae", "rmse", "n_samples", "valid_year"])
    return pd.DataFrame(rows)


def save_metrics(metrics: dict, filename: str = "metrics.json") -> str:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(METRICS_DIR) / filename
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return str(out_path)
