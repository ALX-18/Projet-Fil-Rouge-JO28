"""Visualization helpers for Streamlit/Plotly."""

from __future__ import annotations

import pandas as pd
import plotly.express as px


def medals_by_country_chart(df: pd.DataFrame):
    agg = df.groupby("NOC", as_index=False)["medals"].sum().sort_values("medals", ascending=False).head(15)
    return px.bar(
        agg,
        x="NOC",
        y="medals",
        title="Top 15 pays par medailles",
        labels={"NOC": "Pays (code)", "medals": "Nombre de medailles"},
    )


def medals_trend_chart(df: pd.DataFrame, noc: str):
    trend = (
        df[df["NOC"] == noc]
        .groupby("Year", as_index=False)["medals"]
        .sum()
        .sort_values("Year")
    )
    return px.line(
        trend,
        x="Year",
        y="medals",
        markers=True,
        title=f"Evolution des medailles - {noc}",
        labels={"Year": "Annee", "medals": "Nombre de medailles"},
    )


def feature_importance_chart(importance_df: pd.DataFrame):
    return px.bar(
        importance_df.sort_values("importance", ascending=True).tail(20),
        x="importance",
        y="feature",
        orientation="h",
        title="Importance des variables (Random Forest)",
        labels={"importance": "Importance", "feature": "Variable"},
    )


def heatmap_country_sport(df: pd.DataFrame):
    top_countries = df.groupby("NOC", as_index=False)["medals"].sum().nlargest(12, "medals")["NOC"]
    top_sports = df.groupby("Sport", as_index=False)["medals"].sum().nlargest(12, "medals")["Sport"]
    piv = (
        df[df["NOC"].isin(top_countries) & df["Sport"].isin(top_sports)]
        .pivot_table(index="NOC", columns="Sport", values="medals", aggfunc="sum", fill_value=0)
    )
    fig = px.imshow(piv, aspect="auto", title="Heatmap medailles : pays x sport")
    fig.update_xaxes(title="Sport")
    fig.update_yaxes(title="Pays (code)")
    return fig


def distribution_medals_chart(
    df: pd.DataFrame,
    split_by: str = "Sport",
    top_n: int = 8,
    include_zero: bool = False,
    max_medals: int | None = None,
    bin_size: int = 1,
    show_percent: bool = False,
):
    work = df.copy()
    if work.empty:
        return px.histogram(title="Distribution des medailles")

    if not include_zero:
        work = work[work["medals"] > 0]

    if max_medals is not None:
        work = work[work["medals"] <= max_medals]

    split_map = {"Aucun": None, "Sport": "Sport", "Pays": "NOC", "Annee": "Year"}
    split_col = split_map.get(split_by, "Sport")

    if split_col == "Sport":
        top_values = (
            work.groupby("Sport", as_index=False)["medals"]
            .sum()
            .nlargest(top_n, "medals")["Sport"]
            .tolist()
        )
        work = work[work["Sport"].isin(top_values)]
    elif split_col == "NOC":
        top_values = (
            work.groupby("NOC", as_index=False)["medals"]
            .sum()
            .nlargest(top_n, "medals")["NOC"]
            .tolist()
        )
        work = work[work["NOC"].isin(top_values)]
    elif split_col == "Year":
        year_values = sorted(work["Year"].dropna().astype(int).unique().tolist())
        selected_years = year_values[-top_n:] if len(year_values) > top_n else year_values
        work = work[work["Year"].isin(selected_years)]

    if work.empty:
        return px.histogram(title="Distribution des medailles (aucune donnee avec ces filtres)")

    medals_max = int(work["medals"].max())
    if max_medals is not None:
        medals_max = min(medals_max, int(max_medals))
    start = 0 if include_zero else 1
    bins = max(5, int((medals_max - start + 1) / max(bin_size, 1)))

    fig = px.histogram(
        work,
        x="medals",
        color=split_col,
        nbins=bins,
        barmode="group",
        histnorm="percent" if show_percent else None,
        title="Distribution des medailles par (pays, sport, annee)",
        labels={
            "medals": "Medailles sur une edition",
            "count": "Nombre de cas",
            "percent": "Part (%)",
            "NOC": "Pays",
            "Sport": "Sport",
            "Year": "Annee",
        },
    )
    fig.update_layout(
        legend_title_text=split_by if split_col else "",
        bargap=0.06,
    )
    return fig


