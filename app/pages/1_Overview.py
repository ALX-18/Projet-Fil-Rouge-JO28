from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st
import plotly.express as px

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import aggregate_story_view, apply_global_filters, get_global_filters, load_raw_data
from src.storytelling import overview_story
from src.ui import apply_theme
from src.visualization import medals_by_country_chart


def _load_colleague_table(filename: str):
    try:
        from src.app_data import load_colleague_table
        return load_colleague_table(filename)
    except Exception:
        path = ROOT_DIR / "reports" / "colleague_snapshot" / "outputs" / "tables" / filename
        if not path.exists():
            import pandas as pd
            return pd.DataFrame()
        import pandas as pd
        return pd.read_csv(path)

st.set_page_config(page_title="YPerf - Vue d'ensemble", page_icon=":bar_chart:", layout="wide")
apply_theme()

st.title("Vue d'ensemble")

raw = load_raw_data()
filters = get_global_filters(raw)
raw_filtered = apply_global_filters(raw, filters)
filtered = aggregate_story_view(raw_filtered)

c1, c2, c3 = st.columns(3)
c1.metric("Lignes", int(filtered.shape[0]))
c2.metric("Pays", int(filtered["NOC"].nunique()))
c3.metric("Sports", int(filtered["Sport"].nunique()))

st.plotly_chart(medals_by_country_chart(filtered), use_container_width=True)
st.info(overview_story(filtered))

simple_cols = ["Year", "NOC", "Sport", "medals", "medal_points", "athletes", "female_ratio"]
st.dataframe(filtered[simple_cols].sort_values(["Year", "medals"], ascending=[False, False]).head(50), use_container_width=True)

with st.expander("Travail du collegue - tableaux utiles", expanded=False):
    st.caption("Source: reports/colleague_snapshot/outputs/tables (reference EDA).")

    summary = _load_colleague_table("summary.csv")
    country_top = _load_colleague_table("medals_by_country_top.csv")
    recent_top = _load_colleague_table("medals_by_country_recent_top.csv")
    sport_top = _load_colleague_table("medals_by_sport_top.csv")

    c1, c2 = st.columns(2)
    c1.subheader("Resume du dataset")
    c1.dataframe(summary, use_container_width=True)
    c2.subheader("Top pays (historique)")
    c2.dataframe(country_top.head(15), use_container_width=True)

    if not country_top.empty:
        fig_country = px.bar(
            country_top.head(15),
            x="NOC",
            y="size",
            title="Top pays du collegue (comptage lignes)",
            labels={"NOC": "Pays (code)", "size": "Nombre de medailles (lignes)"},
        )
        st.plotly_chart(fig_country, use_container_width=True)

    d1, d2 = st.columns(2)
    d1.subheader("Top pays (editions recentes)")
    d1.dataframe(recent_top.head(15), use_container_width=True)
    d2.subheader("Top sports")
    d2.dataframe(sport_top.head(15), use_container_width=True)
