"""
Script principal d'orchestration de la transformation des données.

Transformations:
    - Géographie : JSON geo.api.gouv.fr → CSV normalisés
    - Élections : JSON participation + Parquet candidats → CSV agrégés
    - Sécurité : CSV SSMSI France → CSV Bordeaux

Usage:
    python -m src.etl.transform.main

Auteur: @de (Data Engineer)
"""

import logging
import sys

from .config import CODE_COMMUNE, NOM_COMMUNE
from .core import transform_geographie, transform_elections, transform_securite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> bool:
    """
    Point d'entrée principal du script de transformation.

    Orchestration:
        1. Transforme la hiérarchie géographique
        2. Transforme les données électorales (participation + candidats)
        3. Transforme les données de sécurité

    Returns:
        True si toutes les transformations ont réussi
    """
    logger.info("=" * 80)
    logger.info("TRANSFORMATION - NETTOYAGE DES DONNÉES (v3.0)")
    logger.info("=" * 80)
    logger.info(f"Territoire: Gironde (33) - {NOM_COMMUNE} ({CODE_COMMUNE})")
    logger.info("=" * 80)

    try:
        # 1. Géographie
        geographie_ok: bool = transform_geographie()

        # 2. Élections
        elections_ok: bool = transform_elections()

        # 3. Sécurité
        securite_ok: bool = transform_securite()

        # Résumé
        logger.info("\n" + "=" * 80)
        logger.info("RÉSUMÉ DE LA TRANSFORMATION")
        logger.info("=" * 80)
        logger.info(f"  Géographie: {'OK' if geographie_ok else 'ECHEC'}")
        logger.info(f"  Élections:  {'OK' if elections_ok else 'ECHEC'}")
        logger.info(f"  Sécurité:   {'OK' if securite_ok else 'ECHEC'}")
        logger.info("=" * 80)

        if geographie_ok and elections_ok and securite_ok:
            logger.info("[SUCCES] Toutes les données sont transformées")
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
