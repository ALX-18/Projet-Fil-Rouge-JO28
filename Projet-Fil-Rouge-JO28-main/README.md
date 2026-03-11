# Projet Fil Rouge JO28

## Script de filtrage (Sujet 3)

Un script Python `filter_categories.py` permet de filtrer le dataset olympique (`olympics_dataset.csv`) selon différentes colonnes (Sport, Event, Medal, Year, NOC, Team, Sex...).

### Installation

```bash
pip install -r requirements.txt
```

### Aide

```bash
python filter_categories.py -h
```

### Exemples d'utilisation

1. Lister toutes les colonnes disponibles:
```bash
python filter_categories.py --columns
```

2. Lister les valeurs uniques d'une colonne (ex: Sport):
```bash
python filter_categories.py --unique Sport --limit 20
```

3. Filtrer sur un sport et une médaille:
```bash
python filter_categories.py --filter Sport=Rowing Medal=Gold --show-columns
```

4. Recherche partielle (substring, insensible à la casse):
```bash
python filter_categories.py --filter Event=Butterfly --contains --limit 5
```

5. Filtrer plusieurs valeurs dans une même colonne:
```bash
python filter_categories.py --filter Medal=Gold,Silver Sport=Swimming --limit 10
```

6. Exporter le résultat filtré:
```bash
python filter_categories.py --filter NOC=FRA Medal=Gold --out result_fr_gold.csv
```

### Options principales

- `--csv` : chemin vers le fichier (défaut: olympics_dataset.csv)
- `--filter COL=VAL[,VAL2]` : un ou plusieurs filtres (espaces séparés)
- `--contains` : applique une correspondance partielle (substring)
- `--unique COL` : liste les valeurs uniques d'une colonne
- `--columns` : affiche toutes les colonnes
- `--show-columns` : affiche seulement les colonnes clés
- `--limit N` : limite le nombre de lignes affichées
- `--out fichier.csv` : exporte le résultat filtré

### Notes

- Les valeurs multiples se séparent par des virgules: `Medal=Gold,Silver`
- Avec `--contains`, chaque valeur est cherchée comme fragment: pratique pour `Event`.

Bonne analyse !

## EDA rapide et graphiques

Un script Python `eda_report.py` genere des tableaux CSV et des graphiques pour une exploration rapide du dataset.

### Exemple d'utilisation

```bash
python eda_report.py --csv olympics_dataset.csv --out-dir outputs --top-n 15 --recent-n 5 --season Summer
```

### Fichiers generes

- `outputs/tables/summary.csv`
- `outputs/tables/medals_by_country_top.csv`
- `outputs/tables/medals_by_sport_top.csv`
- `outputs/tables/medals_by_year.csv`
- `outputs/tables/participation_by_sex.csv`
- `outputs/tables/participation_by_sex_share.csv`
- `outputs/tables/medals_by_country_recent_top.csv`
- `outputs/tables/medals_by_sport_country_top.csv`
- `outputs/tables/medals_by_country_sport_top.csv`
- `outputs/tables/focus_athletics_by_country_top.csv`
- `outputs/tables/focus_athletics_by_year.csv`
- `outputs/tables/focus_swimming_by_country_top.csv`
- `outputs/tables/focus_swimming_by_year.csv`
- `outputs/tables/prediction_2028_baseline.csv`
- `outputs/figures/*.png`

## Application Streamlit

Lancer l'application:

```bash
streamlit run streamlit_app.py
```

## Rapport storytelling

Un rapport de synthese est disponible pour guider la suite du projet:

- `storytelling_report.md`

## Sortie des donnees

Les sorties EDA sont rangees dans:

- `outputs/tables/` (CSV)
- `outputs/figures/` (PNG)