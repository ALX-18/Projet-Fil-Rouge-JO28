import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


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


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_table(df: pd.DataFrame, out_dir: Path, name: str) -> None:
    path = out_dir / f"{name}.csv"
    df.to_csv(path, index=False)


def plot_barh(series: pd.Series, title: str, out_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    series.sort_values().plot(kind="barh")
    plt.title(title)
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_line(df: pd.DataFrame, x: str, y_cols: list[str], title: str, out_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    for col in y_cols:
        plt.plot(df[x], df[col], label=col)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def filter_season(df: pd.DataFrame, season: str | None) -> pd.DataFrame:
    if not season:
        return df
    if "Season" not in df.columns:
        return df
    season_norm = season.strip().lower()
    return df[df["Season"].astype(str).str.strip().str.lower() == season_norm]


def safe_get_years(df: pd.DataFrame) -> list[int]:
    years = sorted(df["Year"].dropna().unique().tolist())
    return [int(y) for y in years]


def top_n_per_group(df: pd.DataFrame, group_col: str, top_n: int) -> pd.DataFrame:
    df = df.copy()
    df["rank"] = df.groupby(group_col)["size"].rank(method="first", ascending=False)
    df = df[df["rank"] <= top_n].sort_values([group_col, "rank"])
    return df


def run_eda(csv_path: Path, out_dir: Path, top_n: int, recent_n: int, season: str | None) -> None:
    df = prepare_dataset(load_dataset(csv_path))
    df = filter_season(df, season)
    tables_dir = out_dir / "tables"
    figures_dir = out_dir / "figures"
    ensure_dir(out_dir)
    ensure_dir(tables_dir)
    ensure_dir(figures_dir)

    total_rows = pd.DataFrame({
        "metric": ["rows", "unique_athletes", "years", "sports", "events"],
        "value": [
            len(df),
            df["player_id"].nunique(),
            df["Year"].nunique(),
            df["Sport"].nunique(),
            df["Event"].nunique(),
        ],
    })
    save_table(total_rows, tables_dir, "summary")

    medals = df[df["has_medal"]]
    years = safe_get_years(df)
    recent_years = years[-recent_n:] if recent_n and len(years) else years

    medals_by_country = (
        medals.groupby("NOC", as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(top_n)
    )
    save_table(medals_by_country, tables_dir, "medals_by_country_top")
    plot_barh(
        medals_by_country.set_index("NOC")["size"],
        f"Top {top_n} countries by medals",
        figures_dir / "medals_by_country_top.png",
    )

    medals_by_sport = (
        medals.groupby("Sport", as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(top_n)
    )
    save_table(medals_by_sport, tables_dir, "medals_by_sport_top")
    plot_barh(
        medals_by_sport.set_index("Sport")["size"],
        f"Top {top_n} sports by medals",
        figures_dir / "medals_by_sport_top.png",
    )

    medals_by_year = (
        medals.groupby(["Year", "Medal"], as_index=False)
        .size()
        .pivot(index="Year", columns="Medal", values="size")
        .fillna(0)
        .reset_index()
    )
    save_table(medals_by_year, tables_dir, "medals_by_year")
    medal_cols = [c for c in medals_by_year.columns if c != "Year"]
    plot_line(
        medals_by_year,
        "Year",
        medal_cols,
        "Medals by year and type",
        figures_dir / "medals_by_year.png",
    )

    participation_by_sex = (
        df.groupby(["Year", "Sex"], as_index=False)
        .size()
        .pivot(index="Year", columns="Sex", values="size")
        .fillna(0)
        .reset_index()
    )
    for col in ["F", "M"]:
        if col not in participation_by_sex.columns:
            participation_by_sex[col] = 0
    participation_by_sex["total"] = participation_by_sex["F"] + participation_by_sex["M"]
    participation_by_sex["female_share"] = participation_by_sex["F"] / participation_by_sex["total"].replace(0, pd.NA)
    save_table(participation_by_sex, tables_dir, "participation_by_sex")
    sex_cols = [c for c in participation_by_sex.columns if c != "Year"]
    plot_line(
        participation_by_sex,
        "Year",
        sex_cols,
        "Participation by sex over time",
        figures_dir / "participation_by_sex.png",
    )
    save_table(participation_by_sex[["Year", "F", "M", "total", "female_share"]], tables_dir, "participation_by_sex_share")
    plot_line(
        participation_by_sex,
        "Year",
        ["female_share"],
        "Female participation share over time",
        figures_dir / "participation_by_sex_share.png",
    )

    if recent_years:
        medals_recent = medals[medals["Year"].isin(recent_years)]
        medals_by_country_recent = (
            medals_recent.groupby("NOC", as_index=False)
            .size()
            .sort_values("size", ascending=False)
            .head(top_n)
        )
        save_table(medals_by_country_recent, tables_dir, "medals_by_country_recent_top")
        plot_barh(
            medals_by_country_recent.set_index("NOC")["size"],
            f"Top {top_n} countries by medals (recent editions)",
            figures_dir / "medals_by_country_recent_top.png",
        )

    medals_by_sport_country = (
        medals.groupby(["Sport", "NOC"], as_index=False)
        .size()
        .sort_values(["Sport", "size"], ascending=[True, False])
    )
    medals_by_sport_country_top = top_n_per_group(medals_by_sport_country, "Sport", top_n)
    save_table(medals_by_sport_country_top, tables_dir, "medals_by_sport_country_top")

    medals_by_country_sport = (
        medals.groupby(["NOC", "Sport"], as_index=False)
        .size()
        .sort_values(["NOC", "size"], ascending=[True, False])
    )
    medals_by_country_sport_top = top_n_per_group(medals_by_country_sport, "NOC", top_n)
    save_table(medals_by_country_sport_top, tables_dir, "medals_by_country_sport_top")

    focus_sports = ["Athletics", "Swimming"]
    for sport in focus_sports:
        focus = medals[medals["Sport"].astype(str).str.strip().str.lower() == sport.lower()]
        if focus.empty:
            continue
        focus_by_country = (
            focus.groupby("NOC", as_index=False)
            .size()
            .sort_values("size", ascending=False)
            .head(top_n)
        )
        safe_name = sport.lower().replace(" ", "_")
        save_table(focus_by_country, tables_dir, f"focus_{safe_name}_by_country_top")
        plot_barh(
            focus_by_country.set_index("NOC")["size"],
            f"Top {top_n} countries in {sport}",
            figures_dir / f"focus_{safe_name}_by_country_top.png",
        )

        focus_by_year = focus.groupby("Year", as_index=False).size().sort_values("Year")
        save_table(focus_by_year, tables_dir, f"focus_{safe_name}_by_year")
        plot_line(
            focus_by_year,
            "Year",
            ["size"],
            f"{sport} medals over time",
            figures_dir / f"focus_{safe_name}_by_year.png",
        )

    if recent_years:
        pred_years = recent_years[-3:] if len(recent_years) >= 3 else recent_years
        pred_medals = medals[medals["Year"].isin(pred_years)]
        prediction = (
            pred_medals.groupby("NOC", as_index=False)
            .size()
            .assign(recent_years=", ".join(str(y) for y in pred_years))
        )
        prediction["avg_per_edition"] = prediction["size"] / max(len(pred_years), 1)
        prediction = prediction.sort_values("avg_per_edition", ascending=False)
        save_table(prediction, tables_dir, "prediction_2028_baseline")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Basic EDA and plots for the Olympics dataset.")
    p.add_argument("--csv", default="olympics_dataset.csv", help="Path to the CSV file")
    p.add_argument("--out-dir", default="outputs", help="Directory for reports and figures")
    p.add_argument("--top-n", type=int, default=15, help="Top N categories for bar charts")
    p.add_argument("--recent-n", type=int, default=5, help="Number of recent editions to highlight")
    p.add_argument("--season", default=None, help="Filter by season (e.g., Summer)")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    run_eda(Path(args.csv), Path(args.out_dir), args.top_n, args.recent_n, args.season)


if __name__ == "__main__":
    main()
