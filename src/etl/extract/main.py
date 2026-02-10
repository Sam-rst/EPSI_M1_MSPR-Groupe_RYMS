"""
Script principal d'orchestration du téléchargement des données.

Ce module coordonne le téléchargement de toutes les données brutes nécessaires
en délégant à des modules spécialisés du package core.

Architecture:
    - config/ : Configuration centralisée (URLs, chemins, constantes)
    - utils/ : Fonctions génériques de téléchargement
    - core/ : Logique métier par source de données
        - elections.py : Téléchargement des élections présidentielles
        - securite.py : Téléchargement des données SSMSI

Données téléchargées:
    - Élections présidentielles 2017 & 2022 (4 fichiers : tours 1 et 2)
    - Données de sécurité SSMSI (France entière, filtrage ultérieur requis)

Sources:
    - data.gouv.fr API (endpoints définis dans config/)
    - Format: CSV (élections) et CSV gzip (sécurité)

Usage:
    python -m src.etl.extract.main

Auteur: @de (Data Engineer)
"""

import logging
import sys

from .core import download_elections, download_securite

# ==============================================================================
# CONFIGURATION DU LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


# ==============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ==============================================================================

def main() -> bool:
    """
    Point d'entrée principal du script de téléchargement.

    Orchestration:
        1. Télécharge les 4 fichiers électoraux (2017 & 2022, tours 1 & 2)
        2. Télécharge le fichier de sécurité SSMSI (France entière)
        3. Affiche un résumé du téléchargement

    Returns:
        True si tous les téléchargements ont réussi
        False si au moins un téléchargement a échoué

    Exit codes:
        0: Succès complet
        1: Échec partiel ou total
        130: Interruption utilisateur (Ctrl+C)

    Note:
        Les fichiers sont sauvegardés dans data/raw/{elections,securite}/
        L'orchestration délègue aux modules core pour chaque source.
    """
    logger.info("=" * 80)
    logger.info("EXTRACTION - TÉLÉCHARGEMENT DES DONNÉES")
    logger.info("=" * 80)
    logger.info("Source: data.gouv.fr (API)")
    logger.info("Territoire: Bordeaux (33063)")
    logger.info("=" * 80)

    try:
        # Télécharger les élections (4 fichiers)
        elections_ok: bool = download_elections()

        # Télécharger la sécurité (1 fichier)
        securite_ok: bool = download_securite()

        # Résumé global
        logger.info("\n" + "=" * 80)
        logger.info("RÉSUMÉ DU TÉLÉCHARGEMENT")
        logger.info("=" * 80)
        logger.info(f"  Élections: {'✓ OK' if elections_ok else '✗ ÉCHEC'}")
        logger.info(f"  Sécurité: {'✓ OK' if securite_ok else '✗ ÉCHEC'}")
        logger.info("=" * 80)

        if elections_ok and securite_ok:
            logger.info("[SUCCÈS] Toutes les données sont téléchargées et prêtes pour la transformation")
            return True
        else:
            logger.warning("[PARTIEL] Certaines données n'ont pas pu être téléchargées")
            return False

    except KeyboardInterrupt:
        logger.warning("\n[INTERROMPU] Téléchargement annulé par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n[ERREUR FATALE] {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
