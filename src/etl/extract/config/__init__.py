"""
Package de configuration pour l'extraction de données.

Expose toutes les constantes de configuration nécessaires au téléchargement.

Auteur: @de (Data Engineer)
"""

from .settings import (
    CODE_COMMUNE,
    CODE_DEPARTEMENT,
    CONTOURS_IRIS_URL,
    CORRESPONDANCE_BUREAU_IRIS_URL,
    DATA_PROCESSED,
    DATA_RAW,
    DATA_RAW_ELECTIONS,
    DATA_RAW_EMPLOI,
    DATA_RAW_SECURITE,
    ELECTIONS,
    ELECTIONS_2017_T1_URL,
    ELECTIONS_2017_T2_URL,
    ELECTIONS_2022_T1_URL,
    ELECTIONS_2022_T2_URL,
    EMPLOI_BORDEAUX_DOSSIER_URL,
    EMPLOI_IRIS_BASE_URL,
    FICHIER_SECURITE,
    FICHIERS_ELECTIONS,
    FICHIERS_EMPLOI,
    NOM_COMMUNE,
    PROJECT_ROOT,
    SECURITE_COMMUNALE_URL,
)

__all__ = [
    # Chemins
    "PROJECT_ROOT",
    "DATA_RAW",
    "DATA_PROCESSED",
    "DATA_RAW_ELECTIONS",
    "DATA_RAW_SECURITE",
    "DATA_RAW_EMPLOI",
    # Géographie
    "CODE_DEPARTEMENT",
    "CODE_COMMUNE",
    "NOM_COMMUNE",
    # URLs Élections
    "ELECTIONS_2017_T1_URL",
    "ELECTIONS_2017_T2_URL",
    "ELECTIONS_2022_T1_URL",
    "ELECTIONS_2022_T2_URL",
    "ELECTIONS",
    # URLs Sécurité
    "SECURITE_COMMUNALE_URL",
    # URLs Emploi
    "EMPLOI_IRIS_BASE_URL",
    "EMPLOI_BORDEAUX_DOSSIER_URL",
    # URLs Référentiels
    "CORRESPONDANCE_BUREAU_IRIS_URL",
    "CONTOURS_IRIS_URL",
    # Fichiers
    "FICHIERS_ELECTIONS",
    "FICHIER_SECURITE",
    "FICHIERS_EMPLOI",
]