def medals_by_sport_stacked_chart(raw_df: pd.DataFrame):
    work = raw_df.copy()
    work = work[work["Medal"].isin(["Gold", "Silver", "Bronze"])]
    if work.empty:
        return px.bar(title="Medailles par sport et type (aucune donnee)")

    agg = (
        work.groupby(["Sport", "Medal"], as_index=False)
        .size()
        .rename(columns={"size": "medals_count"})
    )
    sport_order = (
        agg.groupby("Sport", as_index=False)["medals_count"]
        .sum()
        .sort_values("medals_count", ascending=False)["Sport"]
        .tolist()
    )

    medal_order = ["Gold", "Silver", "Bronze"]
    color_map = {"Gold": "#D4AF37", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}
    label_map = {"Gold": "Or", "Silver": "Argent", "Bronze": "Bronze"}
    agg["Medal_fr"] = agg["Medal"].map(label_map)

    fig = px.bar(
        agg,
        x="Sport",
        y="medals_count",
        color="Medal_fr",
        barmode="stack",
        title="Nombre de medailles par sport (empile Or/Argent/Bronze)",
        labels={"Sport": "Sport", "medals_count": "Nombre de medailles", "Medal_fr": "Type de medaille"},
        category_orders={"Medal_fr": [label_map[m] for m in medal_order]},
        color_discrete_map={
            "Or": color_map["Gold"],
            "Argent": color_map["Silver"],
            "Bronze": color_map["Bronze"],
        },
    )
    fig.update_layout(xaxis_tickangle=-35)
    fig.update_xaxes(categoryorder="array", categoryarray=sport_order)
    return fig


def global_evolution_chart(df: pd.DataFrame):
    if "Medal" in df.columns:
        work = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()
        yearly = (
            work.groupby(["Year", "Medal"], as_index=False)
            .size()
            .rename(columns={"size": "medals_count"})
        )
        label_map = {"Gold": "Or", "Silver": "Argent", "Bronze": "Bronze"}
        yearly["Type de medaille"] = yearly["Medal"].map(label_map)

        fig = px.line(
            yearly,
            x="Year",
            y="medals_count",
            color="Type de medaille",
            markers=True,
            title="Evolution globale des medailles par type",
            labels={"Year": "Annee", "medals_count": "Nombre de medailles"},
            color_discrete_map={"Or": "#D4AF37", "Argent": "#C0C0C0", "Bronze": "#CD7F32"},
            category_orders={"Type de medaille": ["Or", "Argent", "Bronze"]},
        )
        return fig

    yearly = df.groupby("Year", as_index=False)["medals"].sum()
    return px.line(
        yearly,
        x="Year",
        y="medals",
        markers=True,
        title="Evolution globale des medailles",
        labels={"Year": "Annee", "medals": "Nombre de medailles"},
    )


def female_ratio_chart(df: pd.DataFrame):
    yearly = df.groupby("Year", as_index=False)["female_ratio"].mean()
    return px.line(
        yearly,
        x="Year",
        y="female_ratio",
        markers=True,
        title="Taux de participation des femmes au cours des annees",
        labels={"Year": "Annee", "female_ratio": "Part des femmes"},
    )


def multi_country_sport_chart(df: pd.DataFrame, sport: str, n_countries: int = 8):
    subset = df[df["Sport"] == sport]
    top = subset.groupby("NOC", as_index=False)["medals"].sum().nlargest(n_countries, "medals")
    trend = subset[subset["NOC"].isin(top["NOC"])]
    trend = trend.groupby(["Year", "NOC"], as_index=False)["medals"].sum()
    return px.line(
        trend,
        x="Year",
        y="medals",
        color="NOC",
        markers=True,
        title=f"Comparaison de plusieurs pays - {sport}",
        labels={"Year": "Annee", "medals": "Nombre de medailles", "NOC": "Pays (code)"},
    )
