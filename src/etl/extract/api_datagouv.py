"""
Module d'extraction via API data.gouv.fr.

Architecture validée par @tech :
- Utilisation de l'API REST data.gouv.fr v1
- Récupération des métadonnées des datasets
- Téléchargement des ressources appropriées (niveau bureau de vote)

API Documentation: https://doc.data.gouv.fr/
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from tqdm import tqdm

# === Configuration ===
API_BASE_URL = "https://www.data.gouv.fr/api/1"
STATIC_BASE_URL = "https://static.data.gouv.fr/resources"

# Dataset IDs officiels (validés par @tech)
DATASETS = {
    "2022_T1": "election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour",
    "2022_T2": "election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour",
}

# Configuration logging
sys.stdout = sys.__stdout__  # Reset stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


class DataGouvAPI:
    """
    Client API pour data.gouv.fr.

    Responsabilités :
    - Recherche de datasets
    - Récupération des métadonnées
    - Identification des bonnes ressources (bureaux de vote)
    - Téléchargement des fichiers
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Electio-Analytics-POC/1.0"})

    def get_dataset_info(self, dataset_id: str) -> Optional[Dict]:
        """
        Récupère les métadonnées d'un dataset.

        Args:
            dataset_id: ID ou slug du dataset

        Returns:
            Dictionnaire avec les infos du dataset, None si erreur
        """
        url = f"{API_BASE_URL}/datasets/{dataset_id}/"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API : {e}")
            return None

    def find_resource_by_keywords(
        self, dataset_id: str, keywords: List[str], format_type: str = "txt"
    ) -> Optional[Dict]:
        """
        Trouve une ressource par mots-clés dans le titre.

        Args:
            dataset_id: ID du dataset
            keywords: Liste de mots-clés à chercher (ex: ["subcom", "france-entiere"])
            format_type: Format du fichier (txt, csv, xlsx)

        Returns:
            Dictionnaire de la ressource trouvée, None sinon
        """
        dataset_info = self.get_dataset_info(dataset_id)

        if not dataset_info:
            return None

        resources = dataset_info.get("resources", [])

        # Filtrer par mots-clés et format
        for resource in resources:
            title = resource.get("title", "").lower()
            file_format = resource.get("format", "").lower()

            # Vérifier tous les mots-clés
            if all(keyword.lower() in title for keyword in keywords) and file_format == format_type:
                logger.info(f"Ressource trouvée : {resource.get('title')}")
                logger.info(f"  Format : {resource.get('format')}")
                logger.info(f"  ID : {resource.get('id')}")
                return resource

        logger.warning(f"Aucune ressource trouvée avec keywords={keywords}, format={format_type}")
        return None

    def list_resources(self, dataset_id: str, filter_format: Optional[str] = None):
        """
        Liste toutes les ressources d'un dataset.

        Args:
            dataset_id: ID du dataset
            filter_format: Format à filtrer (optionnel)
        """
        dataset_info = self.get_dataset_info(dataset_id)

        if not dataset_info:
            return

        logger.info(f"\nDataset : {dataset_info.get('title')}")
        logger.info("=" * 80)

        resources = dataset_info.get("resources", [])
        for i, resource in enumerate(resources, 1):
            file_format = resource.get("format", "")

            if filter_format and file_format.lower() != filter_format.lower():
                continue

            logger.info(f"\n{i}. {resource.get('title')}")
            logger.info(f"   Format  : {file_format}")
            logger.info(f"   Taille  : {resource.get('filesize', 'N/A')} octets")
            logger.info(f"   ID      : {resource.get('id')}")

    def download_resource(
        self, resource_url: str, output_path: Path, description: str = ""
    ) -> bool:
        """
        Télécharge une ressource avec barre de progression.

        Args:
            resource_url: URL de la ressource
            output_path: Chemin de destination
            description: Description pour la barre de progression

        Returns:
            True si succès, False sinon
        """
        try:
            logger.info(f"Téléchargement : {description}")
            logger.info(f"URL : {resource_url}")

            # Créer le dossier parent
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Téléchargement avec streaming
            response = self.session.get(resource_url, stream=True, timeout=120)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=description,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            logger.info(f"[OK] Fichier sauvegardé : {output_path}")
            logger.info(f"     Taille : {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            return True

        except Exception as e:
            logger.error(f"[ERREUR] Téléchargement échoué : {e}")
            return False


def main():
    """
    Fonction de test/démonstration de l'API.
    """
    print("=" * 80)
    print("API DATA.GOUV.FR - MODULE DE TEST")
    print("=" * 80)

    api = DataGouvAPI()

    # Test 1 : Lister les ressources 2022 Tour 1
    print("\n### TEST 1 : Ressources présidentielles 2022 - Tour 1 ###")
    api.list_resources(DATASETS["2022_T1"], filter_format="txt")

    # Test 2 : Recherche de la ressource "bureaux de vote"
    print("\n\n### TEST 2 : Recherche ressource bureaux de vote ###")
    resource = api.find_resource_by_keywords(
        DATASETS["2022_T1"],
        keywords=["subcom", "france-entiere"],  # subcom = sub-communal = bureaux de vote
        format_type="txt",
    )

    if resource:
        print(f"\n[OK] Ressource identifiée : {resource.get('title')}")
        print(f"     URL : {resource.get('url')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
