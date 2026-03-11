"""YPerf Streamlit app entrypoint."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import ensure_pipeline_artifacts, load_analytics_data, load_raw_data
from src.ui import apply_theme


st.set_page_config(page_title="YPerf - JO 2028", page_icon=":medal:", layout="wide")
apply_theme()

st.title("YPerf - JO 2028")
st.caption("Plateforme simple pour analyser les performances olympiques et projeter 2028")

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Recalculer les donnees et les modeles", type="primary"):
        metrics = ensure_pipeline_artifacts(force=True)
        st.cache_data.clear()
        st.success("Mise a jour terminee.")
        st.json(metrics.get("latest_split", {}))

with c2:
    st.info("Utilise le menu de gauche: Vue d'ensemble, EDA, Modeles, Predictions 2028, Athletes.")

analytics = load_analytics_data()
raw = load_raw_data()

k1, k2, k3 = st.columns(3)
k1.metric("Lignes", int(raw.shape[0]))
k2.metric("Pays", int(raw["NOC"].nunique()))
k3.metric("Sports", int(raw["Sport"].nunique()))

story_cols = ["Year", "NOC", "Sport", "athletes", "entries", "medals", "medal_points", "female_ratio"]
view_df = analytics[story_cols].sort_values(["Year", "medals"], ascending=[False, False]).head(40)
st.subheader("Vue simple des donnees")
st.dataframe(view_df, use_container_width=True)
