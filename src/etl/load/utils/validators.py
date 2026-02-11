"""
Utilitaires de validation pour le module Load ETL.

Valide les données avant insertion dans PostgreSQL pour garantir
l'intégrité et éviter les erreurs de contraintes.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path


def validate_csv_exists(csv_path: Path) -> bool:
    """
    Vérifie qu'un fichier CSV existe et est lisible.

    Args:
        csv_path: Chemin vers le fichier CSV

    Returns:
        True si le fichier existe et est lisible

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier CSV introuvable : {csv_path}")

    if not csv_path.is_file():
        raise ValueError(f"Le chemin n'est pas un fichier : {csv_path}")

    return True


def validate_dataframe_not_empty(df: pd.DataFrame, source: str) -> bool:
    """
    Vérifie qu'un DataFrame n'est pas vide.

    Args:
        df: DataFrame à valider
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si le DataFrame contient des données

    Raises:
        ValueError: Si le DataFrame est vide
    """
    if df.empty:
        raise ValueError(f"DataFrame vide pour {source}")

    return True


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: List[str],
    source: str
) -> bool:
    """
    Vérifie que toutes les colonnes requises sont présentes.

    Args:
        df: DataFrame à valider
        required_columns: Liste des colonnes requises
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si toutes les colonnes sont présentes

    Raises:
        ValueError: Si des colonnes sont manquantes
    """
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"Colonnes manquantes dans {source} : {missing}"
        )

    return True


def validate_no_nulls(
    df: pd.DataFrame,
    columns: List[str],
    source: str
) -> bool:
    """
    Vérifie qu'il n'y a pas de valeurs NULL dans les colonnes spécifiées.

    Args:
        df: DataFrame à valider
        columns: Liste des colonnes à vérifier
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si aucune valeur NULL

    Raises:
        ValueError: Si des NULL sont trouvés
    """
    for col in columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            raise ValueError(
                f"Valeurs NULL trouvées dans {source}.{col} : {null_count} lignes"
            )

    return True


def validate_year_range(
    df: pd.DataFrame,
    column: str,
    valid_years: List[int],
    source: str
) -> bool:
    """
    Vérifie que les années sont dans la plage valide.

    Args:
        df: DataFrame à valider
        column: Nom de la colonne année
        valid_years: Liste des années valides
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si toutes les années sont valides

    Raises:
        ValueError: Si des années invalides sont trouvées
    """
    invalid = df[~df[column].isin(valid_years)]

    if not invalid.empty:
        invalid_years = invalid[column].unique()
        raise ValueError(
            f"Années invalides dans {source}.{column} : {invalid_years.tolist()}"
        )

    return True


def validate_positive_values(
    df: pd.DataFrame,
    columns: List[str],
    source: str,
    allow_zero: bool = True
) -> bool:
    """
    Vérifie que les valeurs numériques sont positives.

    Args:
        df: DataFrame à valider
        columns: Liste des colonnes à vérifier
        source: Nom de la source (pour messages d'erreur)
        allow_zero: Si True, autorise la valeur 0

    Returns:
        True si toutes les valeurs sont positives

    Raises:
        ValueError: Si des valeurs négatives sont trouvées
    """
    for col in columns:
        if allow_zero:
            invalid = df[df[col] < 0]
        else:
            invalid = df[df[col] <= 0]

        if not invalid.empty:
            raise ValueError(
                f"Valeurs négatives/nulles trouvées dans {source}.{col} : {len(invalid)} lignes"
            )

    return True


def validate_percentage_range(
    df: pd.DataFrame,
    columns: List[str],
    source: str
) -> bool:
    """
    Vérifie que les pourcentages sont entre 0 et 100.

    Args:
        df: DataFrame à valider
        columns: Liste des colonnes pourcentage
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si tous les pourcentages sont valides

    Raises:
        ValueError: Si des pourcentages hors plage sont trouvés
    """
    for col in columns:
        invalid = df[(df[col] < 0) | (df[col] > 100)]

        if not invalid.empty:
            raise ValueError(
                f"Pourcentages hors plage [0, 100] dans {source}.{col} : {len(invalid)} lignes"
            )

    return True


def validate_unique_key(
    df: pd.DataFrame,
    key_columns: List[str],
    source: str
) -> bool:
    """
    Vérifie qu'il n'y a pas de doublons sur la clé composite.

    Args:
        df: DataFrame à valider
        key_columns: Liste des colonnes formant la clé
        source: Nom de la source (pour messages d'erreur)

    Returns:
        True si aucun doublon

    Raises:
        ValueError: Si des doublons sont trouvés
    """
    duplicates = df[df.duplicated(subset=key_columns, keep=False)]

    if not duplicates.empty:
        raise ValueError(
            f"Doublons trouvés dans {source} sur {key_columns} : {len(duplicates)} lignes"
        )

    return True


def validate_elections_data(df: pd.DataFrame, source: str) -> bool:
    """
    Validation spécifique pour les données électorales.

    Args:
        df: DataFrame à valider
        source: Nom de la source

    Returns:
        True si toutes les validations passent
    """
    from ..config import (
        ANNEES_ELECTIONS_VALIDES,
        TOURS_VALIDES,
    )

    # Colonnes requises
    required = [
        "id_territoire",
        "annee",
        "tour",
        "candidat",
        "nombre_voix",
        "pourcentage_voix",
    ]
    validate_required_columns(df, required, source)

    # Pas de NULL sur clés primaires
    validate_no_nulls(df, ["id_territoire", "annee", "tour", "candidat"], source)

    # Années valides
    validate_year_range(df, "annee", ANNEES_ELECTIONS_VALIDES, source)

    # Tours valides (1 ou 2)
    invalid_tours = df[~df["tour"].isin(TOURS_VALIDES)]
    if not invalid_tours.empty:
        raise ValueError(f"Tours invalides dans {source} : {invalid_tours['tour'].unique()}")

    # Valeurs positives
    validate_positive_values(df, ["nombre_voix"], source, allow_zero=True)

    # Pourcentages valides
    validate_percentage_range(df, ["pourcentage_voix"], source)

    # Clé unique
    validate_unique_key(df, ["id_territoire", "annee", "tour", "candidat"], source)

    return True


def validate_indicateurs_data(df: pd.DataFrame, source: str) -> bool:
    """
    Validation spécifique pour les données d'indicateurs.

    Args:
        df: DataFrame à valider
        source: Nom de la source

    Returns:
        True si toutes les validations passent
    """
    from ..config import ANNEES_INDICATEURS_VALIDES

    # Colonnes requises
    required = [
        "id_territoire",
        "code_type",
        "annee",
        "valeur_numerique",
    ]
    validate_required_columns(df, required, source)

    # Pas de NULL sur clés primaires
    validate_no_nulls(df, ["id_territoire", "code_type", "annee"], source)

    # Années valides
    validate_year_range(df, "annee", ANNEES_INDICATEURS_VALIDES, source)

    # Valeurs positives (allow_zero car criminalité peut être 0)
    validate_positive_values(df, ["valeur_numerique"], source, allow_zero=True)

    # Clé unique
    validate_unique_key(df, ["id_territoire", "code_type", "annee"], source)

    return True
