"""
Script principal d'orchestration du téléchargement des données.

Données téléchargées:
    - Géographie : Hiérarchie géographique (geo.api.gouv.fr)
    - Élections : Participation + candidats + nuances (data.gouv.fr)
    - Sécurité : Délinquance SSMSI (data.gouv.fr)

Usage:
    python -m src.etl.extract.main

Auteur: @de (Data Engineer)
"""

import logging
import sys

from .core import download_geographie, download_elections, download_securite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> bool:
    """
    Point d'entrée principal du script de téléchargement.

    Orchestration:
        1. Télécharge la hiérarchie géographique (régions, département, communes)
        2. Télécharge les données électorales (participation + candidats + nuances)
        3. Télécharge le fichier de sécurité SSMSI (France entière)

    Returns:
        True si tous les téléchargements ont réussi
    """
    logger.info("=" * 80)
    logger.info("EXTRACTION - TÉLÉCHARGEMENT DES DONNÉES (v3.0)")
    logger.info("=" * 80)
    logger.info("Sources: geo.api.gouv.fr, data.gouv.fr (API tabulaire + Parquet)")
    logger.info("Territoire: Gironde (33)")
    logger.info("=" * 80)

    try:
        # 1. Géographie
        geographie_ok: bool = download_geographie()

        # 2. Élections (API tabulaire + Parquet + CSV nuances)
        elections_ok: bool = download_elections()

        # 3. Sécurité (CSV gzip)
        securite_ok: bool = download_securite()

        # Résumé global
        logger.info("\n" + "=" * 80)
        logger.info("RÉSUMÉ DU TÉLÉCHARGEMENT")
        logger.info("=" * 80)
        logger.info(f"  Géographie: {'OK' if geographie_ok else 'ECHEC'}")
        logger.info(f"  Élections:  {'OK' if elections_ok else 'ECHEC'}")
        logger.info(f"  Sécurité:   {'OK' if securite_ok else 'ECHEC'}")
        logger.info("=" * 80)

        if geographie_ok and elections_ok and securite_ok:
            logger.info("[SUCCES] Toutes les données sont téléchargées")
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
