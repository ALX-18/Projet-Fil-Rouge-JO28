import argparse
import sys
from pathlib import Path
from typing import List, Dict

try:
    import pandas as pd
except ImportError:
    print("Le module pandas n'est pas installé. Installez-le avec: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

DEFAULT_COLUMNS = ["Sport", "Event", "Medal", "Year", "NOC", "Team", "Sex"]


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        print(f"Fichier introuvable: {csv_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(csv_path)
    return df


def list_columns(df: pd.DataFrame):
    print("Colonnes disponibles:")
    for col in df.columns:
        print(f" - {col}")


def list_unique(df: pd.DataFrame, column: str, limit: int = None):
    if column not in df.columns:
        print(f"Colonne inconnue: {column}", file=sys.stderr)
        sys.exit(1)
    values = df[column].dropna().unique()
    if limit:
        values = values[:limit]
    print(f"Valeurs uniques pour '{column}':")
    for v in values:
        print(f" - {v}")


def parse_filter_expressions(exprs: List[str]) -> Dict[str, List[str]]:
    filters: Dict[str, List[str]] = {}
    for expr in exprs:
        if "=" not in expr:
            print(f"Expression de filtre invalide (manque '='): {expr}", file=sys.stderr)
            sys.exit(1)
        key, raw_val = expr.split("=", 1)
        key = key.strip()
        values = [v.strip() for v in raw_val.split(",") if v.strip()]
        if not values:
            print(f"Aucune valeur pour le filtre: {expr}", file=sys.stderr)
            sys.exit(1)
        filters[key] = values
    return filters


def apply_filters(df: pd.DataFrame, filters: Dict[str, List[str]], contains: bool = False) -> pd.DataFrame:
    for col, values in filters.items():
        if col not in df.columns:
            print(f"Colonne de filtre inconnue: {col}", file=sys.stderr)
            sys.exit(1)
        if contains:
            mask = False
            for v in values:
                mask = mask | df[col].astype(str).str.contains(v, case=False, na=False)
        else:
            mask = df[col].isin(values)
        df = df[mask]
    return df


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Filtrer le dataset Olympique par catégories.")
    p.add_argument("--csv", default="olympics_dataset.csv", help="Chemin vers le fichier CSV")
    p.add_argument("--columns", action="store_true", help="Lister toutes les colonnes")
    p.add_argument("--unique", metavar="COL", help="Lister les valeurs uniques d'une colonne")
    p.add_argument("--limit", type=int, help="Limiter le nombre de lignes ou de valeurs uniques affichées")
    p.add_argument("--filter", nargs="*", metavar="COL=VAL[,VAL2]", help="Filtres de type clé=valeur (plusieurs). Ex: Sport=Swimming Medal=Gold")
    p.add_argument("--contains", action="store_true", help="Utiliser une recherche partielle (substring, insensible à la casse) pour les filtres")
    p.add_argument("--show-columns", action="store_true", help="Afficher uniquement les colonnes pertinentes par défaut")
    p.add_argument("--out", metavar="FICHIER", help="Exporter le résultat filtré en CSV")
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    df = load_dataset(Path(args.csv))

    if args.columns:
        list_columns(df)
        return

    if args.unique:
        list_unique(df, args.unique, args.limit)
        return

    # Construire filtres explicites (paramètres dédiés remplacés par --filter générique)
    filters = parse_filter_expressions(args.filter) if args.filter else {}

    if filters:
        df = apply_filters(df, filters, contains=args.contains)

    if args.show_columns:
        cols = [c for c in DEFAULT_COLUMNS if c in df.columns]
        df = df[cols]

    if args.limit:
        df = df.head(args.limit)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out, index=False)
        print(f"Résultat exporté vers {args.out}")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":  
    main()
