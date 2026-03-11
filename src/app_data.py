"""Shared Streamlit data layer with caching and filters."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from .config import (
    ANALYTICS_DATA_PATH,
    CURATED_CORE_DATA_PATH,
    METRICS_DIR,
    MODELS_DIR,
    RAW_DATA_PATH,
    SUPERVISED_DATA_PATH,
)
from .data_prep import aggregate_country_year_sport, build_analytics_dataset, clean_olympics_data
from .features import build_feature_frame, build_supervised_dataset
from .noc import format_noc_label
from .pipeline import run_pipeline

COLLEAGUE_TABLES_DIR = Path("reports/colleague_snapshot/outputs/tables")


def preferred_source_path() -> Path:
    """Return preferred source dataset for app/pipeline."""
    return CURATED_CORE_DATA_PATH if Path(CURATED_CORE_DATA_PATH).exists() else RAW_DATA_PATH


@st.cache_data(show_spinner=False)
def load_raw_data() -> pd.DataFrame:
    source_path = preferred_source_path()
    raw = pd.read_csv(source_path, low_memory=False)
    raw = clean_olympics_data(raw)
    raw["is_medal"] = (raw["Medal"] != "None").astype(int)
    return raw


@st.cache_data(show_spinner=False)
def load_analytics_data() -> pd.DataFrame:
    if not Path(ANALYTICS_DATA_PATH).exists():
        analytics = build_analytics_dataset(raw_path=preferred_source_path())
        feature_frame = build_feature_frame(analytics)
        feature_frame.to_csv(ANALYTICS_DATA_PATH, index=False)
    return pd.read_csv(ANALYTICS_DATA_PATH)


@st.cache_data(show_spinner=False)
def load_supervised_data() -> pd.DataFrame:
    if not Path(SUPERVISED_DATA_PATH).exists():
        analytics = build_analytics_dataset(raw_path=preferred_source_path())
        feature_frame = build_feature_frame(analytics)
        supervised = build_supervised_dataset(feature_frame)
        feature_frame.to_csv(ANALYTICS_DATA_PATH, index=False)
        supervised.to_csv(SUPERVISED_DATA_PATH, index=False)
    return pd.read_csv(SUPERVISED_DATA_PATH)


def ensure_pipeline_artifacts(force: bool = False) -> dict:
    metrics_path = Path(METRICS_DIR) / "model_metrics.json"
    baseline_model_path = Path(MODELS_DIR) / "baseline_last_value.pkl"
    rf_model_path = Path(MODELS_DIR) / "random_forest.pkl"

    if force or not metrics_path.exists() or not baseline_model_path.exists() or not rf_model_path.exists():
        return run_pipeline()

    with metrics_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_global_filters(df: pd.DataFrame) -> dict:
    years = sorted(df["Year"].dropna().astype(int).unique().tolist())
    min_year, max_year = int(min(years)), int(max(years))

    noc_values = sorted(df["NOC"].dropna().unique().tolist())
    noc_labels = {noc: format_noc_label(noc) for noc in noc_values}

    with st.sidebar:
        st.subheader("Filtres")
        selected_nocs = st.multiselect(
            "Pays",
            options=noc_values,
            default=noc_values,
            format_func=lambda x: noc_labels.get(x, x),
        )
        sports = sorted(df["Sport"].dropna().unique().tolist())
        selected_sports = st.multiselect("Sports", options=sports, default=sports)
        year_range = st.slider("Periode", min_value=min_year, max_value=max_year, value=(min_year, max_year), step=4)

        sex_options = ["Tous"]
        if "Sex" in df.columns:
            sex_options += sorted(df["Sex"].dropna().unique().tolist())
        selected_sex = st.selectbox("Genre", options=sex_options, index=0)

    return {
        "nocs": selected_nocs,
        "sports": selected_sports,
        "year_min": year_range[0],
        "year_max": year_range[1],
        "sex": selected_sex,
    }


def apply_global_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    filtered = df.copy()
    filtered = filtered[filtered["NOC"].isin(filters["nocs"])]
    filtered = filtered[filtered["Sport"].isin(filters["sports"])]
    filtered = filtered[(filtered["Year"] >= filters["year_min"]) & (filtered["Year"] <= filters["year_max"])]

    if filters.get("sex", "Tous") != "Tous" and "Sex" in filtered.columns:
        filtered = filtered[filtered["Sex"] == filters["sex"]]

    return filtered


def aggregate_story_view(raw_filtered: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw filtered data for storytelling pages."""
    if raw_filtered.empty:
        return pd.DataFrame(
            columns=["Year", "NOC", "Sport", "athletes", "entries", "female_ratio", "male_ratio", "medals", "medal_points"]
        )
    return aggregate_country_year_sport(raw_filtered)


@st.cache_data(show_spinner=False)
def load_colleague_table(filename: str) -> pd.DataFrame:
    path = COLLEAGUE_TABLES_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
