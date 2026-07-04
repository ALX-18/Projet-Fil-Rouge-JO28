"""Data preparation utilities for olympics storytelling pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import AGGREGATED_DATA_PATH, RAW_DATA_PATH


MEDAL_POINTS = {"Gold": 3, "Silver": 2, "Bronze": 1}


def load_raw_data(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load raw olympics data."""
    return pd.read_csv(path, low_memory=False)


def clean_olympics_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply core data cleaning steps."""
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]

    required = ["Year", "NOC", "Sport", "Sex", "Medal"]
    for col in required:
        if col not in cleaned.columns:
            raise ValueError(f"Missing required column: {col}")

    # Repair rare malformed rows where columns are shifted by one position.
    if "Unnamed: 11" in cleaned.columns:
        year_num = pd.to_numeric(cleaned["Year"], errors="coerce")
        season_num = pd.to_numeric(cleaned.get("Season"), errors="coerce")
        shift_mask = year_num.isna() & season_num.notna()
        if shift_mask.any():
            cleaned.loc[shift_mask, "Name"] = (
                cleaned.loc[shift_mask, "Name"].astype(str).str.replace("&nbsp", " ", regex=False).str.strip()
                + " "
                + cleaned.loc[shift_mask, "Sex"].astype(str).str.strip()
            )
            cleaned.loc[shift_mask, "Sex"] = cleaned.loc[shift_mask, "Team"]
            cleaned.loc[shift_mask, "Team"] = cleaned.loc[shift_mask, "NOC"]
            cleaned.loc[shift_mask, "NOC"] = cleaned.loc[shift_mask, "Year"]
            cleaned.loc[shift_mask, "Year"] = cleaned.loc[shift_mask, "Season"]
            cleaned.loc[shift_mask, "Season"] = cleaned.loc[shift_mask, "City"]
            cleaned.loc[shift_mask, "City"] = cleaned.loc[shift_mask, "Sport"]
            cleaned.loc[shift_mask, "Sport"] = cleaned.loc[shift_mask, "Event"]
            cleaned.loc[shift_mask, "Event"] = cleaned.loc[shift_mask, "Medal"]
            cleaned.loc[shift_mask, "Medal"] = cleaned.loc[shift_mask, "Unnamed: 11"]

    cleaned = cleaned.dropna(subset=["Year", "NOC", "Sport"])
    cleaned["Year"] = pd.to_numeric(cleaned["Year"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Year"])
    cleaned["Year"] = cleaned["Year"].astype(int)

    if "Season" in cleaned.columns:
        # Keep Summer only for LA 2028 use case.
        cleaned = cleaned[cleaned["Season"].fillna("").str.lower().eq("summer")]

    cleaned["Medal"] = cleaned["Medal"].fillna("None").astype(str).str.strip()
    cleaned["Medal"] = cleaned["Medal"].replace(
        {
            "No medal": "None",
            "no medal": "None",
            "nan": "None",
            "NaN": "None",
            "NA": "None",
            "N/A": "None",
        }
    )
    cleaned["medal_count"] = (cleaned["Medal"] != "None").astype(int)
    cleaned["medal_points"] = cleaned["Medal"].map(MEDAL_POINTS).fillna(0).astype(int)
    if "Unnamed: 11" in cleaned.columns:
        cleaned = cleaned.drop(columns=["Unnamed: 11"])

    return cleaned.reset_index(drop=True)


def aggregate_country_year_sport(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate athlete-level rows to country-year-sport granularity."""
    group_cols = ["Year", "NOC", "Sport"]

    participation = (
        df.groupby(group_cols, as_index=False)
        .agg(
            athletes=("Name", "nunique") if "Name" in df.columns else ("NOC", "size"),
            entries=("NOC", "size"),
            female_ratio=("Sex", lambda s: (s == "F").mean()),
            male_ratio=("Sex", lambda s: (s == "M").mean()),
        )
    )

    dedup_keys = ["Year", "NOC", "Sport", "Event", "Medal"]
    medal_events = df[df["Medal"] != "None"][dedup_keys].drop_duplicates()
    medals = (
        medal_events.groupby(group_cols, as_index=False)
        .size()
        .rename(columns={"size": "medals"})
    )
    medal_points = (
        medal_events.assign(point=medal_events["Medal"].map(MEDAL_POINTS).fillna(0))
        .groupby(group_cols, as_index=False)["point"]
        .sum()
        .rename(columns={"point": "medal_points"})
    )

    aggregated = (
        participation.merge(medals, on=group_cols, how="left")
        .merge(medal_points, on=group_cols, how="left")
        .fillna({"medals": 0, "medal_points": 0})
        .sort_values(group_cols)
        .reset_index(drop=True)
    )

    aggregated["medals"] = aggregated["medals"].astype(int)
    aggregated["medal_points"] = aggregated["medal_points"].astype(int)
    return aggregated


def build_analytics_dataset(raw_path: Path | str = RAW_DATA_PATH, out_path: Path | str = AGGREGATED_DATA_PATH) -> pd.DataFrame:
    """Build aggregated dataset at (NOC, Year, Sport) granularity, without features.

    Written to AGGREGATED_DATA_PATH so it never clobbers the feature frame stored at
    ANALYTICS_DATA_PATH (which the app and prediction code rely on).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    raw = load_raw_data(raw_path)
    clean = clean_olympics_data(raw)
    analytics = aggregate_country_year_sport(clean)
    analytics.to_csv(out_path, index=False)
    return analytics
