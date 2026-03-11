import pandas as pd

from src.features import build_feature_frame, build_supervised_dataset


def test_feature_frame_and_supervised_target():
    df = pd.DataFrame(
        {
            "Year": [2012, 2016, 2020],
            "NOC": ["FRA", "FRA", "FRA"],
            "Sport": ["Swimming", "Swimming", "Swimming"],
            "athletes": [5, 6, 7],
            "entries": [5, 6, 7],
            "medals": [1, 2, 3],
            "medal_points": [3, 6, 9],
            "female_ratio": [0.4, 0.5, 0.5],
            "male_ratio": [0.6, 0.5, 0.5],
        }
    )

    frame = build_feature_frame(df)
    supervised = build_supervised_dataset(frame)

    assert "medals_next_edition" in frame.columns
    assert "medals_next_edition" in supervised.columns
    assert len(frame) == 3
    assert len(supervised) == 2
