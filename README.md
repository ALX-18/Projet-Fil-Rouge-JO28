# YPerf - JO 2028

Professional Data Storytelling + Predictive Analytics platform for olympic performance (Bachelor 3 IA & Data).

## What was fixed in this refactor

- Correct target definition: `medals_next_edition`
- Strict temporal validation: train on years `< valid_year`, test on `valid_year`
- Prediction bug fixed: 2028 projections now use only the latest available edition (2024), not cumulative historical rows
- Medal aggregation corrected: `No medal` values are excluded from target counting
- 2024 visibility fixed across app pages and KPI
- Rich EDA with interactive Plotly charts and dynamic filters
- Added athlete analytics page

## Project structure

```text
app/
  streamlit_app.py
  pages/
    1_Overview.py
    2_EDA.py
    3_Modeles.py
    4_Predictions_2028.py
    5_Athletes.py
src/
  app_data.py
  config.py
  data_prep.py
  evaluation.py
  features.py
  model.py
  noc.py
  pipeline.py
  predict.py
  storytelling.py
  ui.py
  visualization.py
data/
  raw/
  processed/
models/
reports/
tests/
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run pipeline

```bash
python -m src.pipeline
```

Outputs:
- `data/processed/analytics_country_year_sport.csv`
- `data/processed/supervised_country_year_sport.csv`
- `models/baseline_last_value.pkl`
- `models/random_forest.pkl`
- `reports/metrics/model_metrics.json`
- `reports/metrics/rf_feature_importance.csv`

## Run app

```bash
python -m streamlit run app/streamlit_app.py
```

## Tests

```bash
python -m pytest -q
```
