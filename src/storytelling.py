"""Dynamic storytelling text helpers for Streamlit pages."""

from __future__ import annotations

import pandas as pd

from .noc import noc_to_country_name


def overview_story(df: pd.DataFrame) -> str:
    if df.empty:
        return "Aucune donnee pour les filtres choisis."

    by_country = df.groupby("NOC", as_index=False)["medals"].sum().sort_values("medals", ascending=False)
    leader = by_country.iloc[0]

    if df["Year"].nunique() >= 4:
        recent = df[df["Year"] >= max(df["Year"].max() - 12, df["Year"].min())]
        recent_by_country = recent.groupby("NOC", as_index=False)["medals"].sum().sort_values("medals", ascending=False)
        recent_leader = recent_by_country.iloc[0]
        return (
            f"{noc_to_country_name(leader['NOC'])} ({leader['NOC']}) domine l'historique avec {int(leader['medals'])} medailles. "
            f"Sur la periode recente, {noc_to_country_name(recent_leader['NOC'])} ({recent_leader['NOC']}) est en tete. "
            "C'est un pays cle a suivre pour 2028."
        )

    return f"{noc_to_country_name(leader['NOC'])} ({leader['NOC']}) est en tete sur les filtres choisis avec {int(leader['medals'])} medailles."


def prediction_story(pred_country: pd.DataFrame) -> str:
    if pred_country.empty:
        return "Aucune prediction disponible pour les filtres choisis."

    top = pred_country.iloc[0]
    runner = pred_country.iloc[1] if len(pred_country) > 1 else None
    if runner is None:
        return f"Leader projete pour 2028: {top['country_label']} avec environ {top['predicted_medals_2028']:.1f} medailles."

    gap = top["predicted_medals_2028"] - runner["predicted_medals_2028"]
    return f"Leader projete 2028: {top['country_label']} ({top['predicted_medals_2028']:.1f} medailles), avec environ {gap:.1f} medailles d'avance sur {runner['country_label']}."


def model_story(mae_baseline: float, mae_rf: float, rmse_baseline: float, rmse_rf: float) -> str:
    mae_gain = ((mae_baseline - mae_rf) / mae_baseline * 100) if mae_baseline > 0 else 0
    rmse_gain = ((rmse_baseline - rmse_rf) / rmse_baseline * 100) if rmse_baseline > 0 else 0
    if mae_gain >= 0 and rmse_gain >= 0:
        return (
            f"Le modele Random Forest est meilleur que la baseline: {mae_gain:.1f}% de gain en MAE et {rmse_gain:.1f}% en RMSE. "
            "On peut donc le garder pour les previsions."
        )
    return (
        f"La baseline est pour l'instant plus solide (ecart MAE {mae_gain:.1f}%, ecart RMSE {rmse_gain:.1f}% pour RF). "
        "Les variables actuelles favorisent un modele simple. Il faut enrichir les features."
    )
