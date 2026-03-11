"""Feature engineering for olympic medal forecasting."""

from __future__ import annotations

import pandas as pd

from .config import TARGET_COL


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag and rolling features at country-sport granularity.

    Features are created using historical order within each (NOC, Sport).
    """
    data = df.copy().sort_values(["NOC", "Sport", "Year"]).reset_index(drop=True)
    grouped = data.groupby(["NOC", "Sport"], group_keys=False)

    data["medals_lag_1"] = grouped["medals"].shift(1).fillna(0)
    data["medals_lag_2"] = grouped["medals"].shift(2).fillna(0)
    data["medals_roll_3"] = grouped["medals"].transform(lambda s: s.shift(1).rolling(window=3, min_periods=1).mean()).fillna(0)

    data["points_lag_1"] = grouped["medal_points"].shift(1).fillna(0)
    data["entries_lag_1"] = grouped["entries"].shift(1).fillna(0)
    data["athletes_lag_1"] = grouped["athletes"].shift(1).fillna(0)
    data["female_ratio_lag_1"] = grouped["female_ratio"].shift(1).fillna(data["female_ratio"].fillna(0))

    return data


def make_supervised_target(df: pd.DataFrame) -> pd.DataFrame:
    """Create next-edition medal target (medals_next_edition)."""
    data = df.copy().sort_values(["NOC", "Sport", "Year"]).reset_index(drop=True)
    data[TARGET_COL] = data.groupby(["NOC", "Sport"], group_keys=False)["medals"].shift(-1)
    data[TARGET_COL] = data[TARGET_COL].astype("float")
    return data


def build_feature_frame(analytics_df: pd.DataFrame) -> pd.DataFrame:
    """Build full feature frame including latest year for inference."""
    featured = add_temporal_features(analytics_df)
    supervised_ready = make_supervised_target(featured)
    return supervised_ready


def build_supervised_dataset(feature_frame: pd.DataFrame) -> pd.DataFrame:
    """Drop rows without next-edition target for model training."""
    return feature_frame.dropna(subset=[TARGET_COL]).reset_index(drop=True)
