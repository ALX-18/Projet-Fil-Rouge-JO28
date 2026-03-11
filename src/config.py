from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "olympics_dataset.csv"
CURATED_CORE_DATA_PATH = DATA_DIR / "processed" / "olympics_dataset_curated_core.csv"
CURATED_EXTENDED_DATA_PATH = DATA_DIR / "processed" / "olympics_dataset_curated_extended.csv"
ANALYTICS_DATA_PATH = DATA_DIR / "processed" / "analytics_country_year_sport.csv"
SUPERVISED_DATA_PATH = DATA_DIR / "processed" / "supervised_country_year_sport.csv"
# Backward-compatible aliases for older imports.
PROCESSED_DATA_PATH = ANALYTICS_DATA_PATH

MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
METRICS_DIR = REPORTS_DIR / "metrics"
FIGURES_DIR = REPORTS_DIR / "figures"

TARGET_COL = "medals_next_edition"
RANDOM_STATE = 42
