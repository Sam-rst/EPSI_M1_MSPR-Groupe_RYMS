"""
Utilitaires de validation pour le module Load ETL v3.0.

Valide les données avant insertion dans PostgreSQL pour garantir
l'intégrité et éviter les erreurs de contraintes.

Auteur: @de (Data Engineer)
"""

from typing import List
import pandas as pd
from pathlib import Path


def validate_csv_exists(csv_path: Path) -> bool:
    """Vérifie qu'un fichier CSV existe et est lisible."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier CSV introuvable: {csv_path}")
    if not csv_path.is_file():
        raise ValueError(f"Le chemin n'est pas un fichier: {csv_path}")
    return True


def validate_dataframe_not_empty(df: pd.DataFrame, source: str) -> bool:
    """Vérifie qu'un DataFrame n'est pas vide."""
    if df.empty:
        raise ValueError(f"DataFrame vide pour {source}")
    return True


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: List[str],
    source: str
) -> bool:
    """Vérifie que toutes les colonnes requises sont présentes."""
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {source}: {missing}")
    return True


def validate_no_nulls(
    df: pd.DataFrame,
    columns: List[str],
    source: str
) -> bool:
    """Vérifie qu'il n'y a pas de valeurs NULL dans les colonnes spécifiées."""
    for col in columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            raise ValueError(
                f"Valeurs NULL trouvées dans {source}.{col}: {null_count} lignes"
            )
    return True


def validate_year_range(
    df: pd.DataFrame,
    column: str,
    valid_years: List[int],
    source: str
) -> bool:
    """Vérifie que les années sont dans la plage valide."""
    invalid = df[~df[column].isin(valid_years)]
    if not invalid.empty:
        invalid_years = invalid[column].unique()
        raise ValueError(
            f"Années invalides dans {source}.{column}: {invalid_years.tolist()}"
        )
    return True


def validate_positive_values(
    df: pd.DataFrame,
    columns: List[str],
    source: str,
    allow_zero: bool = True
) -> bool:
    """Vérifie que les valeurs numériques sont positives."""
    for col in columns:
        if allow_zero:
            invalid = df[df[col] < 0]
        else:
            invalid = df[df[col] <= 0]
        if not invalid.empty:
            raise ValueError(
                f"Valeurs négatives trouvées dans {source}.{col}: {len(invalid)} lignes"
            )
    return True


def validate_percentage_range(
    df: pd.DataFrame,
    columns: List[str],
    source: str
) -> bool:
    """Vérifie que les pourcentages sont entre 0 et 100."""
    for col in columns:
        invalid = df[(df[col] < 0) | (df[col] > 100)]
        if not invalid.empty:
            raise ValueError(
                f"Pourcentages hors plage [0, 100] dans {source}.{col}: {len(invalid)} lignes"
            )
    return True


def validate_unique_key(
    df: pd.DataFrame,
    key_columns: List[str],
    source: str
) -> bool:
    """Vérifie qu'il n'y a pas de doublons sur la clé composite."""
    duplicates = df[df.duplicated(subset=key_columns, keep=False)]
    if not duplicates.empty:
        raise ValueError(
            f"Doublons trouvés dans {source} sur {key_columns}: {len(duplicates)} lignes"
        )
    return True


def validate_elections_data(df: pd.DataFrame, source: str) -> bool:
    """Validation spécifique pour les données électorales v3."""
    from ..config import ANNEES_ELECTIONS_VALIDES, TOURS_VALIDES

    required = [
        "annee", "tour", "id_territoire", "type_territoire",
    ]
    validate_required_columns(df, required, source)
    validate_no_nulls(df, ["annee", "tour", "id_territoire"], source)
    validate_year_range(df, "annee", ANNEES_ELECTIONS_VALIDES, source)

    invalid_tours = df[~df["tour"].isin(TOURS_VALIDES)]
    if not invalid_tours.empty:
        raise ValueError(f"Tours invalides dans {source}: {invalid_tours['tour'].unique()}")

    return True


def validate_participation_data(df: pd.DataFrame, source: str) -> bool:
    """Validation spécifique pour les données de participation."""
    from ..config import ANNEES_ELECTIONS_VALIDES, TOURS_VALIDES

    required = [
        "annee", "tour", "id_territoire", "type_territoire",
        "nombre_inscrits", "nombre_abstentions", "nombre_votants",
        "nombre_blancs_nuls", "nombre_exprimes",
    ]
    validate_required_columns(df, required, source)
    validate_no_nulls(df, ["annee", "tour", "id_territoire"], source)
    validate_year_range(df, "annee", ANNEES_ELECTIONS_VALIDES, source)
    validate_positive_values(
        df, ["nombre_inscrits", "nombre_votants", "nombre_exprimes"], source
    )
    return True


def validate_indicateurs_data(df: pd.DataFrame, source: str) -> bool:
    """Validation spécifique pour les données d'indicateurs v3."""
    from ..config import ANNEES_INDICATEURS_VALIDES

    required = ["id_territoire", "code_type", "annee", "valeur_numerique"]
    validate_required_columns(df, required, source)
    validate_no_nulls(df, ["id_territoire", "code_type", "annee"], source)
    validate_year_range(df, "annee", ANNEES_INDICATEURS_VALIDES, source)
    validate_positive_values(df, ["valeur_numerique"], source, allow_zero=True)

    # Clé unique (ajout type_territoire si présent)
    key_cols = ["id_territoire", "code_type", "annee"]
    if "type_territoire" in df.columns:
        key_cols.insert(1, "type_territoire")
    validate_unique_key(df, key_cols, source)

    return True


def validate_geographie_data(df: pd.DataFrame, source: str, id_col: str) -> bool:
    """Validation spécifique pour les données géographiques."""
    validate_dataframe_not_empty(df, source)
    validate_required_columns(df, [id_col], source)
    validate_no_nulls(df, [id_col], source)
    validate_unique_key(df, [id_col], source)
    return True
