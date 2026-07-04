# YPerf — Performances sportives pour les JO 2028 (Los Angeles)

Application de **data storytelling** et d'**analytique prédictive** sur les performances
olympiques, réalisée dans le cadre de l'UF « Spécialité IA & Data » (Bachelor 3 Ynov) —
Sujet 3 : *Performances sportives pour les JO 2028 à Los Angeles*.

L'application explore les performances passées des athlètes par **pays, sport et genre**,
et projette les nations à suivre pour les Jeux de **2028**.

---

## 1. Aperçu fonctionnel

| Étape du sujet | Où c'est traité |
|---|---|
| Acquisition & préparation des données | `src/data_prep.py`, notebook `01_data_understanding` |
| Analyse exploratoire (EDA) | `src/visualization.py`, notebooks `01`/`02`, page **EDA** |
| Feature engineering | `src/features.py`, notebook `03_feature_engineering` |
| Modélisation prédictive | `src/model.py`, `src/evaluation.py`, notebook `04_modeling_jo2028` |
| Projections 2028 | `src/predict.py`, page **Predictions 2028** |
| Storytelling / application interactive | `app/` (Streamlit multipage) |

---

## 2. Prérequis

- **Python ≥ 3.10**
- Le dataset brut est déjà versionné dans `data/raw/olympics_dataset.csv` (~27 Mo).

---

## 3. Installation

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> Pour exécuter les notebooks, installer en plus : `pip install jupyter`.

---

## 4. Utilisation

### 4.1 Entraîner les modèles (pipeline complet)
```bash
python -m src.pipeline
```
Produit :
- `data/processed/aggregated_country_year_sport.csv` — agrégat (pays, année, sport)
- `data/processed/analytics_country_year_sport.csv` — agrégat + features temporelles
- `data/processed/supervised_country_year_sport.csv` — jeu supervisé (cible incluse)
- `models/baseline_last_value.pkl`, `models/random_forest.pkl`
- `reports/metrics/model_metrics.json` — MAE/RMSE + backtest
- `reports/metrics/rf_feature_importance.csv`

> Le premier lancement de l'application déclenche automatiquement ce pipeline s'il manque
> des artefacts (voir `src/app_data.py::ensure_pipeline_artifacts`).

### 4.2 Lancer l'application
```bash
python -m streamlit run app/streamlit_app.py
```
L'app s'ouvre sur `http://localhost:8501`.

### 4.3 Exécuter les notebooks (démarche détaillée)
```bash
jupyter notebook   # puis ouvrir notebooks/01 → 04 dans l'ordre
```

### 4.4 Tests
```bash
python -m pytest -q
```

---

## 5. Manuel de l'application (page par page)

Un panneau de **filtres globaux** (pays, sports, période, genre) est disponible dans la
barre latérale et s'applique aux pages concernées.

- **Accueil** — KPI globaux et bouton *Recalculer les données et les modèles*.
- **1 · Vue d'ensemble** — synthèse chiffrée et tableaux de référence.
- **2 · EDA** — carte mondiale des médailles, évolution par type de médaille, heatmap
  pays × sport, participation par genre, comparaison multi-pays par sport.
- **3 · Modèles** — métriques baseline vs Random Forest, backtest, importance des variables.
- **4 · Predictions 2028** — médailles projetées par pays pour 2028 (à partir de 2024).
- **5 · Athletes** — top athlètes, palmarès Or/Argent/Bronze, détection des **nouvelles
  générations montantes**, courbe d'évolution par athlète.

---

## 6. Méthodologie de modélisation

- **Granularité** : `(NOC, Year, Sport)`.
- **Features** : lags et moyennes glissantes calculés **uniquement sur le passé**
  (`shift(1)`), donc sans fuite temporelle.
- **Cible** : `medals_next_edition` = médailles de l'édition suivante (`shift(-1)`).
- **Validation temporelle stricte** : entraînement sur `Year < année_de_validation`,
  test sur l'édition suivante (jamais de split aléatoire). Backtest sur les 3 dernières
  éditions pour vérifier la robustesse.
- **Modèles** : baseline *last value* (référence exigeante) vs **Random Forest**
  (one-hot `NOC`/`Sport` + features numériques).

**Limite connue** : le modèle projette une tendance ; il n'anticipe pas les ruptures
(nouveaux sports LA2028, blessures, changements de règlement). Le dataset ne fournit pas
l'âge des athlètes : la détection des jeunes talents s'appuie sur l'**édition de début
olympique** plutôt que sur l'âge.

---

## 7. Structure du projet

```text
app/                 # Application Streamlit
  streamlit_app.py   # point d'entrée
  pages/             # 1_Overview, 2_EDA, 3_Modeles, 4_Predictions_2028, 5_Athletes
src/                 # Code métier (importé par l'app ET les notebooks)
  config.py          # chemins & constantes
  data_prep.py       # nettoyage + agrégation
  features.py        # features temporelles + cible
  model.py           # baseline + Random Forest
  evaluation.py      # split temporel, backtest, métriques
  predict.py         # inférence 2028
  visualization.py   # graphiques Plotly (dont carte choroplèthe)
  noc.py             # NOC → nom pays / code ISO-3
  app_data.py        # couche données Streamlit (cache, filtres)
  storytelling.py, ui.py
  tools/             # scripts d'enrichissement/curation
notebooks/           # 01 understanding · 02 EDA · 03 features · 04 modeling
data/
  raw/               # dataset brut
  processed/         # artefacts générés (git-ignorés)
  reference/         # tables de référence
reports/             # métriques, snapshot EDA collègue
tests/               # tests pytest (data_prep, features, model)
DATA_DICTIONARY.md   # dictionnaire des données
```

---

## 8. Documentation complémentaire

- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) — description des colonnes (brut + dérivées).
