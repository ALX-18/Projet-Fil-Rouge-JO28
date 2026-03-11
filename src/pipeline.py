"""End-to-end training pipeline for YPerf JO28 project."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import ANALYTICS_DATA_PATH, CURATED_CORE_DATA_PATH, METRICS_DIR, RAW_DATA_PATH, SUPERVISED_DATA_PATH
from src.data_prep import build_analytics_dataset
from src.evaluation import evaluate, temporal_backtest, temporal_split
from src.features import build_feature_frame, build_supervised_dataset
from src.model import extract_feature_importance, save_model, train_baseline, train_random_forest


def run_pipeline() -> dict:
    source_path = CURATED_CORE_DATA_PATH if Path(CURATED_CORE_DATA_PATH).exists() else RAW_DATA_PATH
    analytics = build_analytics_dataset(raw_path=source_path)
    feature_frame = build_feature_frame(analytics)
    supervised = build_supervised_dataset(feature_frame)

    Path(ANALYTICS_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    feature_frame.to_csv(ANALYTICS_DATA_PATH, index=False)
    supervised.to_csv(SUPERVISED_DATA_PATH, index=False)

    train_df, valid_df = temporal_split(supervised)

    baseline = train_baseline(train_df)
    rf = train_random_forest(train_df)

    baseline_metrics = evaluate(baseline, valid_df)
    rf_metrics = evaluate(rf, valid_df)

    save_model(baseline)
    save_model(rf)
    importance_df = extract_feature_importance(rf.estimator)

    all_years = sorted(supervised["Year"].unique().tolist())
    test_years = all_years[-2:] if len(all_years) >= 2 else all_years
    backtest_baseline = temporal_backtest(supervised, train_baseline, test_years)
    backtest_rf = temporal_backtest(supervised, train_random_forest, test_years)

    metrics = {
        "data_source": str(source_path),
        "latest_split": {"baseline": baseline_metrics, "random_forest": rf_metrics},
        "backtest": {
            "baseline": backtest_baseline.to_dict(orient="records"),
            "random_forest": backtest_rf.to_dict(orient="records"),
        },
    }

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    (Path(METRICS_DIR) / "model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    importance_df.to_csv(Path(METRICS_DIR) / "rf_feature_importance.csv", index=False)

    return metrics


if __name__ == "__main__":
    results = run_pipeline()
    print(json.dumps(results, indent=2))
