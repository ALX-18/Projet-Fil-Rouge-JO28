# Merge Notes - Colleague Snapshot

Source analyzed: `Projet-Fil-Rouge-JO28-main`
Date: 2026-03-10

## What was imported

- `outputs/tables/*.csv`
- `outputs/figures/*.png`
- `storytelling_report.md`
- `analysis.ipynb`
- `eda_report.py`
- `streamlit_app.py`

Imported location:

- `reports/colleague_snapshot/`

## Compatibility analysis

- Dataset schema is identical to the main environment dataset:
  - columns: `player_id, Name, Sex, Team, NOC, Year, Season, City, Sport, Event, Medal`
  - rows: `252565`
  - year range: `1896-2024`
- Hash differs between files, but structure and cardinality match.

## Decision for merge strategy

Main environment remains the reference implementation.
Colleague artifacts are preserved as supporting storytelling assets and historical EDA outputs.

## Not merged directly into production pipeline

- `prediction_2028_baseline.csv` and related baseline logic in colleague script use raw medal row counting,
  which is less robust than current pipeline target engineering (`medals_next_edition`) and temporal validation.
- Colleague standalone Streamlit app is archived for reference; current modular app remains authoritative.

## Suggested next action

- Compare our current `reports/metrics/*` against `reports/colleague_snapshot/outputs/tables/*`
  to select 5-8 final visuals/tables for jury presentation.