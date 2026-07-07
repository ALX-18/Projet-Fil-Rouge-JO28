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
from src.noc import format_noc_label
from src.ui import apply_theme

st.set_page_config(page_title="YPerf - Athletes", page_icon=":running:", layout="wide")
apply_theme()

st.title("Athletes")
st.caption(
    "Analyse au niveau athlete: palmares, nationalite et detection des nouvelles "
    "generations montantes. Le dataset ne fournit pas l'age; la progression des jeunes "
    "est donc estimee a partir de l'edition de debut olympique."
)

raw = load_raw_data()
medaled = raw[raw["is_medal"] == 1].copy()

MEDAL_FR = {"Gold": "Or", "Silver": "Argent", "Bronze": "Bronze"}
MEDAL_COLORS = {"Or": "#D4AF37", "Argent": "#C0C0C0", "Bronze": "#CD7F32"}

# --- 1. Top athletes par nombre de medailles (avec nationalite) --------------
athlete_medals = (
    medaled.groupby("Name", as_index=False)
    .agg(medals=("is_medal", "sum"), NOC=("NOC", lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0]))
    .sort_values("medals", ascending=False)
)
athlete_medals["Pays"] = athlete_medals["NOC"].map(format_noc_label)

st.subheader("Top sportifs par nombre de medailles")
fig_top = px.bar(
    athlete_medals.head(20),
    x="Name",
    y="medals",
    color="Pays",
    title="Top 20 sportifs par medailles (couleur = pays)",
    labels={"Name": "Athlete", "medals": "Nombre de medailles", "Pays": "Pays"},
)
fig_top.update_layout(xaxis_tickangle=-35, showlegend=False)
st.plotly_chart(fig_top, use_container_width=True)

# --- 2. Palmares par type de medaille (remplace l'analyse d'age absente) -----
st.subheader("Palmares detaille du top 15 (Or / Argent / Bronze)")
top15_names = athlete_medals.head(15)["Name"].tolist()
palmares = (
    medaled[medaled["Name"].isin(top15_names) & medaled["Medal"].isin(MEDAL_FR)]
    .groupby(["Name", "Medal"], as_index=False)["is_medal"]
    .sum()
    .rename(columns={"is_medal": "medals"})
)
palmares["Type"] = palmares["Medal"].map(MEDAL_FR)
fig_palmares = px.bar(
    palmares,
    x="Name",
    y="medals",
    color="Type",
    barmode="stack",
    title="Repartition des medailles par type pour les 15 meilleurs athletes",
    labels={"Name": "Athlete", "medals": "Nombre de medailles", "Type": "Type de medaille"},
    category_orders={"Type": ["Or", "Argent", "Bronze"], "Name": top15_names},
    color_discrete_map=MEDAL_COLORS,
)
fig_palmares.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig_palmares, use_container_width=True)

# --- 3. Nouvelles generations montantes (base sur l'edition de debut) --------
st.subheader("Nouvelles generations montantes")
st.caption(
    "Athletes ayant fait leurs debuts olympiques lors des 3 dernieres editions et deja "
    "medailles, tries par nombre de medailles remportees depuis leurs debuts."
)

debut_year = raw.groupby("Name", as_index=False)["Year"].min().rename(columns={"Year": "debut"})
recent_editions = sorted(raw["Year"].unique())[-3:]

rising = (
    medaled.groupby("Name", as_index=False)
    .agg(
        medals=("is_medal", "sum"),
        NOC=("NOC", lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0]),
        derniere_edition=("Year", "max"),
    )
    .merge(debut_year, on="Name", how="left")
)
rising = rising[rising["debut"].isin(recent_editions)].sort_values("medals", ascending=False)
rising["Pays"] = rising["NOC"].map(format_noc_label)

if rising.empty:
    st.info("Aucun nouvel athlete medaille detecte sur les dernieres editions.")
else:
    display_rising = rising.head(20)[["Name", "Pays", "debut", "derniere_edition", "medals"]].rename(
        columns={
            "Name": "Athlete",
            "debut": "Debut JO",
            "derniere_edition": "Derniere edition",
            "medals": "Medailles",
        }
    )
    st.dataframe(display_rising, use_container_width=True, hide_index=True)

# --- 4. Evolution d'un athlete -----------------------------------------------
st.subheader("Evolution d'un athlete")
st.caption(
    "Tape le nom d'un athlete pour le rechercher. La liste couvre les "
    f"{athlete_medals['Name'].nunique():,} athletes ayant remporte au moins une medaille."
)
athlete_year = (
    medaled.groupby(["Name", "Year"], as_index=False)["is_medal"]
    .sum()
    .rename(columns={"is_medal": "medals"})
    .sort_values(["Name", "Year"])
)
# Toute la liste des athletes medailles (triee par palmares), pas seulement le top 100.
athlete_options = athlete_medals["Name"].tolist()
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
