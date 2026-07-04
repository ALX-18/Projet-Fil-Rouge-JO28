# Dictionnaire des données

## 1. Données brutes — `data/raw/olympics_dataset.csv`

Une ligne = un engagement d'un athlète dans une épreuve d'une édition olympique.

| Colonne | Type | Description |
|---|---|---|
| `player_id` | int | Identifiant de l'athlète |
| `Name` | str | Nom de l'athlète |
| `Sex` | str | Genre (`M` / `F`) |
| `Team` | str | Nom de l'équipe/délégation |
| `NOC` | str | Code pays du Comité National Olympique (code IOC, ex. `USA`, `FRA`, `GER`) |
| `Year` | int | Année de l'édition |
| `Season` | str | Saison (`Summer` / `Winter`) — le projet ne conserve que `Summer` |
| `City` | str | Ville hôte |
| `Sport` | str | Sport (ex. `Athletics`, `Swimming`) |
| `Event` | str | Épreuve précise (ex. `Athletics Men's 100 metres`) |
| `Medal` | str | `Gold`, `Silver`, `Bronze` ou `No medal` |
| `Unnamed: 11` | str | Colonne technique parasite ; sert à réparer de rares lignes décalées puis est supprimée |

**Qualité des données** (traitée dans `src/data_prep.py::clean_olympics_data`) :
- De rares lignes ont leurs colonnes **décalées d'une position** → réparées via `Unnamed: 11`.
- `Medal` est normalisé : `No medal` / `nan` / `NA` → `None`.
- `Year` non numérique → ligne écartée.
- Filtrage `Season == Summer` pour coller au périmètre JO 2028.

---

## 2. Données dérivées — agrégat `(NOC, Year, Sport)`

Fichiers `data/processed/aggregated_*.csv` et `analytics_*.csv`
(`src/data_prep.py`, `src/features.py`).

| Colonne | Type | Description |
|---|---|---|
| `Year`, `NOC`, `Sport` | | Clé d'agrégation |
| `athletes` | int | Nombre d'athlètes uniques |
| `entries` | int | Nombre d'engagements |
| `female_ratio` / `male_ratio` | float | Part de femmes / d'hommes parmi les engagements |
| `medals` | int | Nombre de médailles (épreuves d'équipe dédupliquées) |
| `medal_points` | int | Points pondérés (Or=3, Argent=2, Bronze=1) |

### Features temporelles (fichier `analytics_*` uniquement)

Calculées **par groupe `(NOC, Sport)`** dans l'ordre chronologique, en n'utilisant que le
passé (`shift(1)`) pour éviter toute fuite temporelle.

| Colonne | Description |
|---|---|
| `medals_lag_1`, `medals_lag_2` | Médailles des 1 et 2 éditions précédentes |
| `medals_roll_3` | Moyenne glissante des 3 éditions précédentes |
| `points_lag_1` | Points de l'édition précédente |
| `entries_lag_1`, `athletes_lag_1` | Engagements / athlètes de l'édition précédente |
| `female_ratio_lag_1` | Part de femmes de l'édition précédente |

---

## 3. Jeu supervisé — `data/processed/supervised_country_year_sport.csv`

Identique au fichier `analytics_*` **plus la cible**, et sans les lignes où la cible est
inconnue (dernière édition de chaque groupe).

| Colonne | Type | Description |
|---|---|---|
| `medals_next_edition` | float | **Cible** : nombre de médailles du même `(NOC, Sport)` à l'édition **suivante** |
