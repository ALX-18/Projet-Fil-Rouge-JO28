"""Build curated olympics datasets from sport scope mapping."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "olympics_dataset.csv"
MAPPING_PATH = ROOT / "data" / "reference" / "sport_scope_mapping.csv"
CORE_OUT = ROOT / "data" / "processed" / "olympics_dataset_curated_core.csv"
EXT_OUT = ROOT / "data" / "processed" / "olympics_dataset_curated_extended.csv"


def main() -> None:
    raw = pd.read_csv(RAW_PATH, low_memory=False)
    mapping = pd.read_csv(MAPPING_PATH)

    raw["Sport"] = raw["Sport"].astype(str).str.strip()
    mapping["raw_sport"] = mapping["raw_sport"].astype(str).str.strip()

    merged = raw.merge(
        mapping[["raw_sport", "normalized_sport", "decision"]],
        left_on="Sport",
        right_on="raw_sport",
        how="left",
    )
    merged["normalized_sport"] = merged["normalized_sport"].fillna(merged["Sport"])
    merged["decision"] = merged["decision"].fillna("EXCLUDE")

    core = merged[merged["decision"].eq("KEEP")].copy()
    core["Sport"] = core["normalized_sport"]
    core = core.drop(columns=["raw_sport", "normalized_sport", "decision"])

    extended = merged[merged["decision"].isin(["KEEP", "KEEP_REVIEW"])].copy()
    extended["Sport"] = extended["normalized_sport"]
    extended = extended.drop(columns=["raw_sport", "normalized_sport", "decision"])

    CORE_OUT.parent.mkdir(parents=True, exist_ok=True)
    core.to_csv(CORE_OUT, index=False)
    extended.to_csv(EXT_OUT, index=False)

    print("Core dataset:", CORE_OUT)
    print("  rows:", len(core), "sports:", core["Sport"].nunique())
    print("Extended dataset:", EXT_OUT)
    print("  rows:", len(extended), "sports:", extended["Sport"].nunique())


if __name__ == "__main__":
    main()