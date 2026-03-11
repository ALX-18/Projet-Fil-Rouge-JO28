from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app_data import ensure_pipeline_artifacts
from src.config import METRICS_DIR, MODELS_DIR
from src.model import extract_feature_importance
from src.predict import load_model
from src.storytelling import model_story
from src.ui import apply_theme
from src.visualization import feature_importance_chart

st.set_page_config(page_title="YPerf - Modeles", page_icon=":robot_face:", layout="wide")
apply_theme()

st.title("Modeles")

if st.button("Entrainer / Mettre a jour", type="primary"):
    metrics = ensure_pipeline_artifacts(force=True)
    st.success("Entrainement termine.")
else:
    metrics_path = Path(METRICS_DIR) / "model_metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    else:
        metrics = ensure_pipeline_artifacts()

latest = metrics.get("latest_split", {})
base = latest.get("baseline", {})
rf = latest.get("random_forest", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("MAE Baseline", base.get("mae", "-"))
c2.metric("MAE RF", rf.get("mae", "-"))
c3.metric("RMSE Baseline", base.get("rmse", "-"))
c4.metric("RMSE RF", rf.get("rmse", "-"))

if base and rf:
    st.info(model_story(float(base["mae"]), float(rf["mae"]), float(base["rmse"]), float(rf["rmse"])))

st.subheader("Validation temporelle")
backtest_base = metrics.get("backtest", {}).get("baseline", [])
backtest_rf = metrics.get("backtest", {}).get("random_forest", [])
col_a, col_b = st.columns(2)
col_a.dataframe(backtest_base, use_container_width=True)
col_b.dataframe(backtest_rf, use_container_width=True)

rf_path = Path(MODELS_DIR) / "random_forest.pkl"
if rf_path.exists():
    rf_model = load_model(str(rf_path))
    importance_df = extract_feature_importance(rf_model)
    st.plotly_chart(feature_importance_chart(importance_df), use_container_width=True)
    st.caption("Ce graphique montre quelles variables influencent le plus la prediction.")
