"""Enrich olympic athlete dataset with cleaned names, age and activity status."""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "olympics_dataset.csv"
OUT_PATH = ROOT / "data" / "processed" / "olympics_dataset_enriched.csv"
OVERRIDES_PATH = ROOT / "data" / "reference" / "name_overrides.csv"
BIO_PATH = ROOT / "data" / "reference" / "athlete_bio_reference.csv"
REVIEW_PATH = ROOT / "data" / "processed" / "names_review_candidates.csv"


def normalize_name(name: str) -> str:
    n = str(name or "").replace("&nbsp", " ").strip()
    n = re.sub(r"\s+", " ", n)

    # "First (-lastname)" -> "First Lastname"
    n = re.sub(r"^(.+?)\s+\(-([^)]+)\)$", r"\1 \2", n)
    # "First (lastname-)" -> "First Lastname"
    n = re.sub(r"^(.+?)\s+\(([^)]+)-\)$", r"\1 \2", n)
    # "(jr) Lastname" -> "Lastname jr"
    n = re.sub(r"^\(([^)]+)\)\s+(.+)$", r"\2 \1", n)

    n = n.replace("  ", " ").strip()
    return n


def load_reference_map(path: Path, key_col: str, val_col: str) -> dict[str, str]:
    if not path.exists():
        return {}
    ref = pd.read_csv(path)
    if key_col not in ref.columns or val_col not in ref.columns:
        return {}
    return dict(zip(ref[key_col].astype(str), ref[val_col].astype(str)))


def main() -> None:
    df = pd.read_csv(RAW_PATH, low_memory=False)

    # Ensure year numeric for downstream logic
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"]).copy()
    df["Year"] = df["Year"].astype(int)

    # 1) Name normalization + overrides
    df["Name_original"] = df["Name"].astype(str)
    df["Name_clean"] = df["Name_original"].map(normalize_name)

    overrides = load_reference_map(OVERRIDES_PATH, "wrong_name", "correct_name")
    if overrides:
        df["Name_clean"] = df["Name_clean"].replace(overrides)

    # 2) Athlete-level temporal features
    athlete_years = (
        df.groupby("player_id", as_index=False)
        .agg(first_year=("Year", "min"), last_year=("Year", "max"), athlete_name=("Name_clean", "first"))
    )

    # 3) Merge known bio references (internet-verified manual list)
    bio = pd.read_csv(BIO_PATH) if BIO_PATH.exists() else pd.DataFrame(columns=["name", "birth_date", "death_date"])
    bio["name"] = bio.get("name", pd.Series(dtype=str)).astype(str)
    athlete_years = athlete_years.merge(bio[[c for c in ["name", "birth_date", "death_date"] if c in bio.columns]], left_on="athlete_name", right_on="name", how="left")
    athlete_years = athlete_years.drop(columns=[c for c in ["name"] if c in athlete_years.columns])

    athlete_years["birth_date"] = pd.to_datetime(athlete_years["birth_date"], errors="coerce")
    athlete_years["death_date"] = pd.to_datetime(athlete_years["death_date"], errors="coerce")

    athlete_years["birth_year"] = athlete_years["birth_date"].dt.year
    athlete_years["death_year"] = athlete_years["death_date"].dt.year

    # 4) Activity status (A active / I inactive)
    # Rule: deceased -> I, else if last participation >= 2020 -> A, else I.
    athlete_years["status"] = "I"
    athlete_years.loc[athlete_years["last_year"] >= 2020, "status"] = "A"
    athlete_years.loc[athlete_years["death_year"].notna(), "status"] = "I"

    # 5) Attach athlete-level info back to event rows
    df = df.merge(
        athlete_years[["player_id", "birth_year", "death_year", "status"]],
        on="player_id",
        how="left",
    )

    df["age_at_games"] = pd.NA
    has_birth = df["birth_year"].notna()
    df.loc[has_birth, "age_at_games"] = (df.loc[has_birth, "Year"] - df.loc[has_birth, "birth_year"]).astype("Int64")

    # Age at death (athlete-level value copied on all rows of that athlete)
    athlete_years["death_age"] = pd.NA
    m = athlete_years["death_year"].notna() & athlete_years["birth_year"].notna()
    athlete_years.loc[m, "death_age"] = (athlete_years.loc[m, "death_year"] - athlete_years.loc[m, "birth_year"]).astype("Int64")
    df = df.merge(athlete_years[["player_id", "death_age"]], on="player_id", how="left")

    # 6) Candidate list for manual internet review
    suspicious = (
        df[["Name_original", "Name_clean", "NOC", "Sport", "Year"]]
        .loc[df["Name_original"].astype(str).str.contains("(", regex=False)]
        .copy()
    )
    review = (
        suspicious.groupby(["Name_original", "Name_clean", "NOC", "Sport"], as_index=False)
        .agg(occurrences=("Year", "count"), first_year=("Year", "min"), last_year=("Year", "max"))
        .sort_values("occurrences", ascending=False)
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    review.to_csv(REVIEW_PATH, index=False)

    print("Enriched dataset written:", OUT_PATH)
    print("Review candidates written:", REVIEW_PATH)
    print("Rows:", len(df), "| Unique athletes:", df["player_id"].nunique())
    print("Known birth_year filled:", int(df["birth_year"].notna().sum()))


if __name__ == "__main__":
    main()