"""
Script de téléchargement des données électorales via API data.gouv.fr.

Télécharge automatiquement les 4 fichiers CSV des présidentielles :
- 2017 Tour 1 (23 avril) - 34 MB - Bureaux de vote
- 2017 Tour 2 (7 mai) - 13 MB - Bureaux de vote
- 2022 Tour 1 (10 avril) - 17 MB - Communes
- 2022 Tour 2 (24 avril) - 6 MB - Communes

Architecture validée par @tech :
- Utilisation de l'API REST data.gouv.fr
- Identification automatique des ressources via mots-clés
- Téléchargement robuste avec barres de progression

Usage:
    python -m src.etl.extract.download_elections
    # ou via CLI : uv run electio-download
"""

import logging
import sys
from typing import Dict

from .api_datagouv import DataGouvAPI
from .config import DATA_RAW_ELECTIONS, FICHIERS_ELECTIONS

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


# Configuration des datasets
ELECTIONS_CONFIG = [
    # === 2017 - Ministère Intérieur (datasets officiels) ===
    {
        "dataset_id": "5901a718c751df3f49b29ff8",
        "keywords": [],  # Pas besoin, 1 seule ressource
        "format": "txt",
        "output_file": FICHIERS_ELECTIONS["2017_T1"],
        "description": "Présidentielles 2017 - 1er tour (23 avril 2017)",
        "use_first_resource": True,  # Prendre la première ressource
    },
    {
        "dataset_id": "5914141088ee386741d8d6f1",
        "keywords": [],
        "format": "txt",
        "output_file": FICHIERS_ELECTIONS["2017_T2"],
        "description": "Présidentielles 2017 - 2nd tour (7 mai 2017)",
        "use_first_resource": True,
    },
    # === 2022 - Ministère Intérieur (structure moderne) ===
    {
        "dataset_id": "election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour",
        "keywords": ["subcom", "france-entiere"],
        "format": "txt",
        "output_file": FICHIERS_ELECTIONS["2022_T1"],
        "description": "Présidentielles 2022 - 1er tour (10 avril 2022)",
        "use_first_resource": False,
    },
    {
        "dataset_id": "election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour",
        "keywords": ["subcom", "france-entiere"],
        "format": "txt",
        "output_file": FICHIERS_ELECTIONS["2022_T2"],
        "description": "Présidentielles 2022 - 2nd tour (24 avril 2022)",
        "use_first_resource": False,
    },
]


def download_all_elections_api() -> Dict[str, bool]:
    """
    Télécharge toutes les données électorales via l'API.

    Returns:
        Dictionnaire avec le statut de chaque téléchargement
    """
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT DES DONNÉES ÉLECTORALES - VIA API")
    logger.info("=" * 80)
    logger.info("Source : Ministère de l'Intérieur via data.gouv.fr")
    logger.info("Niveau : Bureaux de vote (tous les bureaux de France)")
    logger.info("=" * 80)

    api = DataGouvAPI()
    results = {}

    # Téléchargement automatique (2017 + 2022)
    logger.info("\n### TÉLÉCHARGEMENT AUTOMATIQUE ###\n")

    for i, config in enumerate(ELECTIONS_CONFIG, 1):
        logger.info(f"[{i}/{len(ELECTIONS_CONFIG)}] {config['description']}")

        output_path = DATA_RAW_ELECTIONS / config["output_file"]

        # Vérifier si déjà téléchargé
        if output_path.exists():
            logger.warning(f"  >> Fichier existant, ignoré : {output_path.name}")
            results[config["output_file"]] = True
            continue

        # Stratégie de recherche de ressource
        resource = None

        if config.get("use_first_resource", False):
            # Pour 2017 : prendre la première ressource (unique)
            dataset_info = api.get_dataset_info(config["dataset_id"])
            if dataset_info and dataset_info.get("resources"):
                resource = dataset_info["resources"][0]
                logger.info(f"  >> Ressource unique trouvée : {resource.get('title')}")
        else:
            # Pour 2022 : recherche par mots-clés
            resource = api.find_resource_by_keywords(
                config["dataset_id"], config["keywords"], config["format"]
            )

        if not resource:
            logger.error("  >> [ERREUR] Ressource introuvable")
            results[config["output_file"]] = False
            continue

        # Télécharger
        success = api.download_resource(
            resource["url"], output_path, config["description"]
        )
        results[config["output_file"]] = success
        logger.info("")

    # Résumé
    logger.info("=" * 80)
    logger.info("RÉSUMÉ DU TÉLÉCHARGEMENT")
    logger.info("=" * 80)

    success_count = sum(results.values())
    total_count = len(results)

    for filename, success in results.items():
        status = "[OK]" if success else "[MANQUANT]"
        logger.info(f"{status:12} {filename}")

    logger.info("=" * 80)
    logger.info(f"Fichiers disponibles : {success_count}/{total_count}")

    if success_count == total_count:
        logger.info("[SUCCÈS] Tous les fichiers sont disponibles")
    elif success_count >= 2:
        logger.warning(f"[PARTIEL] {total_count - success_count} fichier(s) manquant(s)")
    else:
        logger.error(f"[ÉCHEC] Trop de fichiers manquants ({total_count - success_count})")

    logger.info(f"\nDossier : {DATA_RAW_ELECTIONS}")
    logger.info("=" * 80)

    return results


def main():
    """Point d'entrée principal."""
    try:
        results = download_all_elections_api()

        # Code de sortie : 0 si au moins 2 fichiers, 1 sinon
        if sum(results.values()) >= 2:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n[INTERROMPU] Téléchargement annulé par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[ERREUR FATALE] {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
