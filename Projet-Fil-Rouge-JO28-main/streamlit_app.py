from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("olympics_dataset.csv")


@st.cache_data
def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    return df


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["Name", "Team", "NOC", "Sport", "Event", "City", "Medal", "Season", "Sex"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["has_medal"] = df["Medal"].ne("No medal") & df["Medal"].notna()
    return df


def filter_season(df: pd.DataFrame, season: str | None) -> pd.DataFrame:
    if not season:
        return df
    if "Season" not in df.columns:
        return df
    season_norm = season.strip().lower()
    return df[df["Season"].astype(str).str.strip().str.lower() == season_norm]


def get_recent_years(df: pd.DataFrame, recent_n: int) -> list[int]:
    years = sorted(df["Year"].dropna().unique().tolist())
    years = [int(y) for y in years]
    if recent_n <= 0:
        return years
    return years[-recent_n:]


def main() -> None:
    st.set_page_config(page_title="JO 2028 - Storytelling", layout="wide")
    st.title("JO 2028 - Performances sportives")

    df = prepare_dataset(load_dataset(DATA_PATH))

    st.sidebar.header("Filtres")
    season = st.sidebar.selectbox("Season", ["Summer", "Winter"], index=0)
    top_n = st.sidebar.slider("Top N", min_value=5, max_value=25, value=15, step=1)
    recent_n = st.sidebar.slider("Editions recentes", min_value=3, max_value=10, value=5, step=1)
    focus_sport = st.sidebar.selectbox("Focus sport", ["Athletics", "Swimming"], index=0)

    df = filter_season(df, season)
    medals = df[df["has_medal"]]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lignes", f"{len(df):,}")
    col2.metric("Athletes uniques", f"{df['player_id'].nunique():,}")
    col3.metric("Sports", f"{df['Sport'].nunique():,}")
    col4.metric("Epreuves", f"{df['Event'].nunique():,}")

    st.subheader("Top pays par medailles (historique)")
    top_countries = (
        medals.groupby("NOC", as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(top_n)
    )
    st.dataframe(top_countries, use_container_width=True)
    st.bar_chart(top_countries.set_index("NOC")["size"], height=300)

    st.subheader("Top pays sur editions recentes")
    recent_years = get_recent_years(df, recent_n)
    medals_recent = medals[medals["Year"].isin(recent_years)]
    top_recent = (
        medals_recent.groupby("NOC", as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(top_n)
    )
    st.write(f"Editions: {', '.join(str(y) for y in recent_years)}")
    st.dataframe(top_recent, use_container_width=True)
    st.bar_chart(top_recent.set_index("NOC")["size"], height=300)

    st.subheader("Participation femme/homme")
    participation = (
        df.groupby(["Year", "Sex"], as_index=False)
        .size()
        .pivot(index="Year", columns="Sex", values="size")
        .fillna(0)
        .reset_index()
    )
    for col in ["F", "M"]:
        if col not in participation.columns:
            participation[col] = 0
    participation["total"] = participation["F"] + participation["M"]
    participation["female_share"] = participation["F"] / participation["total"].replace(0, pd.NA)
    st.line_chart(participation.set_index("Year")[["F", "M"]], height=300)
    st.line_chart(participation.set_index("Year")[["female_share"]], height=250)

    st.subheader(f"Focus sport: {focus_sport}")
    focus = medals[medals["Sport"].astype(str).str.strip().str.lower() == focus_sport.lower()]
    focus_by_country = (
        focus.groupby("NOC", as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(top_n)
    )
    focus_by_year = focus.groupby("Year", as_index=False).size().sort_values("Year")
    st.dataframe(focus_by_country, use_container_width=True)
    st.bar_chart(focus_by_country.set_index("NOC")["size"], height=300)
    st.line_chart(focus_by_year.set_index("Year")["size"], height=250)

    st.subheader("Baseline prediction 2028")
    pred_years = recent_years[-3:] if len(recent_years) >= 3 else recent_years
    pred_medals = medals[medals["Year"].isin(pred_years)]
    prediction = (
        pred_medals.groupby("NOC", as_index=False)
        .size()
        .assign(recent_years=", ".join(str(y) for y in pred_years))
    )
    prediction["avg_per_edition"] = prediction["size"] / max(len(pred_years), 1)
    prediction = prediction.sort_values("avg_per_edition", ascending=False).head(top_n)
    st.write(f"Baseline sur {', '.join(str(y) for y in pred_years)}")
    st.dataframe(prediction[["NOC", "avg_per_edition"]], use_container_width=True)


if __name__ == "__main__":
    main()
