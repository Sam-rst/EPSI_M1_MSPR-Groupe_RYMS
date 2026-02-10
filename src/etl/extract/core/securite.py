"""
Module de téléchargement des données de sécurité.

Ce module gère le téléchargement des données de sécurité SSMSI
(Service Statistique Ministériel de la Sécurité Intérieure).

Données téléchargées:
    - Base statistique communale de la délinquance enregistrée
    - Période: 2016-2024
    - Granularité: Toutes les communes de France
    - Format: CSV gzip compressé

Source:
    SSMSI via data.gouv.fr

Auteur: @de (Data Engineer)
"""

import logging
from pathlib import Path

from ..config import CODE_COMMUNE, DATA_RAW_SECURITE, FICHIER_SECURITE, SECURITE_COMMUNALE_URL
from ..utils import download_file

logger = logging.getLogger(__name__)


def download_securite() -> bool:
    """
    Télécharge les données de sécurité SSMSI (délinquance enregistrée).

    Fichier téléchargé:
        - Base statistique communale de la délinquance enregistrée
        - Période: 2016-2024
        - Granularité: Toutes les communes de France
        - Format: CSV gzip compressé (~34 MB)

    Source:
        Service Statistique Ministériel de la Sécurité Intérieure (SSMSI)
        via data.gouv.fr

    Destination:
        data/raw/securite/delinquance_france_2016_2024.csv

    Returns:
        True si le téléchargement a réussi
        False en cas d'erreur

    Note:
        Le fichier contient TOUTES les communes de France.
        Le filtrage pour Bordeaux (33063) sera effectué lors de la transformation.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TÉLÉCHARGEMENT DONNÉES SÉCURITÉ (SSMSI)")
    logger.info("=" * 80)

    output_path: Path = DATA_RAW_SECURITE / FICHIER_SECURITE
    success: bool = download_file(
        SECURITE_COMMUNALE_URL,
        output_path,
        "Délinquance France (communal)"
    )

    if success:
        logger.info(
            f"\n  Note: Fichier France entière téléchargé. "
            f"Filtrage pour Bordeaux ({CODE_COMMUNE}) nécessaire lors de la transformation."
        )

    return success
