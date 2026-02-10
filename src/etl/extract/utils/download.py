"""
Utilitaires de téléchargement pour l'extraction de données.

Ce module contient les fonctions génériques réutilisables pour
le téléchargement de fichiers depuis des URLs.

Fonctionnalités:
    - Téléchargement avec barre de progression
    - Gestion automatique des dossiers
    - Détection de fichiers existants
    - Gestion robuste des erreurs réseau

Auteur: @de (Data Engineer)
"""

import logging
from pathlib import Path

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

# ==============================================================================
# CONSTANTES DE TÉLÉCHARGEMENT
# ==============================================================================

TIMEOUT_SECONDS: int = 300          # Timeout réseau (5 minutes)
CHUNK_SIZE_BYTES: int = 8192        # Taille des chunks de téléchargement (8 KB)
PROGRESS_BAR_WIDTH: int = 80        # Largeur de la barre de progression


def download_file(url: str, output_path: Path, description: str) -> bool:
    """
    Télécharge un fichier depuis une URL avec barre de progression et gestion d'erreurs.

    Cette fonction gère:
        - Création automatique des dossiers parents
        - Détection de fichiers existants (skip si déjà présent)
        - Téléchargement en streaming avec chunks pour économiser la mémoire
        - Affichage d'une barre de progression tqdm
        - Logging détaillé de chaque étape

    Args:
        url: URL complète du fichier à télécharger (API data.gouv.fr)
        output_path: Chemin absolu de destination (Path object)
        description: Label descriptif pour les logs et la barre de progression

    Returns:
        True si le téléchargement a réussi ou si le fichier existe déjà
        False en cas d'erreur réseau ou d'écriture fichier

    Raises:
        Aucune exception n'est propagée (toutes sont capturées et loggées)

    Example:
        >>> from pathlib import Path
        >>> url = "https://data.gouv.fr/api/1/datasets/r/abc123"
        >>> path = Path("data/raw/elections/file.csv")
        >>> success = download_file(url, path, "Présidentielles 2022 - Tour 1")
    """
    try:
        # Créer le dossier parent si nécessaire
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Vérifier si le fichier existe déjà (évite les téléchargements redondants)
        if output_path.exists():
            logger.info(f"  [EXISTE] {output_path.name}")
            return True

        logger.info(f"  Téléchargement: {description}")
        logger.info(f"  URL: {url}")

        # Télécharger en streaming avec timeout
        response = requests.get(url, stream=True, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        # Récupérer la taille totale du fichier (pour la barre de progression)
        total_size: int = int(response.headers.get('content-length', 0))

        # Écrire le fichier par chunks avec barre de progression
        with open(output_path, 'wb') as f:
            with tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=description,
                ncols=PROGRESS_BAR_WIDTH
            ) as pbar:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE_BYTES):
                    if chunk:  # Filtrer les keep-alive chunks vides
                        f.write(chunk)
                        pbar.update(len(chunk))

        # Confirmation avec taille du fichier
        file_size_mb: float = output_path.stat().st_size / 1024 / 1024
        logger.info(f"  [OK] {output_path.name} ({file_size_mb:.2f} MB)")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"  [ERREUR] Téléchargement échoué: {e}")
        return False
    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
