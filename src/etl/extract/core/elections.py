"""
Module de téléchargement des données électorales.

Ce module gère le téléchargement des fichiers des élections présidentielles
depuis data.gouv.fr.

Données téléchargées:
    - Présidentielles 2017 - Tour 1 (23 avril 2017)
    - Présidentielles 2017 - Tour 2 (7 mai 2017)
    - Présidentielles 2022 - Tour 1 (10 avril 2022)
    - Présidentielles 2022 - Tour 2 (24 avril 2022)

Source:
    Ministère de l'Intérieur via data.gouv.fr
    Granularité: Bureau de vote (niveau le plus fin)

Auteur: @de (Data Engineer)
"""

import logging
from pathlib import Path
from typing import List, Tuple

from ..config import DATA_RAW_ELECTIONS, ELECTIONS
from ..utils import download_file

logger = logging.getLogger(__name__)


def download_elections() -> bool:
    """
    Télécharge les 4 fichiers des élections présidentielles (2017 & 2022, tours 1 & 2).

    Fichiers téléchargés:
        - Présidentielles 2017 - Tour 1 (23 avril 2017)
        - Présidentielles 2017 - Tour 2 (7 mai 2017)
        - Présidentielles 2022 - Tour 1 (10 avril 2022)
        - Présidentielles 2022 - Tour 2 (24 avril 2022)

    Source:
        Ministère de l'Intérieur via data.gouv.fr
        Granularité: Bureau de vote (niveau le plus fin)

    Destination:
        data/raw/elections/*.csv

    Returns:
        True si tous les 4 fichiers sont téléchargés avec succès
        False si au moins un téléchargement a échoué

    Note:
        Les fichiers existants sont automatiquement détectés et non retéléchargés
    """
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT DONNÉES ÉLECTORALES")
    logger.info("=" * 80)

    elections: List[Tuple[str, str, str]] = ELECTIONS
    results: List[bool] = []

    for url, filename, description in elections:
        logger.info(f"\n[{description}]")
        output_path: Path = DATA_RAW_ELECTIONS / filename
        success: bool = download_file(url, output_path, description)
        results.append(success)

    # Résumé du téléchargement
    logger.info("\n" + "=" * 80)
    logger.info(f"Fichiers téléchargés: {sum(results)}/{len(results)}")
    logger.info("=" * 80)

    return all(results)
