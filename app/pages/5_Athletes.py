from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import load_raw_data
from src.ui import apply_theme

st.set_page_config(page_title="YPerf - Athletes", page_icon=":running:", layout="wide")
apply_theme()

st.title("Athletes")

raw = load_raw_data()

medaled = raw[raw["is_medal"] == 1].copy()

athlete_medals = (
    medaled.groupby("Name", as_index=False)["is_medal"]
    .sum()
    .rename(columns={"is_medal": "medals"})
    .sort_values("medals", ascending=False)
)
st.subheader("Top sportifs par nombre de medailles")
fig_top = px.bar(
    athlete_medals.head(20),
    x="Name",
    y="medals",
    title="Top 20 sportifs par medailles",
    labels={"Name": "Athlete", "medals": "Nombre de medailles"},
)
fig_top.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig_top, use_container_width=True)

if "Age" in raw.columns:
    age_by_sport = raw.dropna(subset=["Age"]).groupby("Sport", as_index=False)["Age"].mean().sort_values("Age", ascending=False)
    st.subheader("Age moyen par sport")
    fig_age = px.bar(
        age_by_sport.head(20),
        x="Sport",
        y="Age",
        title="Age moyen des athletes par sport",
        labels={"Sport": "Sport", "Age": "Age moyen"},
    )
    fig_age.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_age, use_container_width=True)
else:
    st.warning("Impossible de calculer l'age moyen par sport: la colonne 'Age' est absente du dataset.")

athlete_year = (
    medaled.groupby(["Name", "Year"], as_index=False)["is_medal"]
    .sum()
    .rename(columns={"is_medal": "medals"})
    .sort_values(["Name", "Year"])
)
athlete_year["prev_medals"] = athlete_year.groupby("Name")["medals"].shift(1).fillna(0)
athlete_year["progression"] = athlete_year["medals"] - athlete_year["prev_medals"]

young_talents = pd.DataFrame()
if "Age" in medaled.columns:
    young_talents = (
        medaled[medaled["Age"] < 25]
        .groupby(["Name", "Year"], as_index=False)["is_medal"]
        .sum()
        .rename(columns={"is_medal": "medals"})
        .sort_values(["Name", "Year"])
    )
    young_talents["prev_medals"] = young_talents.groupby("Name")["medals"].shift(1).fillna(0)
    young_talents["progression"] = young_talents["medals"] - young_talents["prev_medals"]
    young_talents = young_talents[young_talents["progression"] > 0].sort_values("progression", ascending=False)

st.subheader("Jeunes talents (<25 ans) en progression")
if young_talents.empty:
    st.info("Non disponible avec les colonnes actuelles, ou aucune progression detectee.")
else:
    st.dataframe(young_talents.head(20), use_container_width=True)

st.subheader("Evolution d'un athlete")
athlete_options = athlete_medals.head(100)["Name"].tolist()
selected = st.selectbox("Choisir un athlete", options=athlete_options)
curve = athlete_year[athlete_year["Name"] == selected]
fig_curve = px.line(
    curve,
    x="Year",
    y="medals",
    markers=True,
    title=f"Evolution des medailles - {selected}",
    labels={"Year": "Annee", "medals": "Nombre de medailles"},
)
st.plotly_chart(fig_curve, use_container_width=True)
