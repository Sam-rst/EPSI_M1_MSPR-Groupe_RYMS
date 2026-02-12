"""
Module de téléchargement de la hiérarchie géographique.

Télécharge les données via geo.api.gouv.fr :
    - Régions françaises
    - Département Gironde (33)
    - Communes de la Gironde

Source: geo.api.gouv.fr (API REST JSON)

Auteur: @de (Data Engineer)
"""

import json
import logging
from pathlib import Path

import requests

from ..config import (
    CODE_DEPARTEMENT,
    DATA_RAW_GEOGRAPHIE,
    FICHIERS_GEOGRAPHIE,
    GEO_COMMUNES_URL,
    GEO_DEPARTEMENT_URL,
    GEO_REGIONS_URL,
)

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS: int = 60


def _download_json(url: str, output_path: Path, description: str, params: dict = None) -> bool:
    """Télécharge un endpoint JSON et sauvegarde en fichier."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            logger.info(f"  [EXISTE] {output_path.name}")
            return True

        logger.info(f"  Téléchargement: {description}")
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        data = response.json()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"  [OK] {output_path.name} ({len(data) if isinstance(data, list) else 1} éléments)")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"  [ERREUR] Téléchargement échoué: {e}")
        return False
    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False


def download_geographie() -> bool:
    """
    Télécharge la hiérarchie géographique via geo.api.gouv.fr.

    Fichiers téléchargés:
        - regions.json : Toutes les régions françaises
        - departement_33.json : Département Gironde
        - communes_33.json : Toutes les communes de la Gironde

    Destination:
        data/raw/geographie/

    Returns:
        True si tous les fichiers sont téléchargés avec succès
    """
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT HIÉRARCHIE GÉOGRAPHIQUE")
    logger.info("=" * 80)
    logger.info(f"  Source: geo.api.gouv.fr")
    logger.info(f"  Département: {CODE_DEPARTEMENT} (Gironde)")

    results = []

    # 1. Régions
    logger.info(f"\n[Régions]")
    results.append(_download_json(
        GEO_REGIONS_URL,
        DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["regions"],
        "Régions françaises",
    ))

    # 2. Département 33
    logger.info(f"\n[Département {CODE_DEPARTEMENT}]")
    results.append(_download_json(
        GEO_DEPARTEMENT_URL,
        DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["departement"],
        f"Département {CODE_DEPARTEMENT}",
    ))

    # 3. Communes du département 33
    logger.info(f"\n[Communes du département {CODE_DEPARTEMENT}]")
    results.append(_download_json(
        GEO_COMMUNES_URL,
        DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["communes"],
        f"Communes département {CODE_DEPARTEMENT}",
        params={
            "fields": "nom,code,population,codesPostaux,codeDepartement,codeRegion",
        },
    ))

    # Résumé
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Fichiers géographie téléchargés: {sum(results)}/{len(results)}")
    logger.info("=" * 80)

    return all(results)
