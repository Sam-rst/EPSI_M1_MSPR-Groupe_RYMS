"""
Package de configuration pour la transformation de données.

Expose toutes les constantes de configuration nécessaires à la transformation.

Auteur: @de (Data Engineer)
"""

from .settings import (
    CODE_COMMUNE,
    CODE_DEPARTEMENT,
    DATA_PROCESSED,
    DATA_PROCESSED_ELECTIONS,
    DATA_PROCESSED_INDICATEURS,
    DATA_RAW,
    DATA_RAW_ELECTIONS,
    DATA_RAW_SECURITE,
    FICHIER_SECURITE,
    FICHIERS_ELECTIONS,
    NOM_COMMUNE,
    PROJECT_ROOT,
)

__all__ = [
    # Chemins
    "PROJECT_ROOT",
    "DATA_RAW",
    "DATA_PROCESSED",
    "DATA_RAW_ELECTIONS",
    "DATA_RAW_SECURITE",
    "DATA_PROCESSED_ELECTIONS",
    "DATA_PROCESSED_INDICATEURS",
    # Géographie
    "CODE_DEPARTEMENT",
    "CODE_COMMUNE",
    "NOM_COMMUNE",
    # Fichiers
    "FICHIERS_ELECTIONS",
    "FICHIER_SECURITE",
]
