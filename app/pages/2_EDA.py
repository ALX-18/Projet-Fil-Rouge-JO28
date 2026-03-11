import streamlit as st
import plotly.express as px

from src.app_data import aggregate_story_view, apply_global_filters, get_global_filters, load_raw_data
from src.noc import format_noc_label
from src.ui import apply_theme
from src.visualization import (
    female_ratio_chart,
    global_evolution_chart,
    heatmap_country_sport,
    medals_by_sport_stacked_chart,
    multi_country_sport_chart,
)
st.set_page_config(page_title="YPerf - Analyse EDA", page_icon=":microscope:", layout="wide")
apply_theme()

st.title("Analyse des donnees (EDA)")

raw = load_raw_data()
filters = get_global_filters(raw)
raw_filtered = apply_global_filters(raw, filters)
filtered = aggregate_story_view(raw_filtered)

if filtered.empty:
    st.warning("Aucune donnee apres filtres.")
    st.stop()

st.plotly_chart(global_evolution_chart(raw_filtered), use_container_width=True)

st.subheader("Medailles par sport (empilees par type)")
d1, d2 = st.columns(2)
noc_values = sorted(raw_filtered["NOC"].dropna().unique().tolist())
year_values = sorted(raw_filtered["Year"].dropna().astype(int).unique().tolist())

with d1:
    selected_noc = st.selectbox(
        "Pays",
        options=["Tous"] + noc_values,
        index=0,
        format_func=lambda x: "Tous les pays" if x == "Tous" else format_noc_label(x),
    )
with d2:
    selected_year = st.selectbox("Annee", options=["Toutes"] + year_values, index=0)

raw_dist = raw_filtered.copy()
if selected_noc != "Tous":
    raw_dist = raw_dist[raw_dist["NOC"] == selected_noc]
if selected_year != "Toutes":
    raw_dist = raw_dist[raw_dist["Year"] == int(selected_year)]

st.plotly_chart(medals_by_sport_stacked_chart(raw_dist), use_container_width=True)

st.plotly_chart(heatmap_country_sport(filtered), use_container_width=True)
st.plotly_chart(female_ratio_chart(filtered), use_container_width=True)

sports = sorted(filtered["Sport"].unique().tolist())
selected_sport = st.selectbox("Choisir un sport pour comparer les pays", options=sports)
st.plotly_chart(multi_country_sport_chart(filtered, selected_sport), use_container_width=True)

country_dom = (
    filtered.groupby(["NOC", "Sport"], as_index=False)["medals"].sum()
    .sort_values(["NOC", "medals"], ascending=[True, False])
    .groupby("NOC", as_index=False)
    .first()
    .sort_values("medals", ascending=False)
)
country_dom["country_label"] = country_dom["NOC"].map(format_noc_label)
fig_dom = px.bar(
    country_dom.head(20),
    x="country_label",
    y="medals",
    color="Sport",
    title="Sport dominant par pays",
    labels={"country_label": "Pays", "medals": "Nombre de medailles", "Sport": "Sport"},
)
fig_dom.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig_dom, use_container_width=True)

leader = filtered.groupby("NOC", as_index=False)["medals"].sum().sort_values("medals", ascending=False).head(1)
leader_noc = leader.iloc[0]["NOC"]
leader_medals = int(leader.iloc[0]["medals"])
st.info(f"Info rapide: {format_noc_label(leader_noc)} est en tete avec {leader_medals} medailles sur la periode choisie.")
