"""
Script principal d'orchestration de la transformation des données.

Ce module coordonne la transformation de toutes les données brutes
en délégant à des modules spécialisés du package core.

Architecture:
    - config/ : Configuration centralisée (chemins, constantes)
    - utils/ : Fonctions génériques de parsing
    - core/ : Logique métier par source de données
        - elections.py : Transformation des élections présidentielles
        - securite.py : Transformation des données SSMSI

Transformations appliquées:
    - Élections : Filtre pour Bordeaux, agrège par commune, calcule participation
    - Sécurité : Filtre pour Bordeaux (CODGEO_2025 = 33063)

Entrées:
    data/raw/elections/*.csv (4 fichiers)
    data/raw/securite/delinquance_france_2016_2024.csv

Sorties:
    data/processed/elections/resultats_elections_bordeaux.csv
    data/processed/indicateurs/delinquance_bordeaux.csv

Usage:
    python -m src.etl.transform.main

Auteur: @de (Data Engineer)
"""

import logging
import sys

from .config import CODE_COMMUNE, NOM_COMMUNE
from .core import transform_elections, transform_securite

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
    Point d'entrée principal du script de transformation.

    Orchestration:
        1. Transforme les données électorales (4 élections → 1 fichier consolidé)
        2. Transforme les données de sécurité (France → Bordeaux uniquement)
        3. Affiche un résumé des transformations

    Fichiers produits:
        - data/processed/elections/resultats_elections_bordeaux.csv (4 lignes)
        - data/processed/indicateurs/delinquance_bordeaux.csv (~135 lignes)

    Returns:
        True si toutes les transformations ont réussi
        False si au moins une transformation a échoué

    Exit codes:
        0: Succès complet
        1: Échec partiel ou total
        130: Interruption utilisateur (Ctrl+C)

    Note:
        Les données transformées sont prêtes pour l'analyse et le Machine Learning.
        L'orchestration délègue aux modules core pour chaque source.
    """
    logger.info("=" * 80)
    logger.info("TRANSFORMATION - NETTOYAGE DES DONNÉES")
    logger.info("=" * 80)
    logger.info(f"Territoire: {NOM_COMMUNE} ({CODE_COMMUNE})")
    logger.info("=" * 80)

    try:
        # Transformer les élections (4 fichiers → 1 fichier consolidé)
        elections_ok: bool = transform_elections()

        # Transformer la sécurité (France → Bordeaux)
        securite_ok: bool = transform_securite()

        # Résumé global
        logger.info("\n" + "=" * 80)
        logger.info("RÉSUMÉ DE LA TRANSFORMATION")
        logger.info("=" * 80)
        logger.info(f"  Élections: {'✓ OK' if elections_ok else '✗ ÉCHEC'}")
        logger.info(f"  Sécurité: {'✓ OK' if securite_ok else '✗ ÉCHEC'}")
        logger.info("=" * 80)

        if elections_ok and securite_ok:
            logger.info("[SUCCÈS] Toutes les données sont transformées et prêtes pour l'analyse")
            return True
        else:
            logger.warning("[PARTIEL] Certaines données n'ont pas pu être transformées")
            return False

    except KeyboardInterrupt:
        logger.warning("\n[INTERROMPU] Transformation annulée par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n[ERREUR FATALE] {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
