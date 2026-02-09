"""
Script de téléchargement des données d'emploi (INSEE).

Note: Les données INSEE nécessitent souvent un téléchargement manuel
depuis l'interface web. Ce script fournit les instructions et URLs.

Pour les données IRIS au niveau fin, il faut :
1. Télécharger manuellement depuis insee.fr
2. Placer les fichiers dans data/raw/emploi/

Sources :
- Demandeurs d'emploi 2022 - Niveau IRIS
- Dossier complet commune de Bordeaux

Usage:
    python -m src.etl.extract.download_emploi
"""

import logging
import sys

from .config import (
    DATA_RAW_EMPLOI,
    EMPLOI_BORDEAUX_DOSSIER_URL,
    EMPLOI_IRIS_BASE_URL,
    FICHIERS_EMPLOI,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def download_emploi() -> bool:
    """
    Fournit les instructions pour télécharger les données d'emploi.

    Les données INSEE nécessitent un téléchargement manuel.

    Returns:
        True si les fichiers sont présents, False sinon
    """
    logger.info("=" * 70)
    logger.info("DONNÉES D'EMPLOI (INSEE)")
    logger.info("=" * 70)
    logger.info("⚠️ TÉLÉCHARGEMENT MANUEL REQUIS")
    logger.info("=" * 70)

    # Vérifier les fichiers existants
    fichier_iris = DATA_RAW_EMPLOI / FICHIERS_EMPLOI["IRIS"]
    fichier_commune = DATA_RAW_EMPLOI / FICHIERS_EMPLOI["COMMUNE"]

    iris_exists = fichier_iris.exists()
    commune_exists = fichier_commune.exists()

    if iris_exists and commune_exists:
        logger.info("✅ Tous les fichiers d'emploi sont présents :")
        logger.info(f"   - {fichier_iris}")
        logger.info(f"   - {fichier_commune}")
        logger.info("=" * 70)
        return True

    # Instructions de téléchargement
    logger.info("\n📋 INSTRUCTIONS DE TÉLÉCHARGEMENT :\n")

    if not iris_exists:
        logger.info("1️⃣ Données IRIS - Demandeurs d'emploi 2022")
        logger.info(f"   URL : {EMPLOI_IRIS_BASE_URL}")
        logger.info("   Étapes :")
        logger.info("   - Accéder à la page INSEE")
        logger.info("   - Cliquer sur 'Télécharger' ou 'Exporter en CSV/Excel'")
        logger.info(f"   - Enregistrer sous : {fichier_iris}")
        logger.info("   - Colonnes attendues : CODE_IRIS, Taux_chomage, Population_active")
        logger.info("")

    if not commune_exists:
        logger.info("2️⃣ Données Commune - Dossier complet Bordeaux")
        logger.info(f"   URL : {EMPLOI_BORDEAUX_DOSSIER_URL}")
        logger.info("   Étapes :")
        logger.info("   - Accéder au dossier complet commune")
        logger.info("   - Télécharger 'Emploi - Population active'")
        logger.info(f"   - Enregistrer sous : {fichier_commune}")
        logger.info("   - Colonnes attendues : Annee, Trimestre, Taux_chomage, Actifs")
        logger.info("")

    logger.info("=" * 70)
    logger.info("💡 ALTERNATIVE : Utiliser l'API France Travail / DARES")
    logger.info("   URL : https://dares.travail-emploi.gouv.fr/dossier/open-data")
    logger.info("   (Nécessite une clé API)")
    logger.info("=" * 70)

    logger.info(f"\n📁 Dossier de destination : {DATA_RAW_EMPLOI}")

    # Créer le dossier de destination
    DATA_RAW_EMPLOI.mkdir(parents=True, exist_ok=True)

    logger.info("\n⚠️ Une fois les fichiers téléchargés manuellement :")
    logger.info("   Relancer ce script pour valider les téléchargements")
    logger.info("=" * 70)

    return False


def main():
    """Point d'entrée principal du script."""
    try:
        success = download_emploi()

        if not success:
            logger.warning("\n⚠️ Fichiers manquants. Téléchargement manuel requis.")
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\n⚠️ Opération interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Erreur fatale : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
