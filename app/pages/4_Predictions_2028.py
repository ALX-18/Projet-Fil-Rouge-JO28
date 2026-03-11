from __future__ import annotations

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import apply_global_filters, ensure_pipeline_artifacts, get_global_filters, load_analytics_data
from src.config import MODELS_DIR
from src.noc import format_noc_label
from src.predict import load_model, predict_next_edition
from src.storytelling import prediction_story
from src.ui import apply_theme

st.set_page_config(page_title="YPerf - Predictions 2028", page_icon=":crystal_ball:", layout="wide")
apply_theme()

st.title("Predictions 2028")

ensure_pipeline_artifacts()
analytics = load_analytics_data()
filters = get_global_filters(analytics)
filtered = apply_global_filters(analytics, filters)

if filtered.empty:
    st.warning("Aucune donnee apres filtres.")
    st.stop()

model_path = Path(MODELS_DIR) / "random_forest.pkl"
if not model_path.exists():
    st.warning("Modele random_forest introuvable. Lance l'entrainement dans la page Modeles.")
    st.stop()

rf_model = load_model(str(model_path))
source_year = int(filtered["Year"].max())
pred_df = predict_next_edition(rf_model, filtered, source_year=source_year)

pred_country = (
    pred_df.groupby("NOC", as_index=False)["predicted_medals_next_edition"]
    .sum()
    .rename(columns={"predicted_medals_next_edition": "predicted_medals_2028"})
    .sort_values("predicted_medals_2028", ascending=False)
)

pred_country["predicted_medals_2028"] = pred_country["predicted_medals_2028"].clip(0, 150)
pred_country["country_label"] = pred_country["NOC"].map(format_noc_label)

st.caption(f"Predictions calculees depuis la derniere edition disponible: {source_year}. Cible: 2028.")

fig = px.bar(
    pred_country.head(20),
    x="country_label",
    y="predicted_medals_2028",
    title="Medailles projetees par pays pour 2028",
    labels={"country_label": "Pays", "predicted_medals_2028": "Medailles projetees"},
)
fig.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(pred_country.head(25), use_container_width=True)
st.info(prediction_story(pred_country))
