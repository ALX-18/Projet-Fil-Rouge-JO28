import pandas as pd

from src.data_prep import aggregate_country_year_sport, clean_olympics_data


def test_clean_olympics_data_adds_expected_columns():
    df = pd.DataFrame(
        {
            "Year": [2016, 2016],
            "NOC": ["FRA", "USA"],
            "Sport": ["Swimming", "Athletics"],
            "Sex": ["F", "M"],
            "Medal": ["Gold", None],
            "Season": ["Summer", "Summer"],
        }
    )

    out = clean_olympics_data(df)

    assert "medal_count" in out.columns
    assert "medal_points" in out.columns
    assert out["medal_count"].tolist() == [1, 0]


def test_aggregate_deduplicates_team_medals():
    df = pd.DataFrame(
        {
            "Year": [2020, 2020],
            "NOC": ["USA", "USA"],
            "Sport": ["Basketball", "Basketball"],
            "Event": ["Men Team", "Men Team"],
            "Team": ["United States", "United States"],
            "Sex": ["M", "M"],
            "Name": ["A", "B"],
            "Medal": ["Gold", "Gold"],
        }
    )

    clean = clean_olympics_data(df)
    out = aggregate_country_year_sport(clean)

    assert int(out.iloc[0]["medals"]) == 1
