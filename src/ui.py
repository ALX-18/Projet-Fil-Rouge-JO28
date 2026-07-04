"""UI helpers for Streamlit pages: CSS theme + matching Plotly template."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


# Shared palette (kept in sync with app/assets/style.css and .streamlit/config.toml).
PALETTE = [
    "#5b8def",  # azure
    "#22d3a6",  # mint
    "#f4c04e",  # gold
    "#f472b6",  # pink
    "#a78bfa",  # violet
    "#38bdf8",  # sky
    "#fb7185",  # coral
    "#84cc16",  # lime
]

_TEXT = "#dbe4f5"
_MUTED = "#93a4c4"
_GRID = "rgba(255,255,255,0.08)"


def _register_plotly_template() -> None:
    """Register a dark template so Plotly charts blend with the app theme."""
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_TEXT, family="Inter, Segoe UI, system-ui, sans-serif", size=13),
        title=dict(font=dict(color="#f4f7ff", size=18)),
        colorway=PALETTE,
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=_GRID, tickfont=dict(color=_MUTED)),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=_GRID, tickfont=dict(color=_MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_MUTED)),
        colorscale=dict(sequential=[[0, "#12203c"], [0.5, "#2f6df0"], [1, "#7cf4c8"]]),
        margin=dict(t=60, r=20, b=40, l=20),
    )
    pio.templates["yperf"] = tpl
    pio.templates.default = "yperf"
    px.defaults.template = "yperf"
    px.defaults.color_discrete_sequence = PALETTE


def apply_theme() -> None:
    _register_plotly_template()
    css_path = Path(__file__).resolve().parents[1] / "app" / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
