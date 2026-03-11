import pandas as pd

from src.model import train_baseline


def test_train_baseline_runs():
    df = pd.DataFrame(
        {
            "Year": [2012, 2016],
            "NOC": ["FRA", "USA"],
            "Sport": ["Swimming", "Athletics"],
            "athletes": [5, 8],
            "entries": [5, 8],
            "medals": [1, 2],
            "medal_points": [3, 5],
            "female_ratio": [0.4, 0.45],
            "male_ratio": [0.6, 0.55],
            "medals_lag_1": [0, 1],
            "medals_lag_2": [0, 0],
            "medals_roll_3": [0, 1],
            "points_lag_1": [0, 3],
            "entries_lag_1": [0, 5],
            "athletes_lag_1": [0, 5],
            "female_ratio_lag_1": [0.4, 0.4],
            "medals_next_edition": [2, 3],
        }
    )

    model = train_baseline(df)
    assert model.model_name == "baseline_last_value"
