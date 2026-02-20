# Rapport Storytelling - Sujet 3 (JO 2028)

Ce rapport synthese les resultats de l'EDA pour guider le storytelling.

Perimetre: edition ete (Season=Summer) pour coller a JO 2028.

## KPIs de base

- Lignes: 252565
- Athletes uniques: 235903
- Editions (annees): 31
- Sports: 76
- Epreuves: 1041

Source: outputs/tables/summary.csv

## Top pays par nombre de medailles

Top 15 (extrait):

- USA, GBR, URS, GER, FRA, ITA, AUS, CHN, HUN, SWE, NED, JPN, RUS, CAN, GDR

Fichier: outputs/tables/medals_by_country_top.csv
Graphique: outputs/figures/medals_by_country_top.png

## Domination historique par pays et par sport

Lecture generale:

- Pays dominants (historique): USA, GBR, URS, GER, FRA.
- Sports dominants (historique): Athletics, Swimming, Rowing.

Exemples par sport (top pays):

- Athletics: USA (1190), GBR (393), URS (242).
- Swimming: USA (1206), AUS (505), GER (160).

Fichiers:

- outputs/tables/medals_by_sport_country_top.csv
- outputs/tables/medals_by_country_sport_top.csv
- outputs/tables/focus_athletics_by_country_top.csv
- outputs/tables/focus_swimming_by_country_top.csv

## Editions recentes et comparaison

Editions recentes dans le dataset: 2008, 2012, 2016, 2020, 2024.

Top pays sur ces editions:

- USA (1448), CHN (731), GBR (649), AUS (597), FRA (583).

Fichier: outputs/tables/medals_by_country_recent_top.csv
Graphique: outputs/figures/medals_by_country_recent_top.png

## Top sports par nombre de medailles

Top 15 (extrait):

- Athletics, Swimming, Rowing, Gymnastics, Fencing, Football, Hockey, Wrestling, Shooting, Sailing, Cycling, Handball, Basketball, Water Polo, Canoeing

Fichier: outputs/tables/medals_by_sport_top.csv
Graphique: outputs/figures/medals_by_sport_top.png

## Evolution des medailles dans le temps

Tableau: outputs/tables/medals_by_year.csv
Graphique: outputs/figures/medals_by_year.png

## Participation par sexe dans le temps

Tableau: outputs/tables/participation_by_sex.csv
Graphique: outputs/figures/participation_by_sex.png

Evolution cle:

- 1896: part femmes 0.0%
- 2024: part femmes 49.1%

Fichier: outputs/tables/participation_by_sex_share.csv
Graphique: outputs/figures/participation_by_sex_share.png

## Focus par sport

Athletics:

- Top pays: USA, GBR, URS.
- Tendance recente: 2016=192, 2020=230, 2024=230 medailles.

Swimming:

- Top pays: USA, AUS, GER.
- Tendance recente: 2016=191, 2020=208, 2024=214 medailles.

Fichiers:

- outputs/tables/focus_athletics_by_country_top.csv
- outputs/tables/focus_athletics_by_year.csv
- outputs/tables/focus_swimming_by_country_top.csv
- outputs/tables/focus_swimming_by_year.csv

## Cibles de prediction 2028 (baseline)

Baseline calculee sur les 3 dernieres editions (2016, 2020, 2024).

Top 5 par moyenne par edition:

- USA ~294.3
- GBR ~147.3
- FRA ~141.3
- CHN ~140.7
- GER ~116.0

Fichier: outputs/tables/prediction_2028_baseline.csv

## Prochaines etapes proposees

1. Choisir 1-2 sports a mettre en avant (Athletics, Swimming) pour le storytelling final.
2. Ajouter un focus pays (ex: FRA, USA) et comparer leur dynamique 2008-2024.
3. Construire un tableau final de prediction (top 10) avec un scenario optimiste/pessimiste.
