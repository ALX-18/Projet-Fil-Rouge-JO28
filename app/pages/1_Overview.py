from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import aggregate_story_view, apply_global_filters, get_global_filters, load_raw_data
from src.noc import format_noc_label
from src.storytelling import overview_story
from src.ui import apply_theme
from src.visualization import medals_by_country_chart, top_events_chart

st.set_page_config(page_title="YPerf - Vue d'ensemble", page_icon=":bar_chart:", layout="wide")
apply_theme()

st.title("Vue d'ensemble")

raw = load_raw_data()
filters = get_global_filters(raw)
raw_filtered = apply_global_filters(raw, filters)
filtered = aggregate_story_view(raw_filtered)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Lignes agregees", int(filtered.shape[0]))
c2.metric("Pays", int(filtered["NOC"].nunique()))
c3.metric("Sports", int(filtered["Sport"].nunique()))
c4.metric("Epreuves", int(raw_filtered["Event"].nunique()) if "Event" in raw_filtered.columns else 0)

st.plotly_chart(medals_by_country_chart(filtered), use_container_width=True)
st.info(overview_story(filtered))

# --- Tableaux de synthese (calcules sur nos donnees) -------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top pays par medailles")
    top_country = (
        filtered.groupby("NOC", as_index=False)["medals"].sum()
        .sort_values("medals", ascending=False)
        .head(15)
    )
    top_country["Pays"] = top_country["NOC"].map(format_noc_label)
    st.dataframe(
        top_country[["Pays", "medals"]].rename(columns={"medals": "Medailles"}),
        use_container_width=True,
        hide_index=True,
    )

with col_b:
    st.subheader("Top sports par medailles")
    top_sport = (
        filtered.groupby("Sport", as_index=False)["medals"].sum()
        .sort_values("medals", ascending=False)
        .head(15)
        .rename(columns={"medals": "Medailles"})
    )
    st.dataframe(top_sport, use_container_width=True, hide_index=True)

# --- Detail par epreuve pour le sport leader ---------------------------------
if not filtered.empty:
    lead_sport = (
        filtered.groupby("Sport", as_index=False)["medals"].sum()
        .sort_values("medals", ascending=False)
        .iloc[0]["Sport"]
    )
    st.subheader(f"Detail des epreuves du sport le plus medaille : {lead_sport}")
    st.plotly_chart(top_events_chart(raw_filtered, lead_sport), use_container_width=True)

st.subheader("Detail (pays x annee x sport)")
simple_cols = ["Year", "NOC", "Sport", "medals", "medal_points", "athletes", "female_ratio"]
st.dataframe(
    filtered[simple_cols].sort_values(["Year", "medals"], ascending=[False, False]).head(50),
    use_container_width=True,
    hide_index=True,
)
